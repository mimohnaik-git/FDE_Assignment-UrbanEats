import copy
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from urbaneats.briefing import fact_sentences
from urbaneats.config import ROOT
from urbaneats.delivery import delivery_event
from urbaneats.provider import HostedFormatter
from urbaneats.service import Runtime, create_app


def test_health_readiness(config):
    health = TestClient(create_app(config)).get("/health").json()
    assert health["model_loaded"] and health["threshold_loaded"]
    assert health["runtime_status"] == "READY"


def test_failure_evidence(runtime):
    result = runtime.process({})
    assert result["evidence"]["routing_status"] == "DATA_FAILURE"
    assert result["evidence"]["records_scored"] == 0
    assert result["evidence"]["facts"][0]["approved_action_ids"] == ["CHECK_DATA"]
    assert "FAILURE" in result["briefing"]["text"]


def test_test_mode_never_claims(runtime, batch, config, monkeypatch):
    monkeypatch.setenv("TEST_MODE", "true")
    result = runtime.process(batch)
    event = delivery_event(config.runs_dir, result, "slack", "claim")
    assert not event["send"]
    assert not list((config.runs_dir / "delivery").glob("*.claim"))


def test_duplicate_channel_and_owner(runtime, batch, config, monkeypatch):
    monkeypatch.setenv("TEST_MODE", "false")
    a, b = runtime.process(batch), runtime.process(batch)
    assert delivery_event(config.runs_dir, a, "slack", "claim")["send"]
    assert delivery_event(config.runs_dir, b, "slack", "claim")["duplicate_suppression"]
    assert delivery_event(config.runs_dir, b, "gmail", "claim")["send"]
    with pytest.raises(ValueError):
        delivery_event(config.runs_dir, b, "slack", "complete", "success", 1)
    assert (
        delivery_event(config.runs_dir, a, "slack", "complete", "unknown", 1)["status"] == "UNKNOWN"
    )
    assert not delivery_event(config.runs_dir, a, "slack", "claim")["send"]


def test_delivery_api_rejects_traversal(config):
    response = TestClient(create_app(config)).post(
        "/delivery", json={"run_id": "../x", "channel": "slack", "operation": "claim"}
    )
    assert response.status_code == 400


@pytest.mark.parametrize("channel", ["slack", "gmail"])
def test_rate_limit_retries_are_bounded(runtime, batch, config, monkeypatch, channel):
    monkeypatch.setenv("TEST_MODE", "false")
    result = runtime.process(batch)
    assert delivery_event(config.runs_dir, result, channel, "claim")["send"]
    for attempt in [1, 2, 3]:
        event = delivery_event(
            config.runs_dir, result, channel, "complete", "failure", attempt, "rate_limited"
        )
        assert event["retry"] is (attempt < 3)
    ambiguous = delivery_event(
        config.runs_dir, result, channel, "complete", "unknown", 1, "provider_receipt_unverified"
    )
    assert not ambiguous["retry"]
    assert not delivery_event(config.runs_dir, result, channel, "claim")["send"]


@pytest.mark.parametrize("mode", ["valid", "number", "action", "timeout", "http"])
def test_hosted_transport_offline(config, batch, monkeypatch, mode):
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "local-test-placeholder")
    monkeypatch.setenv("LLM_BASE_URL", "https://formatter.invalid/v1")
    monkeypatch.setattr("urbaneats.provider.time.sleep", lambda _: None)

    def handler(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("local stub", request=request)
        if mode == "http":
            return httpx.Response(429)
        packet = json.loads(json.loads(request.content)["messages"][0]["content"])["evidence"]
        sentences = fact_sentences(packet)
        items = [
            {
                "evidence_id": f["evidence_id"],
                "text": sentences[f["evidence_id"]] + f" [evidence:{f['evidence_id']}]",
                "action_ids": f["approved_action_ids"],
            }
            for f in packet["facts"]
        ]
        if mode == "number":
            items[0]["text"] += " 999 orders"
        if mode == "action":
            items[0]["action_ids"] = ["STAFFING"]
        return httpx.Response(
            200, json={"choices": [{"message": {"content": json.dumps({"items": items})}}]}
        )

    provider = HostedFormatter(httpx.MockTransport(handler))
    result = Runtime(config, provider).process(batch)
    assert result["briefing"]["formatter"]["provider_status"] == (
        "VALIDATED" if mode == "valid" else "FALLBACK"
    )
    assert provider.attempts == (3 if mode in {"timeout", "http"} else 1)


def test_hosted_test_mode_blocks_transport(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "true")

    def handler(request):
        pytest.fail("TEST_MODE called transport")

    with pytest.raises(ValueError):
        HostedFormatter(httpx.MockTransport(handler)).generate({})


def test_workflow_inactive_safe():
    workflow = json.loads((ROOT / "workflows/n8n/urbaneats_live.json").read_text())
    assert workflow["active"] is False
    assert workflow["settings"]["timezone"] == "Asia/Kolkata"
    names = {n["name"] for n in workflow["nodes"]}
    for n in workflow["nodes"]:
        assert not n.get("credentials") and not n.get("webhookId")
        if n["type"].endswith("httpRequest"):
            assert n["parameters"]["url"].startswith("http://urbaneats-api:8000/")
    for outputs in workflow["connections"].values():
        for output in outputs["main"]:
            assert all(edge["node"] in names for edge in output)


def test_green_and_red_current_model(runtime, batch):
    # Find both deterministic model responses using checkout-only synthetic values.
    routes = set()
    for count in [4, 24]:
        fixture = copy.deepcopy(batch)
        fixture["orders"] = fixture["orders"][:count]
        result = runtime.process(fixture)
        routes.add(result["routing_status"])
    assert routes == {"GREEN_SUMMARY", "RED_ALERT"}
