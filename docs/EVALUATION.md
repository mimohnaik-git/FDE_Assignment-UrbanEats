# Rebuilt measured model results

Original assignment metrics are historical and use unavailable final delivery time.
The rebuilt model uses five checkout-only fields; no outcome predictor. Raw dataset
hash and exact row/fold membership are recorded in evaluation/results/metrics.json.

Population: 80 synthetic labels (44 Delivered, 36 Cancelled). Exclude 33 Delayed and
37 Refunded. Stratified 75/25 split seed 42: 60 development (27 positive), 20 holdout
(9 positive). Development uses four-fold stratified CV repeated five times; each
record's probability averages five predictions from models that excluded that record.
All transforms are fitted inside each fold. Model/threshold selection never sees
holdout. This random protocol does not establish temporal generalization.

| Candidate | Development OOF ROC-AUC | OOF average precision (PR-AUC definition) | OOF F1 at .50 |
|---|---:|---:|---:|
| Dummy prior | .4024 | .4234 | .0000 |
| Logistic regression | .5690 | .4831 | .4706 |
| Random forest (200 trees, minimum leaf 3) | .5657 | .4803 | .4167 |

Logistic regression selected by development OOF average precision, not accuracy.
The tiny difference versus forest does not establish superiority. Dummy OOF priors
vary with fold label composition, explaining its below-.5 discrimination; the
independent holdout dummy has constant prior score and ROC-AUC .5.

Probability threshold candidates .10–.90 in .05 increments are measured on development
OOF scores. Provisional investigation policy: cost of a missed cancellation=2, false
review=1; minimize 2FN+FP, ties choose fewer reviews then higher threshold. This is a
documented demo policy, not a stakeholder-approved economic cost.

Selected **.30**: development TP24/FP21/FN3/TN12, precision .5333, recall .8889,
F1 .6667; flags 45/60 (75% burden), cost27. At .50 it flags 24/60, misses15 positives,
cost42. Higher recall is bought with substantially more manual review. Development
selection results are optimistic; they are not independent validation.

Untouched holdout after choices are frozen:

| Metric | Logistic .30 | Dummy prior at .30 |
|---|---:|---:|
| Precision | .4167 | .4500 |
| Recall | .5556 | 1.0000 |
| F1 | .4762 | .6207 |
| ROC-AUC | .4545 | .5000 |
| Average precision | .5613 | .4500 |
| Brier score (lower better) | .3109 | .2475 |
| TP / FP / FN / TN | 5 / 7 / 4 / 4 | 9 / 11 / 0 / 0 |
| Review burden | 12/20 | 20/20 |
| 2FN+FP | 15 | 11 |

The holdout does not validate a reliable predictive model: logistic performs worse
than the prior baseline on F1, ROC-AUC, Brier and provisional cost, though average
precision is higher and burden lower. Nine positives mean each missed positive changes
recall by 11.1 percentage points. No production-quality, causal or calibration claim.
More representative matured data and independent evaluation are required before real
interventions. Do not tune to this holdout now that its results have been observed.

After evaluation, the selected pipeline is refitted on all 80 approved labels and
persisted for exploratory live inference. That final artifact has no independent
holdout left; the reported holdout assessed the development-fitted pipeline.
Model metadata explicitly has production_ready=false. Runtime never retrains and
checks model/config digests, feature contract and ML dependency versions on load.
Structured evidence/briefs retain this conditional uncalibrated-model limitation.
