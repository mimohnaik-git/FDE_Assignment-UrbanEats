import json
import re
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .actions import ACTION_CATALOG
from .briefing import generate_briefing
from .config import Config
from .delivery import delivery_event
from .evidence import canonical_hash, construct_evidence
from .hotspots import aggregate_hotspots
from .inference import infer
from .metrics import current_metrics
from .model import load_artifact
from .presentation import channel_messages
from .provider import configured_provider
from .run_logging import persist_run
from .validation import utc_now, validate_batch


class Runtime:
    def __init__(self, config=None, provider=None):

        self.config = config or Config.from_env()

        self.provider = provider if provider is not None else configured_provider()

        self._artifact = None

    def artifact(self):

        if self._artifact is None:
            self._artifact = load_artifact(self.config.model_dir)

        return self._artifact

    def process(self, payload, now=None, initial_error=None):

        now = now or utc_now()

        started = now.isoformat()

        run_id = "UE-" + uuid4().hex

        received = (
            len(payload.get("orders", []))
            if (isinstance(payload, dict) and isinstance(payload.get("orders"), list))
            else 0
        )

        result = {
            "run_id": run_id,
            "status": "DATA_FAILURE",
            "validation_status": "DATA_FAILURE",
            "routing_status": "DATA_FAILURE",
            "records_received": received,
            "source_batch_id": None,
            "predictions": [],
            "errors": [],
            "model_version": None,
            "threshold": None,
        }

        if isinstance(payload, dict) and isinstance(payload.get("source_batch_id"), str):
            candidate_id = payload["source_batch_id"]

            if re.fullmatch(r"[A-Za-z0-9_-]{1,100}", candidate_id):
                result["source_batch_id"] = candidate_id

        try:
            result["model_version"] = json.loads(
                (self.config.model_dir / "metadata.json").read_text()
            )["model_version"]

            result["threshold"] = json.loads(
                (self.config.model_dir / "threshold.json").read_text()
            )["probability_threshold"]

        except Exception:
            pass  # Explicit null when artifact/config is unavailable.

        batch, errors = validate_batch(payload, self.config, now)

        if initial_error:
            errors = [{"location": "source", "code": initial_error}]

            batch = None

        if errors:
            result["errors"] = errors

            result["briefing"] = {
                "text": "DATA FAILURE: input rejected; no operational all-clear.",
                "formatter": {"mode": "deterministic"},
            }

            result["approved_actions"] = [ACTION_CATALOG["CHECK_DATA"]]

        else:
            result["validation_status"] = "SUCCESS"

            result["source_batch_id"] = batch.source_batch_id

            try:
                pipeline, metadata, threshold = self.artifact()

                predictions = infer(batch, run_id, pipeline, metadata, threshold)

                metrics = current_metrics(predictions)

                groups = aggregate_hotspots(batch, predictions, self.config)

                packet = construct_evidence(
                    batch,
                    run_id,
                    utc_now().isoformat(),
                    metadata,
                    threshold,
                    metrics,
                    groups,
                    self.config,
                )

                briefing = generate_briefing(packet, self.provider)

                routing = "RED_ALERT" if any(g["is_hotspot"] for g in groups) else "GREEN_SUMMARY"

                result.update(
                    status="SUCCESS",
                    routing_status=routing,
                    predictions=predictions,
                    metrics=metrics,
                    hotspots=groups,
                    evidence=packet,
                    briefing=briefing,
                    model_version=metadata["model_version"],
                    threshold=threshold["probability_threshold"],
                )

                result["routing_reason"] = (
                    "supported predicted-risk hotspot"
                    if routing == "RED_ALERT"
                    else "no supported predicted-risk hotspot; not an all-metrics health claim"
                )

            except Exception:
                # Do not leak exception strings (provider errors can contain secrets).

                result["errors"] = [{"location": "runtime", "code": "runtime_processing_failed"}]

                result["approved_actions"] = [ACTION_CATALOG["CHECK_DATA"]]

                result["briefing"] = {
                    "text": "DATA FAILURE: runtime could not produce verified evidence.",
                    "formatter": {"mode": "deterministic"},
                }

        packet = result.get("evidence")

        if packet is None:
            packet = {
                "run_id": run_id,
                "source_batch_id": result["source_batch_id"],
                "source_sha256": canonical_hash(payload),
                "generated_at": started,
                "source_timestamp": None,
                "facts": [
                    {
                        "evidence_id": "FAILURE",
                        "errors": result["errors"],
                        "approved_action_ids": ["CHECK_DATA"],
                    }
                ],
                "approved_actions": [ACTION_CATALOG["CHECK_DATA"]],
            }

            result["evidence"] = packet

        packet.update(
            routing_status=result["routing_status"],
            records_received=received,
            records_scored=len(result["predictions"]),
            model_version=result["model_version"],
            threshold=result["threshold"],
            freshness_status="FRESH" if batch is not None else "REJECTED",
            source_timestamp=packet.get("source_timestamp", packet.get("source_generated_at")),
        )

        for fact in packet["facts"]:
            if "predicted_risk_rate" in fact:
                fact["predicted_risk_fraction"] = fact["predicted_risk_rate"]

        header = (
            "RED_ALERT - manual review required"
            if result["routing_status"] == "RED_ALERT"
            else "GREEN_SUMMARY - no supported predicted-risk hotspot detected"
            if result["routing_status"] == "GREEN_SUMMARY"
            else "DATA_FAILURE"
        )

        result["briefing"]["text"] = (
            header
            + "\n"
            + result["briefing"]["text"]
            + f"\nRun: {run_id}; batch: {result['source_batch_id']}; "
            f"records evaluated: {len(result['predictions'])}; model: {result['model_version']}; "
            "evidence: " + ", ".join(f["evidence_id"] for f in packet["facts"])
            + f" [evidence:{packet['facts'][0]['evidence_id']}]"
        )

        result["briefing"]["channels"] = channel_messages(result)

        try:
            persist_run(self.config.runs_dir, result, started, utc_now().isoformat())

        except Exception:
            # A successful response without an audit record violates the live contract.
            packet.update(
                status="DATA_FAILURE",
                routing_status="DATA_FAILURE",
                facts=[
                    {
                        "evidence_id": "FAILURE",
                        "error_code": "persistence_failed",
                        "approved_action_ids": ["CHECK_DATA"],
                    }
                ],
                approved_action_ids=["CHECK_DATA"],
                approved_actions=[ACTION_CATALOG["CHECK_DATA"]],
            )
            failed = dict(
                result,
                status="DATA_FAILURE",
                routing_status="DATA_FAILURE",
                errors=[{"location": "audit_log", "code": "persistence_failed"}],
                briefing={
                    "text": "DATA FAILURE: audit log unavailable.",
                    "formatter": {"mode": "deterministic"},
                },
            )
            failed["briefing"]["channels"] = channel_messages(failed)
            return failed

        return result


def create_app(config=None, provider=None):

    runtime = Runtime(config, provider)

    app = FastAPI(title="UrbanEats local runtime", version="0.2.0")

    app.state.runtime = runtime

    @app.get("/health")
    def health():

        try:
            _, metadata, _ = runtime.artifact()

            return {
                "status": "READY",
                "model_version": metadata["model_version"],
                "model_loaded": True,
                "threshold_loaded": True,
                "runtime_status": "READY",
            }

        except Exception:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "NOT_READY",
                    "model_loaded": False,
                    "threshold_loaded": False,
                    "model_version": None,
                    "runtime_status": "NOT_READY",
                },
            )

    @app.post("/process-batch")
    async def process_batch(request: Request):

        try:
            payload = await request.json()

        except Exception:
            payload = None

        # CPU work/log persistence stays off the event loop.

        from starlette.concurrency import run_in_threadpool

        return await run_in_threadpool(runtime.process, payload)

    @app.post("/process-current")
    def process_current():
        """Read the configured placement source afresh for each execution."""

        try:
            payload = json.loads(runtime.config.source_file.read_text(encoding="utf-8"))

        except Exception:
            return runtime.process(None, initial_error="source_unreadable_or_malformed")

        return runtime.process(payload)

    @app.post("/delivery")
    async def delivery(request: Request):

        try:
            body = await request.json()

            rid = body["run_id"]

            if not re.fullmatch(r"UE-[0-9a-f]{32}", rid):
                raise ValueError("invalid_run")

            stored = json.loads((runtime.config.runs_dir / f"{rid}.json").read_text())

            return delivery_event(
                runtime.config.runs_dir,
                stored["result"],
                body["channel"],
                body["operation"],
                body.get("outcome"),
                body.get("attempts", 0),
                body.get("error_category"),
            )

        except Exception:
            return JSONResponse(status_code=400, content={"error": "delivery_request_rejected"})

    return app


app = create_app()
