import json
import os
from pathlib import Path


def persist_run(directory: Path, result: dict, started_at: str, completed_at: str):
    """One immutable UUID file per execution; atomically published, no raw secrets."""

    directory.mkdir(parents=True, exist_ok=True)

    packet = result.get("evidence") or {}

    log = {
        "run_id": result["run_id"],
        "started_at": started_at,
        "completed_at": completed_at,
        "source_batch": result.get("source_batch_id"),
        "validation_status": result["validation_status"],
        "records_received": result["records_received"],
        "records_scored": len(result.get("predictions", [])),
        "routing_status": result["routing_status"],
        "model_version": result.get("model_version"),
        "threshold": result.get("threshold"),
        "evidence_ids": [f["evidence_id"] for f in packet.get("facts", [])],
        "error_summary": result.get("errors", []),
        "notification_status": "DELIVERY_EVENTS_SEPARATE",
        "llm": result.get("briefing", {}).get("formatter"),
        "result": result,
    }

    target = directory / f"{result['run_id']}.json"

    temporary = target.with_suffix(".tmp")

    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(log, handle, indent=2, allow_nan=False)

        handle.flush()

        os.fsync(handle.fileno())

    os.replace(temporary, target)

    return log
