"""Only checkout snapshot fields enter the sklearn pipeline."""

CATEGORICAL = ["restaurant_name", "delivery_zone", "payment_method"]
NUMERIC = ["order_value", "discount_applied"]
FEATURES = CATEGORICAL + NUMERIC
PROHIBITED = {
    "order_status", "delivery_time_mins", "rider_rating", "customer_complaints",
    "cancel_probability", "cancel_risk", "cancellation_probability", "order_id", "target",
}
FEATURE_CONTRACT = {
    "version": "checkout-v1",
    "prediction_point": "placement after finalized checkout, before fulfillment",
    "features": FEATURES,
    "excluded": sorted(PROHIBITED),
    "target": "Cancelled=1, Delivered=0; conditional on these two terminal outcomes",
    "limitations": "Synthetic final export; no horizon/as-of snapshots; uncalibrated exploratory score",
    "currency": "INR",
    "discount_unit": "INR per original README; source owner must confirm before production",
    "calendar_features": "Omitted: small sample and no incremental justification",
}


def feature_frame(records):
    import pandas as pd

    return pd.DataFrame(records).loc[:, FEATURES]
