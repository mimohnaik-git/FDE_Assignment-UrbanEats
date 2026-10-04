import math
from datetime import datetime, timezone

from pydantic import ValidationError

from .schemas import CurrentBatch


def utc_now():
    return datetime.now(timezone.utc)


def validate_batch(payload, config, now=None):
    """Fail closed; never expose submitted field values in error summaries."""
    now = now or utc_now()
    try:
        batch = CurrentBatch.model_validate(payload)
    except ValidationError as exc:
        return None, [
            {"location": ".".join(map(str, e["loc"])), "code": e["type"]}
            for e in exc.errors(include_input=False, include_url=False)
        ]
    errors = []
    if batch.generated_at.tzinfo is None:
        errors.append({"location": "generated_at", "code": "timezone_required"})
    else:
        age = (now - batch.generated_at).total_seconds()
        if age > config.max_age_seconds or age < -60:
            errors.append({"location": "generated_at", "code": "stale_or_future_batch"})
    ids = set()
    for i, order in enumerate(batch.orders):
        loc = f"orders.{i}"
        if order.order_id in ids:
            errors.append({"location": loc, "code": "duplicate_order_id"})
        ids.add(order.order_id)
        if not order.restaurant_name.strip() or order.restaurant_name != order.restaurant_name.strip():
            errors.append({"location": loc, "code": "invalid_restaurant_name"})
        if not all(math.isfinite(v) for v in [order.order_value, order.discount_applied]):
            errors.append({"location": loc, "code": "nonfinite_numeric"})
        if order.discount_applied > order.order_value:
            errors.append({"location": loc, "code": "discount_exceeds_value"})
        if order.placed_at.tzinfo is None:
            errors.append({"location": loc, "code": "timezone_required"})
        else:
            age = (now - order.placed_at).total_seconds()
            if age > config.max_age_seconds or age < -60:
                errors.append({"location": loc, "code": "stale_or_future_order"})
            if batch.generated_at.tzinfo and order.placed_at > batch.generated_at:
                errors.append({"location": loc, "code": "placement_after_snapshot"})
    return (None, errors) if errors else (batch, [])
