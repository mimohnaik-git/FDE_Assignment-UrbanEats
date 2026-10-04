import math

from .features import feature_frame


def infer(batch, run_id, pipeline, metadata, threshold):
    probabilities = pipeline.predict_proba(feature_frame([
        order.model_dump() for order in batch.orders
    ]))[:, 1]
    if len(probabilities) != len(batch.orders) or any(
        not math.isfinite(float(p)) or not 0 <= p <= 1 for p in probabilities
    ):
        raise ValueError("Invalid model probabilities")
    return [
        {
            "order_id": order.order_id,
            "cancellation_probability": float(probability),
            "risk_flag": bool(probability >= threshold["probability_threshold"]),
            "model_version": metadata["model_version"],
            "run_id": run_id,
        }
        for order, probability in zip(batch.orders, probabilities, strict=True)
    ]
