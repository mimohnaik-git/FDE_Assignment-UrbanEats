"""Phase-3C policy, citations, fallback and formatter configuration without credentials."""
import copy
import json

import httpx
import pytest
from js_runner import evaluate_js

from urbaneats.briefing import MODEL_LIMITATION, fact_sentences, validate_formatter_output
from urbaneats.config import ROOT
from urbaneats.provider import HostedFormatter, configured_provider
from urbaneats.service import Runtime

LOGIC = ROOT / "workflows/n8n/notification_logic.cjs"


def notification(route, test_mode=False):
    response = {"run_id": "UE-" + "a" * 32, "source_batch_id": "policy-batch", "routing_status": route,
                "evidence": {"routing_status": route, "facts": [{"evidence_id": "KPI-BATCH"}]},
                "briefing": {"text": "safe canonical brief"}}
    return evaluate_js(LOGIC, "f.normalizeNotification(v.response,v.settings,{id:'policy',mode:'manual'},1,[],v.now)",
                       {"response": response, "settings": {"test_mode": test_mode},
                        "now": "2026-10-03T00:00:00Z"})


@pytest.mark.parametrize("route", ["GREEN_SUMMARY", "RED_ALERT", "DATA_FAILURE"])
@pytest.mark.parametrize("test_mode", [False, True])
def test_channel_policy_and_test_gate(route, test_mode):
    packet = notification(route, test_mode)
    assert packet["channel_policy"] == {"slack": route != "GREEN_SUMMARY", "gmail": True}
    row = evaluate_js(LOGIC, "f.prepareNotificationClaim({id:'table',name:v.claim_table_name},v,v.started_at)", packet)
    if route == "GREEN_SUMMARY":
        assert row["slack_delivery_state"] == "SKIPPED_POLICY"
        receipt = evaluate_js(LOGIC, "f.notificationReceipt(v,'slack',{error:'must not send'},0,v.completed_at)", row)
        assert receipt["slack_attempts"] == 0 and not receipt["retry_allowed"]
        assert receipt["slack_delivery_state"] == "SKIPPED_POLICY"
    assert row["gmail_delivery_state"] == ("SKIPPED_TEST_MODE" if test_mode else "PENDING")


def cited_output(packet):
    sentences = fact_sentences(packet)
    return {"items": [{"evidence_id": f["evidence_id"],
                       "text": sentences[f["evidence_id"]] + f" [evidence:{f['evidence_id']}]",
                       "action_ids": f["approved_action_ids"]} for f in packet["facts"]]}


@pytest.mark.parametrize("change", ["valid", "unknown_id", "unknown_citation", "number", "action",
                                    "provenance", "missing_citation", "observed_rate", "routing", "malformed"])
def test_cited_formatter_closed_contract(runtime, batch, change):
    packet = runtime.process(batch)["evidence"]
    original = copy.deepcopy(packet)
    output = cited_output(packet)
    item = output["items"][0]
    if change == "unknown_id":
        item["evidence_id"] = "UNKNOWN"
    elif change == "unknown_citation":
        item["text"] = item["text"].replace("[evidence:KPI-BATCH]", "[evidence:UNKNOWN]")
    elif change == "number":
        item["text"] += " 999 orders"
    elif change == "action":
        item["action_ids"] = ["STAFFING"]
    elif change == "provenance":
        item["text"] += " [run:changed]"
    elif change == "missing_citation":
        item["text"] = fact_sentences(packet)["KPI-BATCH"]
    elif change == "observed_rate":
        item["text"] = item["text"].replace("predicted-risk fraction", "observed cancellation rate")
    elif change == "routing":
        output["routing_status"] = "GREEN_SUMMARY"
    elif change == "malformed":
        output = {"items": "malformed"}
    if change == "valid":
        assert validate_formatter_output(output, packet) == output
    else:
        with pytest.raises(ValueError):
            validate_formatter_output(output, packet)
    assert packet == original


@pytest.mark.parametrize("mode", ["unavailable", "malformed", "validation", "valid"])
def test_provider_fallback_preserves_route_and_channel_messages(config, batch, mode):
    class Provider:
        def generate(self, evidence):
            if mode == "unavailable":
                raise RuntimeError("unavailable")
            if mode == "malformed":
                return None
            output = cited_output(evidence)
            if mode == "validation":
                output["items"][0]["text"] += " invented cause"
            return output
    result = Runtime(config, Provider()).process(batch)
    assert result["routing_status"] == "RED_ALERT"
    assert result["briefing"]["formatter"]["provider_status"] == ("VALIDATED" if mode == "valid" else "FALLBACK")
    messages = result["briefing"]["channels"]
    for key in ["slack_text", "gmail_text"]:
        assert MODEL_LIMITATION in messages[key]
        assert "[evidence:" in messages[key] and "invented cause" not in messages[key]
        assert result["run_id"] in messages[key] and batch["source_batch_id"] in messages[key]
    assert "{\"" not in messages["gmail_text"]


def test_groq_unconfigured_and_test_mode_never_calls_transport(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_MODEL", "locally-selected-model")
    monkeypatch.setenv("GROQ_BASE_URL", "https://formatter.invalid/v1")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    provider = HostedFormatter(httpx.MockTransport(lambda request: pytest.fail("transport called")))
    assert provider.name == "groq" and provider.model == "locally-selected-model" and provider.key == ""
    monkeypatch.setenv("TEST_MODE", "true")
    assert configured_provider() is None
    with pytest.raises(ValueError, match="test_mode"):
        provider.generate({})
    monkeypatch.setenv("TEST_MODE", "false")
    with pytest.raises(ValueError, match="provider_not_configured"):
        provider.generate({})


def test_presentation_failure_and_green(runtime, batch):
    green = copy.deepcopy(batch)
    green["orders"] = green["orders"][:4]
    result = runtime.process(green)
    assert result["briefing"]["channels"]["slack_text"] == ""
    assert "GREEN_SUMMARY" in result["briefing"]["channels"]["gmail_subject"]
    failure = runtime.process({})
    assert "[evidence:FAILURE]" in failure["briefing"]["channels"]["gmail_text"]
    assert "No GREEN/RED assessment produced" in failure["briefing"]["channels"]["slack_text"]


def test_phase3c_workflow_single_channel_nodes():
    workflow = json.loads((ROOT / "workflows/n8n/urbaneats_live.json").read_text())
    assert len(workflow["nodes"]) == 23 and not workflow["active"]
    assert workflow["settings"]["timezone"] == "Asia/Kolkata"
    for kind in ["slack", "gmail"]:
        nodes = [n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base." + kind]
        assert len(nodes) == 1 and nodes[0]["disabled"] and not nodes[0].get("credentials")
