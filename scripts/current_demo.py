"""Create a fresh, clearly synthetic placement batch locally; never re-date outcomes."""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def demo_batch(count=24):
    now = datetime.now(timezone.utc)
    return {
        "schema_version": "placement-v1", "source_batch_id": "demo-" + now.strftime("%Y%m%dT%H%M%S%f"),
        "source_dataset": "synthetic-placement-demo", "source_mode": "synthetic_demo",
        "generated_at": now.isoformat(), "target_population": "Delivered_vs_Cancelled_conditional",
        "orders": [{
            "order_id": f"demo-{i:03}", "placed_at": (now - timedelta(minutes=2)).isoformat(),
            "restaurant_name": "Wrap & Roll", "delivery_zone": "Central",
            "order_value": 500 + 10 * i, "payment_method": "UPI", "discount_applied": 10,
        } for i in range(count)],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/current_batch.json")
    parser.add_argument("--scenario", choices=["red", "green", "failure"], default="red")
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps({} if args.scenario == "failure" else demo_batch(4 if args.scenario == "green" else 24), indent=2), encoding="utf-8")
