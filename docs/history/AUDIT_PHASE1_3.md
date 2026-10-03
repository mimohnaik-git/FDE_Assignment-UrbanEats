# Historical audit snapshot — superseded by current AUDIT.md

# Phase-3 audit outcome (2026-10-03)

Phase-2 tests: 34 passed. Evaluation reproduced the supplied weak holdout metrics.
Saved artifact loaded locally. Direct audit found missing deployment model path,
separate scaffold n8n volume, absent delivery claims/provider transport and sparse
readiness/failure evidence. Phase 3 adds explicit container paths, preserves external
n8n_data, a hosted adapter disabled in TEST_MODE, evidence-backed delivery claims,
inactive workflow and local verification. Docker and disposable n8n import/execution
passed; no existing n8n account/configuration changes. Infrastructure outage delivery remains a live-test readiness gap. Bounded rate-limit
retry loops use receipt verification and keep ambiguous sends suppressed. See docs/LIVE_AUTOMATION.md
and evaluation/results/phase3_verification.json. No sends, activation, commits or pushes.

---

# UrbanEats Phase 1 audit

## Phase-2 implementation addendum (2026-10-03)

The audit below is preserved as the baseline assessment. The rebuilt local runtime
now resolves placement-feature leakage (C2/H1), in-sample evaluation reporting (H2),
fail-open local routing (C1), unsupported hotspot actions (H4/H5), pipeline/evidence
provenance and runtime logging. Delivered/Cancelled target restrictions are explicit,
not claimed as general-population cancellation probabilities. Evaluation is weak and
does not establish production predictive readiness; see docs/EVALUATION.md.

C3 is partially resolved locally: configured current-source reread â†’ validation â†’
saved inference â†’ metrics/hotspots â†’ evidence â†’ provider stub/deterministic briefing â†’
logging is implemented. Scheduled Docker/n8n execution, actual hosted generation and
Slack/Gmail remain Phase 3 under the subsequent user's explicit prohibition on Phase-2
external calls. The original plan's hosted-demo timing is superseded by that request.

Current public workflow examples are sanitized. The legacy root workflow remains
inactive and retains its historical fail-open methodology; it is not the rebuilt
workflow. Its original unsanitized bytes remain preserved in assignment-baseline-v1,
not copied into new public artifacts. Historical Git/backup exposure still exists;
no history rewrite. Original notebooks, CSVs, alerts and brief remain unchanged.
The README now separates rebuilt status from retained original assignment narrative.

Audit date: 2026-10-03 (Asia/Calcutta). Scope: local inspection only; no notebook execution, model changes, external service calls, workflow activation, messages, commits, pushes, or history changes. All eight project artifacts were read, including notebook sources, serialized outputs/metadata, every CSV row, workflow parameters/connections, and all alerts. Backup files and ZIP entries were inspected read-only. Findings describe the assignment artifacts, not a deployed system.

## 1. repository inventory

Authoritative branch: `feat/urbaneats-ops-intelligence-rebuild`. HEAD: `c62430075fc5ccaaa5db487a7556d531ac128c63`. Annotated tag `assignment-baseline-v1` has tag-object ID `5334745d8e723577c8c969a5ce566940a323730d`; its peeled commit is the supplied baseline `c62430075fc5ccaaa5db487a7556d531ac128c63`. Initial working tree was clean. No applicable AGENTS.md was found in the workspace/checked ancestor directories.

| File | Bytes | Role / audit result |
|---|---:|---|
| README.md | 12112 | Assignment narrative and reproduction steps; misleading placement-time and live readiness claims |
| UrbanEats_classifier_langchain.ipynb | 56942 | 15 cells; model, full-data scoring, hosted LLM, exports; 12 stored outputs |
| UrbanEats_profiling_gx.ipynb | 121459 | 15 cells; profiling, imputation, six GX expectations, custom HTML; 20 stored outputs |
| UrbanEats_n8n_workflow.json | 14697 | Eight nodes; inactive; fetches precomputed CSV, computes KPIs, branches, Slack then Gmail |
| urbaneats_alerts.json | 7611 | 13 hotspots; aggregates agree with scored CSV; generated text differs from notebook outputs |
| urbaneats_delivery_orders.csv | 10491 | 150 rows, 11 columns, 150 unique non-null IDs |
| urbaneats_delivery_orders_scored.csv | 11930 | 150 rows, 13 columns; 49 high / 101 low; six delivery-time imputations |
| urbaneats_ops_brief.md | 1843 | Five-sentence narrative; unsupported readiness, causes, deployment and success claims |

These are all non-Git files present at audit start (all tracked). CSV IDs/order match exactly; apart from two new score fields, only the six missing delivery times differ. Raw data: Delivered 44, Cancelled 36, Refunded 37, Delayed 33; cancellation 36/150 = 24%; Cancelled + Refunded 73/150 = 48.7%. Delivery time and rider rating each have six nulls; all other columns have none. Observed ranges: order value 123â€“1800, discount 0â€“30, delivery time 16â€“90, rating 2â€“5, complaints 0â€“3. Parsed dates use DD-MM-YYYY, 2024-01-04 through 2024-12-28 (118 distinct dates); this is historical synthetic data, not a current feed.

Git internals were inventoried separately (36 files at inspection; app-generated capture refs may change): `.git/config`, `description`, `gk/config`, `HEAD`, `index`, `info/exclude`, `packed-refs`; 14 sample hooks (applypatch-msg, commit-msg, fsmonitor-watchman, post-update, pre-applypatch, pre-commit, pre-merge-commit, pre-push, pre-rebase, pre-receive, prepare-commit-msg, push-to-checkout, sendemail-validate, update); logs for HEAD, feature branch, main, origin/HEAD; loose tag object under `objects/53/`; commit-graph chain and graph; one pack with idx/pack/rev; refs for feature branch, main, origin/HEAD, baseline tag and one Codex turn capture. No Git internals were changed by audit scripts. New documentation is listed in section 15.

## 2. Critical findings

- **C1 â€” Invalid data can reach all-clear logic.** Workflow Code node accepts arbitrary object/string content without schema checks. Local isolated execution of the exact exported JavaScript: missing status column â†’ total 1, rate 0, `aboveThreshold=false`; multiline HTML â†’ total 1, rate 0, false; header-only â†’ total 0, NaN rate, false. The IF has only RED/GREEN routes and no validity guard. Actual n8n strict-type handling of NaN may throw; that does not provide DATA FAILURE reporting. Missing-schema numeric zero can directly satisfy the false branch. The supplied historical GREEN-email incident is consistent with this defect, but its execution log is not in the repository.
- **C2 â€” Placement-time risk uses unavailable outcome information.** Classifier cell 5 includes final `delivery_time_mins`; cell 3 imputes it from all 150 records. README defines this as minutes from order to delivery. Ops brief sentence 4 falsely claims placement-time features. Prediction is not defensible at the requested point.
- **C3 â€” Required live runtime does not exist.** n8n retrieves a historical pre-scored Drive CSV, never invokes a model, constructs no evidence packet, and makes no runtime LLM call. Its AI message is a constant. A schedule alone does not demonstrate current-data automation.

## 3. High findings

- **H1 â€” Preprocessing contaminates evaluation.** Full-data zone medians and categorical vocabularies are fitted before splitting, including test and excluded-status rows (classifier cell 3).
- **H2 â€” Training rows dominate aggregate risk evidence.** Scoring all 150 includes 64 fit rows, 16 held-out rows, and 70 excluded-status rows. These scores cannot be presented as held-out performance or fresh operational evidence.
- **H3 â€” Target population mismatch.** Model learns cancellation conditional on Delivered/Cancelled (36/80 = 45% prevalence), then scores Delayed/Refunded too and is described as general placement-time probability. Labels/horizons for those statuses are unresolved.
- **H4 â€” Unsupported prescriptions and causes.** LLM alerts recommend pricing/menu changes, confirmations, incentives or staffing without causal evidence. Workflow says deploy two riders within 24 hours without a staffing input. Classifier interpretation asserts a cancellation cycle triggered by time/discounts. Feature importance is not causation.
- **H5 â€” Small groups promoted as decisive.** Top hotspot is 3/4 flagged orders, not 75% observed cancellations. Pizza Palace/Central is 1/2. All 25 groups contain 1â€“10 orders. No uncertainty or adequate minimum support.
- **H6 â€” Data gate is disconnected.** GX validates a mutated dataframe and prints success; it does not stop model/notification execution. No raw ingestion gate, freshness checks, complete schema, timestamp contract, or production failure state.
- **H7 â€” Public export contains environment identifiers.** Recipient emails, Drive file ID, OAuth credential references, Slack channel ID, webhook IDs, instance ID and workflow metadata require sanitization in a future portable export. No verified embedded API key was detected.

## 4. Medium findings

- **M1 â€” Evaluation is too small and incomplete.** 64 training / 16 test; eight positives in stored test report. No CV, temporal holdout, dummy baseline, uncertainty, calibration, or threshold selection. No predictive value established.
- **M2 â€” Thresholds lack policy justification.** Model flag >=0.55; hotspot >0.30 on rounded rates; operational cancellation >0.20. They measure different things and have no documented decision cost/validation basis.
- **M3 â€” Fragile parser and KPI definitions.** Comma/newline splitting is not CSV-aware; quoted commas/newlines break it. Missing values silently become zero/N/A; no finite/range checks. Delivery average uses Delivered only but scored data includes imputed outcomes. Raw observed Delivered mean is 48.0238 (42 values); scored mean 48.3523 (44 values); workflow rounds to 48.4. Worst restaurant/zone rankings use counts without denominator exposure.
- **M4 â€” Missingness claims are unsupported.** Delivery nulls span statuses (Delayed 2, Delivered 2, Cancelled 1, Refunded 1); rating nulls are Delivered 3, Cancelled 2, Refunded 1. This does not establish MCAR/MNAR or prove structural missingness. No rider-assignment field supports the rider explanation.
- **M5 â€” Schedule and output contracts are incomplete.** Cron is 07:30 daily, export `active=false`, timezone absent. JS formats date in en-IN but does not set a timezone. Gmail follows Slack and uses `$json`; Slack response preservation is unverified, so downstream KPI loss is a concrete risk. Slack failure can prevent email.
- **M6 â€” Reproducibility and portability are unverified.** Colab `/content` paths, unpinned/upgraded installs, warning suppression, no model artifact/version, dataset/run manifests, tests, CLI or Docker definition. Community Edition import/node behavior has not been tested.
- **M7 â€” No coherent provenance.** Alert JSON text differs from stored generated notebook text; same numeric aggregate does not prove same generation run. No run ID/hash/model version/evidence IDs connect exports.

## 5. Low findings

- README uses incorrect classifier/workflow filenames and lists HTML artifacts absent from the authoritative checkout.
- Notebook output labels say first five rows while displaying ten; expectation heading says five while implementing six.
- GX HTML is hand-rendered from validation results, not the native GX Data Docs site. Its timestamp is not a dataset freshness guarantee.
- README's 22% quarterly rise, weather/festival/road-closure implications, tomorrow deployment, and four-week impact target lack supporting observations or execution evidence.

## 6. prediction point

Adopt **order placement, immediately after checkout fields are finalized**, before fulfillment/cancellation. This is the desired contract, not a proven source-system guarantee: the dataset is a final-state synthetic export with no as-of snapshots, event timestamps, cancellation timestamp/reason, or label-maturity field. Phase 2 must document checkout availability, immutable field meanings and an explicit cancellation horizon. Do not silently broaden to later-lifecycle features. Live scoring of newly placed orders and retrospective KPI reporting use separate data contracts/windows.

## 7. allowed feature set

| Field | Availability reasoning / required contract |
|---|---|
| restaurant_name | Restaurant selected at checkout; use placement snapshot, not reassignment |
| delivery_zone | Destination zone known at placement; freeze original zone |
| order_value | Checkout amount is known; confirm gross/net/refund semantics and immutability |
| payment_method | Selected checkout method; no later payment outcome/status |
| discount_applied | Checkout discount is known; README says INR but 0â€“30 values do not prove units; resolve before modeling |
| order_date-derived calendar features | Placement date is documented; strict DD-MM-YYYY parsing; day-of-week/month available, no hour features from date-only data |

Restaurant/zone/checkout values are provisional semantic approvals subject to a source contract. Current model uses only restaurant, zone, amount, discount plus prohibited time; payment/date are currently unused. `order_id` is provenance/join key, not a predictor.

## 8. excluded features + reasons

| Field | Reason |
|---|---|
| order_status | Final outcome/target source; would reveal outcome. Retain only in matured-label/KPI datasets |
| delivery_time_mins | Documented final elapsed order-to-delivery time, unavailable at placement; even a filled value depends on later outcomes. Not a promised ETA |
| rider_rating | Customer evaluation after rider service; no placement-time rating semantics |
| customer_complaints | Tickets accumulated for this order; no as-of timestamp means future complaints can leak |
| order_id | Identifier; retain for lineage/deduplication only |
| cancel_probability, cancel_risk, target | Derived predictions/labels, never new model inputs |

Outcome fields may support retrospective KPIs when measured, sufficiently complete and timestamped. Prior-history aggregates would need a strictly earlier cutoff and adequate history; none is approved from this dataset.

## 9. ML leakage/evaluation findings

Classifier cells 3â€“6: full-data zone-median imputation and LabelEncoder fitting; 80 Delivered/Cancelled records; random, non-stratified 80/20 split with seed 42; 100-tree RF seed 42. Nominal LabelEncoder integers impose artificial ordering; train-fold OneHotEncoder with explicit unknown-category behavior is preferable. Full vocabulary fitting is test-set knowledge, although less severe than outcome-feature leakage.

Stored test results: precision .600, recall .375, F1 .462, accuracy .5625; derived confusion counts TP=3, FP=2, FN=5, TN=6. These are notebook records, not an audit rerun. Each cancelled test order changes recall by 12.5 percentage points. `rf.predict` evaluation uses the estimator decision rule, whereas deployment flags >=.55. No threshold-specific validation, calibrated probabilities, ROC/PR curves, Brier/log loss, CV or confidence intervals. Score rounding precedes thresholding; aggregate rounding precedes hotspot selection.

150 synthetic historical rows, only 80 included labels, cannot establish generalization to live orders. Train-only preprocessing, leakage-safe labels, dummy/logistic baselines, stratified CV where viable, a temporal evaluation aligned with live placement, held-out/OOF-only retrospective scoring and separately marked live inference are needed. Calibration must be evaluated on independent folds and may be unjustified with this sample size. No forced calibration claim. Freeze thresholds before final holdout, report sample counts and uncertainty, and retain a weak-model outcome if baselines are not beaten. The current risk flag reduction target is susceptible to model/threshold changes and does not prove actual cancellation reduction.

## 10. LLM grounding findings

Classifier cells 11â€“12 supply exactly restaurant, zone, rounded high-risk percentage, mean order value and mean imputed delivery time. Although `total_orders` is exported, it is not supplied to the prompt. No numerator, observed cancellation rate, complaints, staffing, prep times, inventory, menu/price evidence, evidence identifiers, citations, period or uncertainty is supplied. LCEL invokes Groq for each hotspot. Missing key initialization catches errors but later cells still call `chain`; no robust no-key path. Quality checks in cell 13 examine only the first three alerts for name/action words/no hedging, not factual accuracy, causal support or citations.

Treat language as generation, not evidence. A deterministic evidence packet must contain schema version, source dataset/checksum, source window/as-of time, run ID, model/version and scoring mode, prediction point, quality/freshness status, thresholds/policy version, KPI denominators/missing counts and per-aggregation source_order_ids or aggregation_id, restaurant, delivery_zone, numerator, denominator, measured_rate, metric_kind, threshold, sample_size, uncertainty and generated_at. Store the actual membership manifest behind aggregation IDs. Distinguish flagged fraction from measured cancellation rate.

Pipeline-generated IDs such as `run_id:aggregation_id:metric` resolve to stored facts. Actions come from an approved deterministic mapping (e.g., investigate cancellation reasons for a supported threshold breach), not model-invented causes, quantities or promises. LLM receives only approved evidence/actions, formats them, and returns constrained structured references. Validate referenced IDs/numbers/action IDs; render citations deterministically from validated IDs. Reject unsupported content and use deterministic formatting. Hosted LLM remains optional for operation, but Phase-2 demonstration with configured credentials MUST exercise runtime generation and log evidence/prompt/output lineage. No hosted calls occurred in this audit.

## 11. n8n findings

Eight nodes, standard base node types: scheduleTrigger 1.2, httpRequest 4.2, code 2, if 2.2, gmail 2.1, slack 2.3. Settings include executionOrder v1 and binaryMode separate; no timezone; empty pinData; inactive export. Actual graph: Schedule â†’ Drive fetch â†’ JS KPI â†’ IF â†’ Slack RED/GREEN â†’ corresponding Gmail. It never consumes alerts JSON despite the notebook save comment. Hard-coded AI text is disconnected from computed top pair/current run. Public Drive response may be HTML, malformed or stale; no source timestamp/hash/content-type or observation-window check. Minimum pair support is only two. The GREEN text claims all metrics are in range although only cancellation is compared.

Local exported-code checks used Node in isolation with synthetic inputs; neither n8n nor external services were run. Valid scored CSV gives 150, .24, RED predicate true, delivery 48.4. Invalid-content results are in C1. Node response formats and strict IF behavior require an actual Community Edition integration test in Phase 2; do not claim the historical email reproduced end-to-end.

Required replacement runtime: scheduled trigger â†’ fetch current unscored/as-of input â†’ validate source and schema â†’ DATA FAILURE on any invalid/missing mandatory data â†’ saved validated model inference â†’ current, defined-window KPIs/hotspots with minimum support â†’ evidence packet â†’ approved action mapping â†’ runtime hosted LLM when configured â†’ validated deterministic citations â†’ Slack/Gmail â†’ execution/delivery logging. Explicit Asia/Kolkata timezone; immutable run payload survives each notification node. Independently track channel delivery/retries/idempotency so one channel does not silently block the other. An ingestion/provider failure must never reuse stale output as a GREEN run.

Community Edition Docker should orchestrate a small local Python runtime service over the internal Compose network (no arbitrary shell execution or Python installation inside n8n). Public workflow references configured local service and locally bound credentials, omits environment-specific IDs, starts inactive, and is demonstrably importable/runnable. A current fixture provider can support a reproducible demonstration, but must be visibly synthetic and updated per run; it cannot be represented as a real UrbanEats production source. Deployment versions/response contracts remain to be validated locally in Phase 2.

## 12. security findings

Local pattern scan covered all current project text, complete notebook JSON including rich outputs, backup HTML/notebooks/workflow and every ZIP file without extraction. Reachable Git revisions were scanned for common provider key/token/private-key patterns and email exposure. No concrete Groq/OpenAI/Slack/Google key or private key candidate was found; `GROQ_API_KEY` references are secret lookup instructions, not keys. This is a bounded pattern scan, not proof of absence or credential revocation. Do not print or copy identifier values into audit reports.

| Type | Location | Remediation in Phase 2 |
|---|---|---|
| Recipient email (2 occurrences) | workflow Gmail sendTo; current export lines 88/112; also backup/ZIP and three reachable historical revisions | Parameterize local recipients; remove from new public template; assess consent/exposure |
| Public Drive file ID | HTTP node parameters.url, line 26; backup/ZIP | Replace public static source with configured current ingestion; inspect/restrict sharing locally |
| OAuth credential IDs/names | Four Gmail/Slack nodes credentials | Remove exported references, bind credentials locally; IDs are references, not OAuth tokens |
| Slack channel ID/cache metadata | Both Slack channelId fields | Parameterize local destination; omit cache metadata |
| webhook IDs | Four notification nodes webhookId, lines 101/125/155/184 | Remove environment IDs from portable export; no evidence these are usable webhook secrets |
| instance ID | workflow meta.instanceId, line 276 | Remove instance metadata |
| workflow/node/version identifiers | workflow id/versionId and node ids | Remove unnecessary instance linkage; keep regenerated graph identifiers where import requires them |
| Colab execution/widget metadata and output tables | Both notebook metadata/outputs | Preserve originals as history; future public executable references should minimize metadata and review outputs |

Historical email exposure persists in Git; a sanitized new export does not erase history. No history rewriting is authorized. If an actual credential is later found, rotate/revoke it locally, then decide historical remediation explicitly. Do not distribute the backup ZIP before sanitization review. No files containing secret values were generated by this audit.

## 13. backup-only artifact assessment

Read-only backup: `../Assignment-UrbanEats_PRE_RECONCILE_20261003_162916`. Exactly three backup-only top-level files:

| Artifact | Bytes | Retention recommendation |
|---|---:|---|
| urbaneats_gx_data_docs.html | 4830 | Retain later as dated historical assignment evidence with caveats: custom report, post-imputation validation, erroneous structural-null claims. Run timestamp 2026-06-14 07:07:41 (timezone absent), 150 rows, six passes |
| urbaneats_operations_audit.html | 1905191 | Retain later as historical raw profiling evidence, not live/current readiness. Contains embedded scripts (two script tags); review public content/assets before publication |
| UrbanEats Assignment.zip | 589566 | Preserve private archival bundle; avoid duplicate public release with environment identifiers and conflicting narrative. Optional checksum manifest/reference after sanitization decision |

ZIP inspected in memory, not extracted: directory UrbanEats/ plus alerts JSON, classifier notebook, raw/scored CSV, GX HTML, workflow JSON, profile HTML, ops brief and profiling notebook. No README in ZIP. Backup CSVs are byte-identical to current; six other shared project files differ (README, alerts, both notebooks, workflow, brief), partly consistent with serialization/encoding differences. They are not interchangeable canonical copies. No backup artifacts were copied or modified.

## 14. proposed repository tree

```text
UrbanEats/
  README.md
  AUDIT.md
  pyproject.toml                 # create only after runtime/dependency decisions
  requirements.txt
  requirements-dev.txt
  .gitignore
  .env.example                  # names/placeholders only
  src/urbaneats/
    ingestion.py                # current provider, timestamps and checksum
    contracts.py
    validation.py
    features.py
    inference.py                # saved pipeline, placement-only inputs
    metrics.py
    evidence.py
    actions.py
    llm_formatter.py
    briefing.py
    service.py                  # internal Docker runtime API
    run_logging.py
  data/
    reference/                  # preserved assignment CSVs
    fixtures/                   # explicit current synthetic demo provider
  evaluation/
    train.py
    evaluate.py
    reports/
    model_card.md
  tests/
    test_validation.py
    test_feature_availability.py
    test_evidence.py
    test_runtime.py
    test_workflow_contract.py
  workflows/n8n/
    urbaneats_live.json          # clean Community Edition export
  docker/
    compose.yaml
    runtime.Dockerfile
  docs/
    REMEDIATION_PLAN.md
    source_contract.md
    runtime.md
    actions_policy.md
    historical_evidence/        # only reviewed artifacts, later
  notebooks/original/           # original notebook references, preserved history
  artifacts/models/             # versioned manifests; large/local files ignored
  generated/runs/<run_id>/      # inputs manifest, validation, scores, evidence,
                               # briefing, LLM lineage, delivery/execution log
```

This is a proposal, not a file migration. Original baseline remains accessible through Git/tag; preservation/moves in Phase 2 must be explicit and reviewed. Runtime outputs with sensitive input/destinations are ignored; curated sanitized example runs can be retained for portfolio evidence. No LangGraph, RAG/vector store, Kubernetes, agent orchestration or decorative cloud infrastructure is justified.

## 15. files created/modified

Created `AUDIT.md` and `docs/REMEDIATION_PLAN.md` only. Existing project artifacts remain unchanged. Audit helper scripts were placed in OS temporary storage, outside the repository; no credentials/identifier values were written to reports. No dependency/config scaffolding is justified before agreeing source/label/runtime contracts. No commit or push.

## 16. Phase-2 implementation plan

See `docs/REMEDIATION_PLAN.md`: preserve provenance; establish current source and placement/label contracts; implement fail-closed ingestion; evaluate and persist a leakage-safe pipeline; implement runtime inference/current KPIs/evidence/action mapping; add optional hosted runtime formatting with verified citations; build and verify portable Community Edition Docker workflow; record live execution proof and failure paths. Offline work validates components consumed by this live path and is not the primary product.

## 17. recommendation

**READY FOR PHASE 2** â€” ready to begin the remediation implementation described here, not ready for deployment or portfolio claims of a validated live system. Phase-2 source/label contracts and acceptance gates must be resolved before claiming model performance or live success. Existing artifacts cannot demonstrate the required runtime.
