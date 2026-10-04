import copy
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from urbaneats.briefing import fact_sentences, validate_citations, validate_formatter_output
from urbaneats.config import Config
from urbaneats.hotspots import aggregate_hotspots
from urbaneats.service import Runtime, create_app
from urbaneats.validation import validate_batch


def test_valid_batch_scores_and_logs(runtime, batch, config):

    result = runtime.process(batch)

    assert result["status"] == "SUCCESS", result

    assert len(result["predictions"]) == len(batch["orders"])

    for prediction in result["predictions"]:
        assert set(prediction) == {
            "order_id",
            "cancellation_probability",
            "risk_flag",
            "model_version",
            "run_id",
        }

    log = json.loads((config.runs_dir / f"{result['run_id']}.json").read_text())

    assert log["records_scored"] == 24

    assert log["completed_at"] >= log["started_at"]

    assert log["notification_status"] == "DELIVERY_EVENTS_SEPARATE"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "empty",
        "numeric_string",
        "nan",
        "duplicate",
        "stale",
        "future",
        "naive",
        "invalid_category",
        "discount",
        "outcome_field",
        "historical_order",
    ],
)
def test_invalid_never_green(runtime, batch, mutation, config):

    now = datetime.now(timezone.utc)

    if mutation == "missing":
        del batch["orders"][0]["order_value"]

    elif mutation == "empty":
        batch["orders"] = []

    elif mutation == "numeric_string":
        batch["orders"][0]["order_value"] = "500"

    elif mutation == "nan":
        batch["orders"][0]["discount_applied"] = float("nan")

    elif mutation == "duplicate":
        batch["orders"][1]["order_id"] = batch["orders"][0]["order_id"]

    elif mutation == "stale":
        batch["generated_at"] = (now - timedelta(days=1)).isoformat()

    elif mutation == "future":
        batch["orders"][0]["placed_at"] = (now + timedelta(days=1)).isoformat()

    elif mutation == "naive":
        batch["generated_at"] = now.replace(tzinfo=None).isoformat()

    elif mutation == "invalid_category":
        batch["orders"][0]["payment_method"] = "bitcoin"

    elif mutation == "discount":
        batch["orders"][0]["discount_applied"] = 600

    elif mutation == "outcome_field":
        batch["orders"][0]["order_status"] = "Refunded"

    elif mutation == "historical_order":
        batch["orders"][0]["placed_at"] = "2024-01-01T00:00:00+00:00"

    result = runtime.process(batch)

    assert result["status"] == result["routing_status"] == "DATA_FAILURE"

    assert result["predictions"] == []

    assert list(config.runs_dir.glob("*.json"))


def test_small_group_suppressed(batch, config):

    batch["orders"] = batch["orders"][:4]

    parsed, errors = validate_batch(batch, config)

    assert not errors

    predictions = [{"order_id": o.order_id, "risk_flag": True} for o in parsed.orders]

    group = aggregate_hotspots(parsed, predictions, config)[0]

    assert group["predicted_risk_rate"] == 1

    assert group["support_status"] == "INSUFFICIENT_SUPPORT"

    assert not group["is_hotspot"]


def test_support_and_rate_boundary(batch, config):

    batch["orders"] = batch["orders"][:20]

    parsed, _ = validate_batch(batch, config)

    predictions = [
        {"order_id": o.order_id, "risk_flag": i < 6} for i, o in enumerate(parsed.orders)
    ]

    group = aggregate_hotspots(parsed, predictions, config)[0]

    assert group["support_status"] == "SUPPORTED"

    assert not group["is_hotspot"]  # exactly 30%, policy is strictly greater

    predictions[6]["risk_flag"] = True

    assert aggregate_hotspots(parsed, predictions, config)[0]["is_hotspot"]


def test_evidence_deterministic_and_numbers_match(runtime, batch):

    first, second = runtime.process(batch), runtime.process(batch)

    a, b = first["evidence"], second["evidence"]

    assert a["source_sha256"] == b["source_sha256"]

    assert a["facts"] == b["facts"]

    assert a["run_id"] != b["run_id"]

    for fact in a["facts"]:
        assert fact["denominator"] == len(fact["source_order_ids"])

        assert fact["predicted_risk_rate"] == fact["numerator"] / fact["denominator"]

        assert f"{fact['numerator']}/{fact['denominator']}" in first["briefing"]["text"]

    assert validate_citations(first["briefing"]["text"], a)

    assert not validate_citations(first["briefing"]["text"] + " [evidence:FAKE]", a)

    assert first["metrics"]["observed_cancellation_rate"] is None


class BadProvider:
    def generate(self, packet):

        packet["facts"][0]["numerator"] = 999  # cannot mutate source truth

        return {"items": [{"evidence_id": "FAKE", "text": "Deploy 99 riders", "action_ids": []}]}


class FailingProvider:
    def generate(self, packet):

        raise RuntimeError("pretend provider failure")


class SafeProvider:
    def generate(self, packet):

        sentences = fact_sentences(packet)

        return {
            "items": [
                {
                    "evidence_id": f["evidence_id"],
                    "text": sentences[f["evidence_id"]] + f" [evidence:{f['evidence_id']}]",
                    "action_ids": f["approved_action_ids"],
                }
                for f in packet["facts"]
            ]
        }


@pytest.mark.parametrize("provider", [BadProvider(), FailingProvider()])
def test_llm_invalid_or_failure_fallback(config, batch, provider):

    result = Runtime(config, provider).process(batch)

    assert result["status"] == "SUCCESS"

    assert result["briefing"]["formatter"]["provider_status"] == "FALLBACK"

    assert "99 riders" not in result["briefing"]["text"]

    assert result["evidence"]["facts"][0]["numerator"] <= 24


def test_safe_stub_validated(config, batch):

    result = Runtime(config, SafeProvider()).process(batch)

    assert result["briefing"]["formatter"]["provider_status"] == "VALIDATED"


@pytest.mark.parametrize("change", ["number", "cause", "action", "reference", "omit"])
def test_unsupported_formatter_claims_rejected(runtime, batch, change):

    packet = runtime.process(batch)["evidence"]

    output = SafeProvider().generate(packet)

    if change == "number":
        output["items"][0]["text"] += " 999 cancellations."

    elif change == "cause":
        output["items"][0]["text"] += " Bad preparation caused cancellations."

    elif change == "action":
        output["items"][0]["action_ids"] = ["DEPLOY_RIDERS"]

    elif change == "reference":
        output["items"][0]["evidence_id"] = "INVENTED"

    elif change == "omit":
        output["items"] = []

    with pytest.raises(ValueError):
        validate_formatter_output(output, packet)


def test_api_endpoints(config, batch):

    client = TestClient(create_app(config))

    assert client.get("/health").json()["status"] == "READY"

    response = client.post("/process-batch", json=batch)

    assert response.status_code == 200

    assert response.json()["status"] == "SUCCESS"

    for data in [{}, {"orders": []}, None]:
        assert client.post("/process-batch", json=data).json()["routing_status"] == "DATA_FAILURE"

    assert client.post("/process-batch", content="bad JSON").json()["status"] == "DATA_FAILURE"


def test_current_source_reloaded(config, batch):

    config.source_file.write_text(json.dumps(batch))

    client = TestClient(create_app(config))

    assert client.post("/process-current").json()["status"] == "SUCCESS"

    config.source_file.write_text("<html>not a batch</html>")

    assert client.post("/process-current").json()["routing_status"] == "DATA_FAILURE"


def test_missing_artifact_and_log_failure_fail_closed(config, batch, tmp_path):

    missing = Config(model_dir=tmp_path / "missing", runs_dir=tmp_path / "logs")

    assert Runtime(missing).process(batch)["routing_status"] == "DATA_FAILURE"

    client = TestClient(create_app(missing))

    assert client.get("/health").status_code == 503

    blocker = tmp_path / "file-not-directory"

    blocker.write_text("block")

    no_log = Config(model_dir=config.model_dir, runs_dir=blocker)

    result = Runtime(no_log).process(copy.deepcopy(batch))

    assert result["routing_status"] == "DATA_FAILURE"

    assert result["errors"][0]["code"] == "persistence_failed"
    assert result["evidence"]["routing_status"] == "DATA_FAILURE"
    assert result["evidence"]["facts"][0]["approved_action_ids"] == ["CHECK_DATA"]
