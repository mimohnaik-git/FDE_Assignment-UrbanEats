"""Credential-free Docker/n8n outage checks; stops only the API and restores it in finally.

No model changes or external notification/provider calls. Disposable n8n state is isolated
from n8n_data. Run from repository root with Docker Desktop available.
"""
import hashlib
import json
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from current_demo import demo_batch

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "docker.n8n.io/n8nio/n8n@sha256:87e0bab2c93192e8dd885ff7b0697c22a1bd97489568a8c67cc140fd7dbb342d"
N8N_TEST = "urbaneats-phase3b-n8n-check"
FIXTURE_TEST = "urbaneats-phase3b-fixtures"

MOCK_SERVER = r'''
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json,time
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  if self.path=="/timeout":time.sleep(2)
  status=500 if self.path=="/500" else 503 if self.path in {"/503","/poison"} else 200
  self.send_response(status);self.send_header("Content-Type","application/json");self.end_headers()
  body=b"<html>not model evidence</html>" if self.path=="/malformed" else json.dumps({
    "run_id":"UE-"+"b"*32,"routing_status":"RED_ALERT","model_version":"PRIOR-MODEL",
    "records_scored":999,"evidence":{"routing_status":"RED_ALERT","facts":[{"evidence_id":"PRIOR-HOTSPOT"}]},
    "briefing":{"text":"PRIOR RED MODEL BRIEF"}}).encode()
  try:self.wfile.write(body)
  except BrokenPipeError:pass
 def log_message(self,*args):pass
ThreadingHTTPServer(("0.0.0.0",8720),Handler).serve_forever()
'''

SUMMARY = r'''
const fs=require('fs');const t=fs.readFileSync('/tmp/ue3b-execution.log','utf8');
const start=t.indexOf('Execution was successful:');if(start<0)throw Error('Native workflow failed');
const result=JSON.parse(t.slice(t.indexOf('{',start)));const nodes=result.data.resultData.runData;
const response=nodes['Normalize Response'].at(-1).data.main[0][0].json;
const row=nodes['Persist Completed Audit'].at(-1).data.main[0][0].json;
const stored=JSON.parse(row.evidence_json);const evidence=stored.evidence;
if(!row.started_at||!row.completed_at)throw Error('Incomplete persistent audit');
if(response.evidence_origin==='orchestration'){
 if(evidence.routing_status!=='DATA_FAILURE'||['model_version','records_scored','facts','evidence_id'].some(k=>k in evidence))
  throw Error('Fabricated model evidence');
 if(JSON.stringify(evidence).includes('PRIOR-'))throw Error('Prior execution evidence leaked');
 if(!evidence.notification_required||evidence.attempts.length!==nodes['Call UrbanEats API'].length)
  throw Error('Incomplete outage evidence');
}
if(row.test_mode){
 if(row.slack_attempts||row.gmail_attempts||nodes.Slack||nodes.Gmail)throw Error('Real sends attempted in TEST_MODE');
}
console.log(JSON.stringify({status:result.status,evidence_origin:response.evidence_origin,
 routing_status:response.routing_status,attempt_count:nodes['Call UrbanEats API'].length,
 failure_category:response.failure_category,slack:row.slack_delivery_state,gmail:row.gmail_delivery_state,
 slack_attempts:row.slack_attempts,gmail_attempts:row.gmail_attempts,
 duplicate_suppression:row.duplicate_suppression}));
'''



def docker(*args, check=True):
    result = subprocess.run(["docker", *args], text=True, capture_output=True)
    if check and result.returncode:
        # Never echo native execution/provider/configuration output on errors.
        raise RuntimeError("Docker verification command failed: " + args[0])
    return result.stdout.strip()


def health():
    with urlopen("http://127.0.0.1:8000/health", timeout=5) as response:
        result = json.load(response)
    assert result["model_loaded"] and result["threshold_loaded"]
    return result


def main():
    directory = ROOT / "docker/local/phase3b"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "mock_transport.py").write_text(MOCK_SERVER, encoding="utf-8")
    (directory / "summarize.cjs").write_text(SUMMARY, encoding="utf-8")
    # n8n execute omits backend modules; initialize the same native modules as
    # n8n start, exclusively inside the disposable container (no mocked storage).
    (directory / "initialize_cli.cjs").write_text(
        "const fs=require('fs');const p='/usr/local/lib/node_modules/n8n/dist/commands/execute.js';"
        "let s=fs.readFileSync(p,'utf8');s=s.replace('await this.initExternalHooks();',"
        "'await this.initExternalHooks(); await this.moduleRegistry.initModules(this.instanceSettings.instanceType);');"
        "fs.writeFileSync(p,s);", encoding="utf-8")
    public = json.loads((ROOT / "workflows/n8n/urbaneats_live.json").read_text())
    assert len(public["nodes"]) == 22 and not public["active"]
    # CLI import requires a workflow ID; UI Import from File assigns one for a
    # new workflow. Keep the public template free of instance identity.
    (directory / "public.json").write_text(
        json.dumps({**public, "id": "ue3b-public-template"}), encoding="utf-8")
    cases = [
        ("healthy", "http://urbaneats-api:8000/process-current", None),
        ("green", "http://urbaneats-api:8000/process-current", None),
        ("data_failure", "http://urbaneats-api:8000/process-current", None),
        # Docker removes stopped container aliases from its DNS on this host.
        ("stopped_api", "http://urbaneats-api:8000/process-current",
         ("CONNECTION_REFUSED", "DNS_SERVICE_FAILURE")),
        ("refused", "http://urbaneats-api:1/process-current", "CONNECTION_REFUSED"),
        ("dns", "http://urbaneats-missing:8000/process-current", "DNS_SERVICE_FAILURE"),
        ("timeout", "http://urbaneats-phase3b-fixtures:8720/timeout", "TIMEOUT"),
        ("http500", "http://urbaneats-phase3b-fixtures:8720/500", "HTTP_5XX"),
        ("http503", "http://urbaneats-phase3b-fixtures:8720/503", "HTTP_5XX"),
        ("malformed", "http://urbaneats-phase3b-fixtures:8720/malformed", "MALFORMED_RESPONSE"),
        ("prior_red_body", "http://urbaneats-phase3b-fixtures:8720/poison", "HTTP_5XX"),
        ("recovery", "http://urbaneats-api:8000/process-current", None),
        ("mock_retry", "http://urbaneats-api:8000/process-current", None),
        ("mock_unknown", "http://urbaneats-api:8000/process-current", None),
    ]
    for name, url, _ in cases:
        workflow = json.loads(json.dumps(public))
        workflow["id"] = "ue3b-test-" + name
        for node in workflow["nodes"]:
            if node["name"] == "Settings":
                source = node["parameters"]["jsCode"]
                source = source.replace("orchestration_run_id_override:''", "orchestration_run_id_override:'ORCH-3b-" + name + "'")
                if name.startswith("mock_"):
                    source = source.replace("test_mode:true", "test_mode:false")
                node["parameters"]["jsCode"] = source
            if node["name"] in {"Slack", "Gmail"} and name.startswith("mock_"):
                channel = node["name"]
                if name == "mock_unknown":
                    receipt = "{error:'ambiguous timeout'}"
                elif channel == "Slack":
                    receipt = "$runIndex<2 ? {ok:false,error:'ratelimited'} : {ok:true,ts:'mock-receipt'}"
                else:
                    receipt = "$runIndex<1 ? {statusCode:429} : {id:'mock-receipt'}"
                node.update(type="n8n-nodes-base.code", typeVersion=2, disabled=False,
                            parameters={"jsCode": "return [{json:" + receipt + "}];"})
            if node["name"] == "Call UrbanEats API":
                node["parameters"]["url"] = url
                node["parameters"]["options"]["timeout"] = 200 if name == "timeout" else 5000
                if name in {"healthy", "green", "data_failure", "recovery", "mock_retry", "mock_unknown"}:
                    # Exercise the identical API pipeline with isolated request fixtures;
                    # verification must not rewrite the user's mounted current source.
                    payload = {} if name == "data_failure" else demo_batch(4 if name == "green" else 24)
                    node["parameters"].update(url="http://urbaneats-api:8000/process-batch",
                        sendBody=True, specifyBody="json", jsonBody=json.dumps(payload))
            if node["name"] in {"API Retry Delay", "Delivery Retry Delay"}:
                node["parameters"]["amount"] = 0.1
        (directory / (name + ".json")).write_text(json.dumps(workflow), encoding="utf-8")
    report = {"phase": "3B.1", "real_notifications": 0, "hosted_llm_calls": 0, "cases": []}
    stopped = False
    try:
        report["initial_health"] = health()
        mount = f"type=bind,source={directory},target=/verify,readonly"
        docker("run", "-d", "--rm", "--name", N8N_TEST, "--network", "urbaneats_private",
               "--entrypoint", "/bin/sh", "-e", "N8N_DIAGNOSTICS_ENABLED=false",
               "-e", "N8N_GRACEFUL_SHUTDOWN_TIMEOUT=1",
               "-e", "N8N_VERSION_NOTIFICATIONS_ENABLED=false", "-e", "N8N_TEMPLATES_ENABLED=false",
               "--mount", mount, IMAGE, "-c", "while :; do sleep 60; done")
        docker("exec", "-u", "root", N8N_TEST, "node", "/verify/initialize_cli.cjs")
        docker("exec", N8N_TEST, "/bin/sh", "-c",
               "n8n import:workflow --input=/verify/public.json >/tmp/ue3b-public-import.log 2>&1")
        report["public_workflow_import"] = "PASS"
        report["public_workflow_sha256"] = hashlib.sha256(
            (ROOT / "workflows/n8n/urbaneats_live.json").read_bytes()).hexdigest()
        docker("run", "-d", "--rm", "--name", FIXTURE_TEST, "--network", "urbaneats_private",
               "--entrypoint", "python", "--mount", mount, "urbaneats-urbaneats-api",
               "/verify/mock_transport.py")
        for name, _, category in cases:
            if name == "stopped_api":
                docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                       "stop", "urbaneats-api")
                stopped = True
            if name == "refused":
                docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                       "start", "urbaneats-api")
                stopped = False
                for _ in range(15):
                    try:
                        health()
                        break
                    except Exception:
                        time.sleep(1)
                else:
                    raise RuntimeError("API recovery health failed")
            docker("exec", N8N_TEST, "/bin/sh", "-c",
                   f"n8n import:workflow --input=/verify/{name}.json >/tmp/ue3b-import.log 2>&1")
            def execute():
                docker("exec", N8N_TEST, "/bin/sh", "-c",
                       f"n8n execute --id=ue3b-test-{name} >/tmp/ue3b-execution.log 2>&1")
                return json.loads(docker("exec", N8N_TEST, "node", "/verify/summarize.cjs"))
            result = execute()
            if category:
                assert result["evidence_origin"] == "orchestration", result
                assert result["routing_status"] == "DATA_FAILURE", result
                expected = category if isinstance(category, tuple) else (category,)
                assert result["failure_category"] in expected, result
                assert result["attempt_count"] == 3, result
                assert result["slack"] == result["gmail"] == "SKIPPED_TEST_MODE", result
            else:
                assert result["evidence_origin"] == "api", result
                expected_route = "GREEN_SUMMARY" if name == "green" else "DATA_FAILURE" if name == "data_failure" else "RED_ALERT"
                assert result["routing_status"] == expected_route, result
            if name == "mock_retry":
                assert result["slack"] == result["gmail"] == "SUCCESS", result
                assert result["slack_attempts"] == 3 and result["gmail_attempts"] == 2, result
            elif name == "mock_unknown":
                assert result["slack"] == result["gmail"] == "UNKNOWN", result
                assert result["slack_attempts"] == result["gmail_attempts"] == 1, result
            report["cases"].append({"name": name, **result})
            print(json.dumps({"name": name, **result}), flush=True)
            if name in {"stopped_api", "healthy", "mock_retry"}:
                repeat = execute()
                assert repeat["duplicate_suppression"], repeat
                assert repeat["slack"] == repeat["gmail"] == "DUPLICATE_SUPPRESSED", repeat
                report["cases"].append({"name": "duplicate_" + name, **repeat})
                print(json.dumps({"name": "duplicate_" + name, **repeat}), flush=True)
        report["recovered_health"] = health()
        report["result"] = "PASS"
    except Exception:
        docker("cp", N8N_TEST + ":/tmp/ue3b-execution.log", str(directory / "native_failure.log"),
               check=False)
        raise
    finally:
        if stopped:
            docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                   "start", "urbaneats-api", check=False)
        docker("stop", N8N_TEST, check=False)
        docker("stop", FIXTURE_TEST, check=False)
        (ROOT / "evaluation/results/phase3b1_native_verification.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
