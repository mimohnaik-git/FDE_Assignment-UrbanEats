"""Credential-free Docker/n8n outage checks; stops only the API and restores it in finally.

No model changes or external notification/provider calls. Disposable n8n state is isolated
from n8n_data. Run from repository root with Docker Desktop available.
"""
import argparse
import hashlib
import json
import re
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
if(row.routing_status==='GREEN_SUMMARY' && (nodes.Slack||row.slack_attempts||row.slack_delivery_state!=='SKIPPED_POLICY'))throw Error('Green Slack policy violation');
if(row.test_mode){
 if(row.slack_attempts||row.gmail_attempts||nodes.Slack||nodes.Gmail)throw Error('Real sends attempted in TEST_MODE');
}
console.log(JSON.stringify({status:result.status,evidence_origin:response.evidence_origin,
 routing_status:response.routing_status,attempt_count:nodes['Call UrbanEats API'].length,
 failure_category:response.failure_category,slack:row.slack_delivery_state,gmail:row.gmail_delivery_state,
 slack_attempts:row.slack_attempts,gmail_attempts:row.gmail_attempts,
 duplicate_suppression:row.duplicate_suppression,event_type:row.event_type}));
'''



CLI_TIMEOUT = 120


class DockerCommandError(RuntimeError):
    def __init__(self, operation, result):
        super().__init__("Docker verification command failed: " + operation)
        self.returncode = result.returncode
        self.stderr = result.stderr


def docker(*args, check=True, timeout=30):
    result = subprocess.run(["docker", *args], text=True, capture_output=True, timeout=timeout)
    if check and result.returncode:
        # Never echo native execution/provider/configuration output on errors.
        raise DockerCommandError(args[0], result)
    return result.stdout.strip()


def stage(report, name, state="started"):
    report["current_stage"] = name
    report.setdefault("stages", []).append({"stage": name, "state": state,
                                            "elapsed_seconds": round(time.monotonic() - report["started_monotonic"], 3)})
    print(json.dumps({"stage": name, "state": state}), flush=True)


def import_diagnostic(directory, label, retain=False):
    # Never publish raw logs: n8n may log configuration or workflow content.
    raw = docker("exec", N8N_TEST, "cat", f"/tmp/ue3b-{label}-import.log")
    if retain:
        # Private, gitignored local diagnostics only; never emit or publish raw logs.
        (directory / (label + "_import_private.log")).write_text(raw, encoding="utf-8")
    markers = []
    for line in raw.splitlines():
        if re.fullmatch(r"Successfully imported \d+ workflows?\.", line):
            markers.append(line)
        elif line.startswith("Starting migration "):
            markers.append("database migration started")
        elif line.startswith("Finished migration "):
            markers.append("database migration completed")
        elif re.fullmatch(r"Importing \d+ workflows\.\.\.", line):
            markers.append(line)
        elif line == "An error occurred while importing workflows. See log messages for details.":
            markers.append("import error reported")
    diagnostic = {"markers": markers, "log_bytes": len(raw.encode()),
                  "log_sha256": hashlib.sha256(raw.encode()).hexdigest()}
    path = directory / (label + "_import_diagnostic.json")
    path.write_text(json.dumps(diagnostic, indent=2), encoding="utf-8")
    return diagnostic


def import_workflow(report, directory, name):
    stage(report, name + " workflow import")
    report.pop("import_diagnostic", None)
    try:
        docker("exec", N8N_TEST, "/bin/sh", "-c",
               f"n8n import:workflow --input=/verify/{name}.json >/tmp/ue3b-{name}-import.log 2>&1",
               timeout=CLI_TIMEOUT)
    except (subprocess.TimeoutExpired, RuntimeError, KeyboardInterrupt) as error:
        if isinstance(error, DockerCommandError):
            report["docker_exit_code"] = error.returncode
            (directory / (name + "_docker_private.log")).write_text(error.stderr, encoding="utf-8")
        try:
            report["import_diagnostic"] = import_diagnostic(directory, name, retain=True)
        except Exception:
            report["import_diagnostic"] = {"markers": [], "capture": "FAILED"}
        raise
    diagnostic = import_diagnostic(directory, name)
    report["import_diagnostic"] = diagnostic
    report.setdefault("imports", {})[name] = diagnostic
    # This CLI catches import errors itself, so exit zero alone is insufficient.
    if "Successfully imported 1 workflow." not in diagnostic["markers"]:
        import_diagnostic(directory, name, retain=True)
        raise RuntimeError("IMPORT_FAILED")
    stage(report, name + " workflow import", "completed")


def health():
    with urlopen("http://127.0.0.1:8000/health", timeout=5) as response:
        result = json.load(response)
    assert result["model_loaded"] and result["threshold_loaded"]
    assert result["status"] == "READY"
    return result


def prepare():
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
    assert len(public["nodes"]) == 23 and not public["active"]
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
         ("CONNECTION_REFUSED", "DNS_SERVICE_FAILURE", "TIMEOUT")),
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
        ("mock_green", "http://urbaneats-api:8000/process-current", None),
        ("mock_slack_failure", "http://urbaneats-api:8000/process-current", None),
        ("mock_gmail_failure", "http://urbaneats-api:8000/process-current", None),
        ("mock_slack_rejected", "http://urbaneats-api:8000/process-current", None),
        ("mock_gmail_rejected", "http://urbaneats-api:8000/process-current", None),
        ("mock_gmail_disabled", "http://urbaneats-api:8000/process-current", None),
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
                if name == "mock_gmail_disabled" and channel == "Gmail":
                    continue
                if (name == "mock_slack_rejected" and channel == "Slack") or (name == "mock_gmail_rejected" and channel == "Gmail"):
                    receipt = "{ok:false,error:'ratelimited'}" if channel == "Slack" else "{statusCode:429}"
                elif name == "mock_unknown" or (name == "mock_slack_failure" and channel == "Slack") or (name == "mock_gmail_failure" and channel == "Gmail"):
                    receipt = "{error:'ambiguous timeout'}"
                elif name in {"mock_green", "mock_slack_failure", "mock_gmail_failure", "mock_slack_rejected", "mock_gmail_rejected", "mock_gmail_disabled"}:
                    receipt = "{ok:true,channel:'mock-channel',message_timestamp:'mock-receipt'}" if channel == "Slack" else "{id:'mock-receipt'}"
                elif channel == "Slack":
                    receipt = "$runIndex<2 ? {ok:false,error:'ratelimited'} : {ok:true,channel:'mock-channel',message_timestamp:'mock-receipt'}"
                else:
                    receipt = "$runIndex<1 ? {statusCode:429} : {id:'mock-receipt'}"
                node.update(type="n8n-nodes-base.code", typeVersion=2, disabled=False,
                            parameters={"jsCode": "return [{json:" + receipt + "}];"})
            if node["name"] == "Call UrbanEats API":
                node["parameters"]["url"] = url
                node["parameters"]["options"]["timeout"] = 200 if name == "timeout" else 5000
                if name in {"healthy", "green", "data_failure", "recovery", "mock_retry", "mock_unknown", "mock_green", "mock_slack_failure", "mock_gmail_failure", "mock_slack_rejected", "mock_gmail_rejected", "mock_gmail_disabled"}:
                    # Exercise the identical API pipeline with isolated request fixtures;
                    # verification must not rewrite the user's mounted current source.
                    payload = {} if name == "data_failure" else demo_batch(4 if name in {"green", "mock_green"} else 24)
                    if payload:
                        # Windows clock resolution can give adjacent fixtures the
                        # same timestamp ID; different cases are different batches.
                        payload["source_batch_id"] += "-" + name
                    node["parameters"].update(url="http://urbaneats-api:8000/process-batch",
                        sendBody=True, specifyBody="json", jsonBody=json.dumps(payload))
            if node["name"] in {"API Retry Delay", "Delivery Retry Delay"}:
                node["parameters"]["amount"] = 0.1
        (directory / (name + ".json")).write_text(json.dumps(workflow), encoding="utf-8")
    return directory, cases


def main(output=None):
    """Verify in isolation; an explicit output preserves historical run evidence."""
    target = Path(output) if output is not None else ROOT / "evaluation/results/phase3c3_native_verification.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    report = {"phase": "3C.3", "result": "FAIL", "real_notifications": 0,
              "hosted_llm_calls": 0, "cases": [], "started_monotonic": time.monotonic()}
    stopped = False
    created = []
    try:
        stage(report, "fixture preparation")
        directory, cases = prepare()
        stage(report, "fixture preparation", "completed")
        stage(report, "initial API health")
        report["initial_health"] = health()
        stage(report, "API TEST_MODE safety")
        safety = docker("exec", "urbaneats-urbaneats-api-1", "python", "-c",
                        "import os; print(os.getenv('TEST_MODE','true').lower()!='false')")
        if safety != "True":
            raise RuntimeError("Native verification requires API TEST_MODE")
        stage(report, "API TEST_MODE safety", "completed")
        mount = f"type=bind,source={directory},target=/verify,readonly"
        stage(report, "disposable container creation")
        for container in (N8N_TEST, FIXTURE_TEST):
            if docker("ps", "-aq", "--filter", "name=^/" + container + "$"):
                raise RuntimeError("Disposable verifier name already exists; inspect before reuse")
        created.append(N8N_TEST)
        docker("run", "-d", "--rm", "--name", N8N_TEST, "--network", "urbaneats_private",
               "--entrypoint", "/bin/sh", "-e", "N8N_DIAGNOSTICS_ENABLED=false",
               "-e", "N8N_GRACEFUL_SHUTDOWN_TIMEOUT=1",
               "-e", "N8N_VERSION_NOTIFICATIONS_ENABLED=false", "-e", "N8N_TEMPLATES_ENABLED=false",
               "--mount", mount, IMAGE, "-c", "while :; do sleep 60; done")
        stage(report, "disposable container creation", "completed")
        stage(report, "CLI initialization")
        docker("exec", "-u", "root", N8N_TEST, "node", "/verify/initialize_cli.cjs",
               timeout=CLI_TIMEOUT)
        stage(report, "CLI initialization", "completed")
        import_workflow(report, directory, "public")
        report["public_workflow_import"] = "PASS"
        report["public_workflow_sha256"] = hashlib.sha256(
            (ROOT / "workflows/n8n/urbaneats_live.json").read_bytes()).hexdigest()
        stage(report, "fixture server")
        created.append(FIXTURE_TEST)
        docker("run", "-d", "--rm", "--name", FIXTURE_TEST, "--network", "urbaneats_private",
               "--entrypoint", "python", "--mount", mount, "urbaneats-urbaneats-api",
               "/verify/mock_transport.py")
        stage(report, "fixture server", "completed")
        for name, _, category in cases:
            stage(report, "native case " + name)
            if name == "stopped_api":
                stopped = True
                docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                       "stop", "urbaneats-api")
            if name == "refused":
                docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                       "start", "urbaneats-api")
                for _ in range(15):
                    try:
                        report["recovered_health"] = health()
                        break
                    except Exception:
                        time.sleep(1)
                else:
                    raise RuntimeError("API recovery health failed")
                stopped = False
            import_workflow(report, directory, name)
            def execute():
                stage(report, "native execution " + name)
                docker("exec", N8N_TEST, "/bin/sh", "-c",
                       f"n8n execute --id=ue3b-test-{name} >/tmp/ue3b-execution.log 2>&1",
                       timeout=CLI_TIMEOUT)
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
                expected_route = "GREEN_SUMMARY" if name in {"green", "mock_green"} else "DATA_FAILURE" if name == "data_failure" else "RED_ALERT"
                assert result["routing_status"] == expected_route, result
            if name in {"green", "mock_green"}:
                assert result["slack"] == "SKIPPED_POLICY" and result["slack_attempts"] == 0, result
                assert result["gmail"] == ("SUCCESS" if name == "mock_green" else "SKIPPED_TEST_MODE"), result
            if name == "mock_gmail_disabled":
                assert result["slack"] == "SUCCESS" and result["gmail"] == "UNKNOWN", result
                assert result["gmail_attempts"] == 0 and result["event_type"] == "notification_unverified", result
            if result["slack"] == "UNKNOWN" or result["gmail"] == "UNKNOWN":
                assert result["event_type"] == "notification_unverified", result
            if name == "mock_slack_failure":
                assert result["slack"] == "UNKNOWN" and result["gmail"] == "SUCCESS", result
            if name == "mock_gmail_failure":
                assert result["gmail"] == "UNKNOWN" and result["slack"] == "SUCCESS", result
            if name == "mock_slack_rejected":
                assert result["slack"] == "FAILURE" and result["slack_attempts"] == 3 and result["gmail"] == "SUCCESS", result
            if name == "mock_gmail_rejected":
                assert result["gmail"] == "FAILURE" and result["gmail_attempts"] == 3 and result["slack"] == "SUCCESS", result
            if name == "mock_retry":
                assert result["slack"] == result["gmail"] == "SUCCESS", result
                assert result["slack_attempts"] == 3 and result["gmail_attempts"] == 2, result
            elif name == "mock_unknown":
                assert result["slack"] == result["gmail"] == "UNKNOWN", result
                assert result["slack_attempts"] == result["gmail_attempts"] == 1, result
            report["cases"].append({"name": name, **result})
            print(json.dumps({"name": name, **result}), flush=True)
            if name in {"stopped_api", "healthy", "mock_retry", "mock_green"}:
                repeat = execute()
                assert repeat["duplicate_suppression"], repeat
                assert repeat["gmail"] == "DUPLICATE_SUPPRESSED" and repeat["slack"] == ("SKIPPED_POLICY" if name == "mock_green" else "DUPLICATE_SUPPRESSED"), repeat
                report["cases"].append({"name": "duplicate_" + name, **repeat})
                print(json.dumps({"name": "duplicate_" + name, **repeat}), flush=True)
            stage(report, "native case " + name, "completed")
        report["recovered_health"] = health()
        report["result"] = "PASS"
    except BaseException as error:
        report["result"] = "INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "FAIL"
        report["failure_stage"] = report.get("current_stage", "setup")
        if isinstance(error, KeyboardInterrupt):
            report["failure_category"] = "INTERRUPTED"
        elif isinstance(error, subprocess.TimeoutExpired):
            imported = "Successfully imported 1 workflow." in report.get("import_diagnostic", {}).get("markers", [])
            report["failure_category"] = (
                "PROCESS_EXIT_TIMEOUT" if imported and "workflow import" in report["failure_stage"]
                else "IMPORT_TIMEOUT" if "workflow import" in report["failure_stage"] else "COMMAND_TIMEOUT")
        else:
            report["failure_category"] = "IMPORT_FAILED" if "workflow import" in report["failure_stage"] else type(error).__name__
        raise
    finally:
        stage(report, "cleanup")
        errors = []
        try:
            if stopped:
                try:
                    docker("compose", "-p", "urbaneats", "-f", str(ROOT / "docker/compose.yaml"),
                           "start", "urbaneats-api")
                    for attempt in range(15):
                        try:
                            report["recovered_health"] = health()
                            break
                        except Exception:
                            if attempt == 14:
                                raise
                            time.sleep(1)
                except BaseException:
                    errors.append("API restoration failed")
            for container in created:
                try:
                    docker("rm", "-f", container, check=False)
                    remaining = docker("ps", "-aq", "--filter", "name=^/" + container + "$")
                    if remaining:
                        errors.append(container + " remains")
                except BaseException:
                    errors.append(container + " cleanup unverified")
            report["cleanup"] = {"result": "FAIL" if errors else "PASS", "errors": errors}
            if errors:
                report["result"] = "FAIL" if report["result"] != "INTERRUPTED" else "INTERRUPTED"
                report.setdefault("failure_stage", "cleanup")
            stage(report, "cleanup", "completed" if not errors else "failed")
        finally:
            temporary = target.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
            temporary.replace(target)
        if errors:
            raise RuntimeError("Verifier cleanup failed; see result artifact")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a new result without replacing historical evidence")
    main(parser.parse_args().output)
