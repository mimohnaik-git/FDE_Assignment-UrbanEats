"""Atomic per-batch/channel claims. Ambiguous sends stay claimed for manual review."""

import hashlib
import json
import os
from pathlib import Path

from .validation import utc_now


def delivery_event(
    directory: Path,
    result: dict,
    channel: str,
    operation: str,
    outcome=None,
    attempts=0,
    error_category=None,
):
    if channel not in {"slack", "gmail"} or operation not in {"claim", "complete"}:
        raise ValueError("invalid_delivery_request")
    if not isinstance(attempts, int) or not 0 <= attempts <= 3:
        raise ValueError("invalid_attempts")
    if outcome not in {None, "success", "failure", "unknown"}:
        raise ValueError("invalid_outcome")
    if error_category not in {None, "rate_limited", "provider_receipt_unverified"}:
        raise ValueError("invalid_error_category")
    packet = result["evidence"]
    identity = packet["source_batch_id"] or packet["source_sha256"]
    key = hashlib.sha256(f"{identity}:{channel}".encode()).hexdigest()
    directory = directory / "delivery"
    directory.mkdir(parents=True, exist_ok=True)
    claim = directory / (key + ".claim")
    test_mode = os.getenv("TEST_MODE", "true").lower() != "false"
    send = False
    status = "TEST_MODE_DISABLED"
    if operation == "claim" and not test_mode:
        try:
            with claim.open("x", encoding="utf-8") as handle:
                handle.write(result["run_id"])
                handle.flush()
                os.fsync(handle.fileno())
            send, status = True, "CLAIMED"
        except FileExistsError:
            status = "DUPLICATE_SUPPRESSED"
    elif operation == "complete":
        if not claim.exists() or claim.read_text() != result["run_id"]:
            raise ValueError("claim_owner_mismatch")
        status = (outcome or "unknown").upper()
    event = {
        "run_id": result["run_id"],
        "source_batch_id": identity,
        "channel": channel,
        "operation": operation,
        "status": status,
        "attempts": attempts,
        "at": utc_now().isoformat(),
        "send": send,
        "duplicate_suppression": status == "DUPLICATE_SUPPRESSED",
        "attempted": operation == "complete",
        "success": status == "SUCCESS",
        "error_category": error_category
        or ("provider_receipt_unverified" if status == "UNKNOWN" else None),
        "retry": operation == "complete"
        and status == "FAILURE"
        and error_category == "rate_limited"
        and attempts < 3,
        "final_result": status,
    }
    # Append one small record under an exclusive file lock via per-event unique files.
    from uuid import uuid4

    (directory / (uuid4().hex + ".json")).write_text(json.dumps(event), encoding="utf-8")
    return event
