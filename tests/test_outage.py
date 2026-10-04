"""Exercise the exact JS embedded in n8n, without network or notification credentials."""
import json
import subprocess

import pytest
from js_runner import evaluate_js

from urbaneats.config import ROOT

LOGIC = ROOT / "workflows/n8n/orchestration_logic.cjs"


def js(expression, values):
    return evaluate_js(LOGIC, expression, values)


@pytest.mark.parametrize("response,category", [
    ({"error": {"code": "ECONNREFUSED"}}, "CONNECTION_REFUSED"),
    ({"error": "The service refused the connection - perhaps it is offline"}, "CONNECTION_REFUSED"),
    ({"error": {"code": "ENOTFOUND"}}, "DNS_SERVICE_FAILURE"),
    ({"error": "incorrect host (domain) value"}, "DNS_SERVICE_FAILURE"),
    ({"error": {"code": "ETIMEDOUT"}}, "TIMEOUT"),
    ({"error": "The connection timed out"}, "TIMEOUT"),
    ({"statusCode": 500, "body": "failure"}, "HTTP_5XX"),
    ({"statusCode": 503, "body": "failure"}, "HTTP_5XX"),
    ({"statusCode": 401, "body": "failure"}, "HTTP_ERROR"),
    ({"statusCode": 200, "body": "<html>bad</html>"}, "MALFORMED_RESPONSE"),
    ({"statusCode": 200, "body": "{}"}, "MALFORMED_RESPONSE"),
])
def test_transport_classification(response, category):
    assert js("f.classifyApiResponse(v)", response)["failure_category"] == category


@pytest.mark.parametrize("route", ["GREEN_SUMMARY", "RED_ALERT", "DATA_FAILURE"])
@pytest.mark.parametrize("body_key", ["body", "data"])
def test_healthy_api_response_preserved(route, body_key):
    packet = {"run_id": "UE-" + "a" * 32, "routing_status": route,
              "evidence": {"routing_status": route, "facts": [{"evidence_id": "KPI-BATCH"}]},
              "briefing": {"text": "canonical API brief"}}
    assert js("f.classifyApiResponse(v)", {"statusCode": 200, body_key: json.dumps(packet)}) == {
        "api_response": packet}


@pytest.mark.parametrize("prior_route", ["GREEN_SUMMARY", "RED_ALERT"])
def test_outage_never_reuses_prior_assessment(prior_route):
    prior = {"routing_status": prior_route, "model_version": "STALE-MODEL",
             "records_scored": 99, "evidence_id": "OLD-HOTSPOT", "source_order_ids": ["OLD-ORDER"]}
    values = {"context": {**prior, "orchestration_run_id": "ORCH-test", "started_at": "2026-10-03T00:00:00Z",
                          "test_mode": True, "source_batch_id": None, "claim_table_name": "UE_ORCH_ORCH-test"},
              "response": {"statusCode": 503, "body": json.dumps(prior), "previous": prior}}
    result = js("f.constructOutage(v.context,{...f.classifyApiResponse(v.response),attempt_count:3,attempt_history:[]},'2026-10-03T00:00:03Z')", values)
    evidence = result["outage_evidence"]
    assert evidence["routing_status"] == "DATA_FAILURE"
    assert evidence["evidence_origin"] == "orchestration"
    assert evidence["failure_category"] == "HTTP_5XX"
    assert not {"model_version", "records_scored", "evidence_id", "source_order_ids"} & evidence.keys()
    assert "STALE-MODEL" not in json.dumps(result)
    assert "OLD-HOTSPOT" not in result["notification_text"]
    assert "No GREEN or RED operational assessment was produced" in result["notification_text"]


def test_identity_reexecution_force_and_timezone():
    values = {"settings": {"orchestration_run_id_override": "ORCH-retry", "test_mode": True},
              "execution": {"id": "one", "mode": "manual"}, "now": "2026-10-03T23:00:00Z"}
    a = js("f.initializeOrchestration(v.settings,v.execution,v.now)", values)
    values["execution"]["id"] = "two"
    assert js("f.initializeOrchestration(v.settings,v.execution,v.now)", values)["claim_table_name"] == a["claim_table_name"]
    values["settings"]["force_retry_nonce"] = "explicit1"
    assert js("f.initializeOrchestration(v.settings,v.execution,v.now)", values)["claim_table_name"] != a["claim_table_name"]
    values["settings"] = {}
    values["execution"]["mode"] = "trigger"
    assert js("f.initializeOrchestration(v.settings,v.execution,v.now)", values)["orchestration_run_id"] == "ORCH-20261004-0730"


def notification_js(expression, values):
    return evaluate_js(ROOT / "workflows/n8n/notification_logic.cjs", expression, values)


def outage_notification(test_mode=True):
    return notification_js("f.normalizeNotification({error:'ETIMEDOUT'},v,{id:'test',mode:'manual'},3,[], '2026-10-03T00:00:00Z')",
                           {"test_mode": test_mode})


def test_persistent_claim_test_mode_duplicate_and_audit_error():
    packet = outage_notification()
    values = {"packet": packet, "native": {"id": "local-table", "name": packet["claim_table_name"]}}
    result = notification_js("f.prepareNotificationClaim(v.native,v.packet,'2026-10-03T00:00:03Z')", values)
    assert result["slack_delivery_state"] == result["gmail_delivery_state"] == "SKIPPED_TEST_MODE"
    values["packet"]["test_mode"] = False
    values["native"] = {"error": "Data table already exists"}
    result = notification_js("f.prepareNotificationClaim(v.native,v.packet,'2026-10-03T00:00:03Z')", values)
    assert result["duplicate_suppression"] and result["slack_delivery_state"] == "DUPLICATE_SUPPRESSED"
    values["native"] = {"error": "permission denied"}
    with pytest.raises(subprocess.CalledProcessError):
        notification_js("f.prepareNotificationClaim(v.native,v.packet,'2026-10-03T00:00:03Z')", values)


@pytest.mark.parametrize("channel", ["slack", "gmail"])
def test_outage_delivery_retries_and_unknown_receipt(channel):
    packet = outage_notification(False)
    initial = notification_js("f.prepareNotificationClaim(v.native,v.packet,'2026-10-03T00:00:03Z')", {
        "packet": packet, "native": {"id": "table", "name": packet["claim_table_name"]}})
    receipt = {"ok": False, "error": "ratelimited"} if channel == "slack" else {"error": {"statusCode": 429}}
    for attempt in [1, 2, 3]:
        row = notification_js("f.notificationReceipt(v.initial,v.channel,v.receipt,v.attempt,'2026-10-03T00:00:03Z')",
                 {"initial": initial, "channel": channel, "receipt": receipt, "attempt": attempt})
        assert row["retry_allowed"] is (attempt < 3)
    row = notification_js("f.notificationReceipt(v.initial,v.channel,{},1,'2026-10-03T00:00:03Z')",
                          {"initial": initial, "channel": channel})
    assert row[channel + "_delivery_state"] == "UNKNOWN" and not row["retry_allowed"]


def test_outage_workflow_independent_and_sanitized():
    workflow = json.loads((ROOT / "workflows/n8n/urbaneats_live.json").read_text())
    nodes = {n["name"]: n for n in workflow["nodes"]}
    assert not workflow["active"]
    assert not nodes["Call UrbanEats API"]["retryOnFail"]  # explicit, countable retry loop
    assert nodes["Claim Run"]["parameters"]["options"]["createIfNotExists"] is False
    for node in nodes.values():
        assert not node.get("credentials") and not node.get("webhookId")
        if node["type"] in {"n8n-nodes-base.slack", "n8n-nodes-base.gmail"}:
            assert node["disabled"] is True
    # Unified orchestration claims/logs never depend on the API being available.
    for name in ["Claim Run", "Persist Prepared Audit", "Persist Delivery Audit", "Persist Completed Audit"]:
        assert nodes[name]["type"] == "n8n-nodes-base.dataTable"
    assert all(edge["node"] in nodes for c in workflow["connections"].values()
               for output in c["main"] for edge in output)
