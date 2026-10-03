"""Verify shared notification semantics using the JS embedded in the n8n export."""
import hashlib
import json
import subprocess

import pytest
from js_runner import evaluate_js

from urbaneats.config import ROOT

LOGIC = ROOT / "workflows/n8n/notification_logic.cjs"


def shared(expression, values):
    return evaluate_js(LOGIC, expression, values)


def packet(route="RED_ALERT", source="source-one", run="a"):
    return {"run_id": "UE-" + run * 32, "source_batch_id": source, "routing_status": route,
            "evidence": {"routing_status": route, "source_batch_id": source,
                         "facts": [{"evidence_id": "KPI-BATCH"}]},
            "briefing": {"text": "canonical " + route}}


def normalize(response, attempt=1, settings=None):
    return shared("f.normalizeNotification(v.response,v.settings,v.execution,v.attempt,[],v.now)", {
        "response": response, "settings": settings or {"test_mode": True},
        "execution": {"id": "test", "mode": "manual"}, "attempt": attempt,
        "now": "2026-10-03T00:00:00Z"})


@pytest.mark.parametrize("value", ["", "abc", "source:case-sensitive-A", "रन", "a" * 100])
def test_claim_hash_matches_sha256(value):
    assert shared("f.identityHash(v)", value) == hashlib.sha256(value.encode()).hexdigest()


@pytest.mark.parametrize("route", ["DATA_FAILURE", "GREEN_SUMMARY", "RED_ALERT"])
def test_unified_packet_preserves_api_brief_and_route(route):
    value = packet(route)
    result = normalize(value)
    assert result["evidence_origin"] == "api" and result["routing_status"] == route
    assert result["text"] == value["briefing"]["text"]
    assert result["evidence"] == value["evidence"]
    assert result["subject"] == "UrbanEats " + route


def test_batch_claim_stable_across_api_runs_and_force_is_explicit():
    original = normalize(packet())
    assert normalize(packet(run="b"))["claim_table_name"] == original["claim_table_name"]
    assert normalize(packet(source="source-two"))["claim_table_name"] != original["claim_table_name"]
    assert normalize(packet(), settings={"test_mode": True, "force_retry_nonce": "force1"})[
        "claim_table_name"] != original["claim_table_name"]


def test_outage_retry_bound_and_legacy_identity_preserved():
    settings = {"test_mode": True, "orchestration_run_id_override": "ORCH-original"}
    for attempt in [1, 2]:
        assert normalize({"error": "ECONNREFUSED"}, attempt, settings)["retry_api"]
    final = normalize({"error": "ECONNREFUSED"}, 3, settings)
    assert final["routing_status"] == "DATA_FAILURE" and not final["retry_api"]
    assert final["claim_table_name"] == "UE_ORCH_ORCH-original"
    assert not {"model_version", "records_scored", "facts"} & final["evidence"].keys()
    assert not normalize({"statusCode": 401}, 1)["retry_api"]


@pytest.mark.parametrize("route", ["GREEN_SUMMARY", "RED_ALERT"])
def test_poisoned_success_body_is_never_used_after_http_failure(route):
    result = normalize({"statusCode": 503, "body": json.dumps(packet(route))}, 3)
    assert result["routing_status"] == "DATA_FAILURE"
    assert result["evidence_origin"] == "orchestration"
    assert "canonical" not in result["text"]


def initial(test_mode=False, duplicate=False):
    value = normalize(packet(), settings={"test_mode": test_mode})
    native = {"error": "already exists"} if duplicate else {"id": "table", "name": value["claim_table_name"]}
    return shared("f.prepareNotificationClaim(v.native,v.packet,v.now)", {
        "native": native, "packet": value, "now": "2026-10-03T00:00:01Z"})


@pytest.mark.parametrize("channel", ["slack", "gmail"])
def test_shared_receipts_retry_only_definite_rate_limit(channel):
    rate = {"ok": False, "error": "ratelimited"} if channel == "slack" else {"statusCode": 429}
    for count in [1, 2, 3]:
        row = shared("f.notificationReceipt(v.initial,v.channel,v.receipt,v.count,v.now)", {
            "initial": initial(), "channel": channel, "receipt": rate, "count": count,
            "now": "2026-10-03T00:00:02Z"})
        assert row["retry_allowed"] is (count < 3)
    row = shared("f.notificationReceipt(v.initial,v.channel,{},1,v.now)", {
        "initial": initial(), "channel": channel, "now": "2026-10-03T00:00:02Z"})
    assert row[channel + "_delivery_state"] == "UNKNOWN" and not row["retry_allowed"]


@pytest.mark.parametrize("test_mode,duplicate,state", [
    (True, False, "SKIPPED_TEST_MODE"), (False, True, "DUPLICATE_SUPPRESSED")])
def test_shared_gate_skips_both_channels(test_mode, duplicate, state):
    row = initial(test_mode, duplicate)
    for channel in ["slack", "gmail"]:
        result = shared("f.notificationReceipt(v.initial,v.channel,{},0,v.now)", {
            "initial": row, "channel": channel, "now": "2026-10-03T00:00:02Z"})
        assert result[channel + "_delivery_state"] == state
        assert result[channel + "_attempts"] == 0 and not result["retry_allowed"]


def test_small_workflow_single_sends_and_shared_audit():
    workflow = json.loads((ROOT / "workflows/n8n/urbaneats_live.json").read_text())
    assert len(workflow["nodes"]) == 22
    for kind in ["slack", "gmail"]:
        send = [n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base." + kind]
        assert len(send) == 1 and send[0]["disabled"] and not send[0].get("credentials")
    settings = next(n for n in workflow["nodes"] if n["name"] == "Settings")
    assert "test_mode:true" in settings["parameters"]["jsCode"]
    assert not workflow["active"] and workflow["settings"]["timezone"] == "Asia/Kolkata"


def test_unknown_claim_error_blocks_delivery():
    with pytest.raises(subprocess.CalledProcessError):
        shared("f.prepareNotificationClaim({error:'storage unavailable'},v,v.started_at)", normalize(packet()))


def test_completion_retains_independent_channel_outcomes():
    prepared = initial()
    rows = []
    for channel, receipt in [("slack", {"ok": True, "ts": "local-receipt"}),
                             ("gmail", {"error": "ambiguous timeout"})]:
        rows.append(shared("f.notificationReceipt(v.initial,v.channel,v.receipt,1,v.now)", {
            "initial": prepared, "channel": channel, "receipt": receipt,
            "now": "2026-10-03T00:00:02Z"}))
    result = shared("f.completeNotification(v.initial,v.rows,v.now)", {
        "initial": prepared, "rows": rows, "now": "2026-10-03T00:00:03Z"})
    assert result["slack_delivery_state"] == "SUCCESS"
    assert result["gmail_delivery_state"] == "UNKNOWN"
    with pytest.raises(subprocess.CalledProcessError):
        shared("f.completeNotification(v.initial,v.rows,v.now)", {
            "initial": prepared, "rows": rows[:1], "now": "2026-10-03T00:00:03Z"})
