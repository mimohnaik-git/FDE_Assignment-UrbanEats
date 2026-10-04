import hashlib
from collections import defaultdict


def aggregate_hotspots(batch, predictions, config):
    grouped = defaultdict(list)
    for order, prediction in zip(batch.orders, predictions, strict=True):
        grouped[(order.restaurant_name, order.delivery_zone)].append(prediction)
    rows = []
    for (restaurant, zone), group in sorted(grouped.items()):
        count = sum(p["risk_flag"] for p in group)
        total = len(group)
        supported = total >= config.min_support
        key = hashlib.sha256(f"{restaurant}\0{zone}".encode()).hexdigest()[:16]
        rows.append({
            "evidence_id": f"HS-{key}",
            "restaurant": restaurant,
            "delivery_zone": zone,
            "high_risk_count": count,
            "total_count": total,
            "numerator": count,
            "denominator": total,
            "predicted_risk_rate": count / total,
            "predicted_risk_fraction": count / total,
            "sample_size": total,
            "source_order_ids": sorted(p["order_id"] for p in group),
            "support_status": "SUPPORTED" if supported else "INSUFFICIENT_SUPPORT",
            "is_hotspot": supported and count / total > config.hotspot_rate,
        })
    return rows
