import hashlib
import json

from .actions import ACTION_CATALOG, approved_actions


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def construct_evidence(batch, run_id, generated_at, metadata, threshold, metrics, groups, config):
    action_ids = approved_actions(groups)
    facts = [{
        "evidence_id": "KPI-BATCH", "numerator": metrics["high_risk_count"],
        "denominator": metrics["records_evaluated"],
        "predicted_risk_rate": metrics["predicted_risk_rate"],
        "sample_size": metrics["records_evaluated"],
        "source_order_ids": sorted(o.order_id for o in batch.orders),
        "metric_kind": "model_flagged_fraction", "approved_action_ids": [],
    }]
    facts += [dict(g, metric_kind="model_flagged_fraction", approved_action_ids=(
        ["MANUAL_REVIEW"] if g["is_hotspot"] else []
    )) for g in groups]
    return {
        "schema_version": "evidence-v1", "run_id": run_id,
        "routing_status": "RED_ALERT" if any(g["is_hotspot"] for g in groups) else "GREEN_SUMMARY",
        "source_timestamp": batch.generated_at.isoformat(),
        "freshness_status": "FRESH", "records_received": len(batch.orders),
        "records_scored": len(batch.orders),
        "source_dataset": batch.source_dataset, "source_batch_id": batch.source_batch_id,
        "source_mode": batch.source_mode, "source_generated_at": batch.generated_at.isoformat(),
        "source_sha256": canonical_hash(batch.model_dump(mode="json")),
        "generated_at": generated_at, "model_version": metadata["model_version"],
        "threshold": threshold["probability_threshold"],
        "hotspot_rate_threshold": config.hotspot_rate, "minimum_support": config.min_support,
        "records_evaluated": len(batch.orders), "status": "SUCCESS",
        "target_population": batch.target_population,
        "scoring_mode": "current_placement_inference",
        "model_claim": "exploratory, uncalibrated, conditional target; no production-quality claim",
        "metrics": metrics, "facts": facts,
        "approved_action_ids": action_ids,
        "approved_actions": [ACTION_CATALOG[a] for a in action_ids],
    }
