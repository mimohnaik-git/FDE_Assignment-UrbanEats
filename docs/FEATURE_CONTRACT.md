# Placement and target contract

Prediction occurs after checkout is finalized and before fulfillment. Only restaurant,
delivery zone, gross checkout order value (INR), selected payment method and checkout
discount (INR under the original README convention) enter the pipeline. Source owners
must verify immutable snapshots and discount units before production integration.
No calendar features are added without incremental evidence on this small sample.

Order ID is lineage only. placed_at and generated_at enforce freshness, not prediction.
Outcome/status, final delivery time, rating, complaints and prior score fields are
rejected from the placement API. Date-only assignment input is parsed only for historical
reference; live input requires timezone-aware ISO timestamps.

Supervised target remains **Cancelled=1 versus Delivered=0**, n=80 (36/44).
Delayed (33) and Refunded (37) are excluded from training/evaluation and are not recoded.
The model estimates a conditional terminal-outcome distinction; it does not establish
overall cancellation probability for all newly placed orders. New placement batches
must acknowledge `Delivered_vs_Cancelled_conditional`; their unknown final outcomes
do not magically establish eligibility. Scores are exploratory conditional estimates.
There are no labelled Delayed/Refunded predictions or equivalent-interpretation claims.

The assignment has no cancellation timestamps, maturity horizon, reasons or actual
placement snapshots. No fixed-horizon risk or temporal-generalization claim is valid.
A production source must supply matured labels with an explicit horizon and confirm
whether this conditional target is appropriate. Do not change the target just to improve
reported scores. This is a limitation of the model, not a reason to redesign the project
as offline analytics.

Inference loads a trusted local saved sklearn pipeline and never fits/retrains. The
pipeline fits OneHotEncoder(handle_unknown="ignore"), numeric imputation/scaling and
categorical imputation only on training folds. Novel restaurants are permitted and
encoded as unknown; zones and payment methods use a closed domain. Request numbers
must be finite JSON numbers, not numeric strings/bools. Source validation rejects
missing fields, duplicates, nonpositive value, invalid discount, naive/future/stale
timestamps and unknown extra fields. The default source and placement maximum age is
one hour with at most 60 seconds clock skew; placement cannot follow source snapshot.

Schema: `placement-v1`, source_batch_id, source_dataset, source_mode, generated_at,
target_population, orders[]. Each order: order_id, placed_at, restaurant_name,
delivery_zone, order_value, payment_method, discount_applied. Fresh batch generation
does not refresh stale placement timestamps. Source mode is synthetic_demo or
configured_source; the caller is trusted on this local boundary. Phase 3 needs provider
authentication and provenance rather than trusting caller assertions of a real source.

Hotspot support defaults to 20 unique current records per restaurant/zone, enforced
as a minimum floor. A supported group's unrounded flagged fraction must exceed 30%.
These are demo review-policy settings, not empirically proven operational cutoffs.
Groups below 20 remain explicit INSUFFICIENT_SUPPORT evidence and trigger no action.
GREEN_SUMMARY means no supported predicted-risk hotspot, never observed cancellation
health or all metrics within range. Placement input has no observed outcome metrics;
observed_cancellation_rate is null with an explicit unavailable explanation.

The probability threshold is selected from development OOF measurements and saved
in artifacts/model/threshold.json. Rates and inference comparisons use unrounded values.
Model scores are not calibrated; outputs named cancellation_probability must be read
with that limitation. No production-quality predictive claim is made.
