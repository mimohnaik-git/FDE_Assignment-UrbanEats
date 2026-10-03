# Historical snapshot — not current operating instructions

Preserved before Phase 3B.1 reconciliation. Use [current runtime](../RUNTIME.md) and
[current automation](../LIVE_AUTOMATION.md). Commands, counts and filenames below describe
their historical phases; they are not active implementation guidance.

# Phase 3 live integration (2026-10-03)

Local API/provider/delivery architecture and sanitized inactive workflow are implemented.
TEST_MODE defaults true; no external LLM calls, Slack/Gmail sends or workflow activation.
Docker config/build/health/API routes and disposable n8n 2.41.6 import/all three routes
passed. **NOT READY FOR LIVE CREDENTIAL TEST** until infrastructure failure notification
handling is completed. Bounded retries cover definite rate-limit rejections; ambiguous
delivery outcomes remain suppressed for manual reconciliation.
See [live automation setup](../LIVE_AUTOMATION.md) for exact commands, credentials, tests, retries and preservation strategy.
Model remains exploratory: precision .4167, recall .5556, F1 .4762, ROC-AUC .4545,
AP .5613, TN/FP/FN/TP 4/7/4/5; production_ready=false. RED is manual review only.
GREEN means no supported predicted-risk hotspot detected.

The Phase-2/historical sections below record earlier implementation status; the Phase-3
setup above supersedes their Docker, provider, logging and idempotency statements.

---

# UrbanEats Phase-2 implementation plan

Status: Phase-2 core implementation completed locally; external integration deferred
to Phase 3. The user's Phase-2 request supersedes the hosted-demo timing in the original
plan below: no hosted/paid LLM calls, Slack/Gmail activation or container/workflow
activation occur in Phase 2. The non-negotiable final deliverable remains a live system
on n8n Community Edition Docker after local credential configuration.

## Implementation status

- Implemented src runtime modules, strict placement schema/freshness gate, saved
  checkout-only sklearn pipeline, current metrics/support suppression, evidence/actions,
  citations, formatter interface/stubs/fallback, API and atomic per-run JSON logging.
- Evaluated logistic/forest/prior with repeated development OOF selection and separate
  holdout; selected logistic at .30. Weak holdout results explicitly documented in
  docs/EVALUATION.md; final artifact is exploratory and refits the 80 restricted labels.
- Local HTTP validation/inference/evidence/logging path is demonstrated with current
  synthetic input. Tests verify failures cannot route GREEN, safe formatting and lineage.
- Docker/CE n8n are inactive scaffolding only. Source is a configured local current
  JSON file, not a connected genuine UrbanEats provider. Outcomes are not supplied as
  inference inputs; observed cancellation metrics are explicitly unavailable.
- Sanitized legacy root workflow identifiers while preserving original baseline Git
  content/history. Original CSVs/notebooks/alerts/brief remain unchanged.
- Phase 3 must implement/test schedule + provider ingestion + actual hosted formatter
  + independent Slack/Gmail delivery + logging/retry/idempotency on pinned CE Docker.
  Do not use the original workflow's methodology or static scored CSV.

## Phase-3 acceptance gates

1. Verify pinned Docker/CE versions and import the clean workflow locally; resolve
   missing current source/model and every invalid-input/transport failure to DATA_FAILURE.
2. Configure authenticated current-source adapter and explicit source/label-maturity
   contracts. Keep synthetic demos visibly distinct; verify checkout amount/discount units.
3. Implement hosted transport with bounded timeout/retry, redacted generation lineage
   and structured factual validation. Demonstrate real generation only when authorized
   and locally configured; deterministic fallback remains mandatory.
4. Add separately handled Slack/Gmail branches referencing the immutable runtime
   result across node responses; local credentials only. Log receipts/failures, handle
   deduplication/retries and channel-specific failures without asserting success falsely.
5. Capture a scheduled current run proving the complete runtime under one run ID,
   plus input-change/failure/fallback demonstrations. This proves integration, not
   production model quality; retain exploratory labeling until predictive evidence improves.
6. Re-scan current public exports, decide treatment of historical identifier exposure,
   and document local state retention/authentication. No history changes or sends are
   implicitly authorized by this document.

## Original Phase-1 implementation proposal (historical)

## Runtime acceptance contract

`scheduled trigger → current data ingestion → validation → live model inference → current KPI/hotspot calculation → evidence construction → runtime LLM generation → Slack/Gmail notification → execution logging`

The configured hosted mode must demonstrate every stage during a scheduled run. The system must also function with no hosted credentials using deterministic formatting; record formatter mode, fallback/failure reason and provider status explicitly. LLM failure is not DATA FAILURE if validated evidence exists, but no generation failure may be concealed as a hosted success. Invalid/missing/stale source data always yields DATA FAILURE, never GREEN, and stops inference/operational all-clear. Provider credentials and destinations remain local.

## 1. Preserve assignment history and resolve contracts

- Verify baseline/tag, record original checksums, preserve original references. Do not copy/replace backup artifacts until retention and public sanitization decisions are made. Do not rewrite history.
- Document placement-only feature snapshots and gross/net amount/discount units. Date parsing is DD-MM-YYYY; date-only input cannot support hourly features.
- Define cancellation horizon, terminal label maturity, refund treatment and unresolved Delayed outcomes. Separate new/open-order scoring from matured outcome KPI data. Either acquire appropriate matured labels for the target population or explicitly restrict the model claim; do not treat Delayed/Refunded as unexplained negatives or universally valid predictions.
- Configure a current source adapter with source timestamp, watermark/window and content checksum. Historical assignment data is reference only. A fixture adapter generates/serves explicitly synthetic current inputs for reproducible demos and records its mode. A genuine production-source claim requires a genuine connected provider and observed live data.

Acceptance: contracts explain field availability, target population, latency/horizon, source identity/freshness, empty-window semantics and KPI denominators.

## 2. Fail-closed data gate

Validate content type/format, schema version, required columns, types, finite numbers, categorical policy, unique IDs, timestamps/timezone, freshness, window bounds, ranges and required-field missingness before transformation. Preserve raw input/missingness; do not fill final outcomes to make operational KPIs appear complete. Outcome nullability follows lifecycle, separately from placement-input requirements. Required KPI absence fails the run; optional unavailable KPIs are explicitly unavailable, not zero. An empty input window is non-GREEN unless a verified no-orders policy is defined.

Acceptance: missing headers/status, malformed/HTML/empty input, duplicated IDs, NaN/infinity, impossible timestamps, stale data and failed source fetch produce structured DATA FAILURE with logged reasons. No notification template asserts health for invalid runs. Boundary tests define exactly 20% and no-supported-hotspot behavior.

## 3. Train/evaluate the runtime pipeline

Use approved placement columns only. Split before fitting all transformations; one persisted sklearn Pipeline/ColumnTransformer with train-fold imputation and nominal encoding handles unknown categories explicitly. Compare simple baselines and models; use stratified folds where viable and time-aware holdout for the deployment question. Exclude unresolved labels. Document random seeds, runtime dependencies, feature/schema versions and source hashes.

Use held-out/OOF predictions for retrospective evaluation and aggregation; tag scoring mode. Report positive/support counts, confusion matrix, threshold-specific precision/recall/F1, PR/ROC metrics where meaningful, Brier/reliability and uncertainty. Calibration requires adequate independent data; a small sample may support only exploratory results. Select threshold by explicit operational cost/capacity policy within training folds, then freeze it for holdout. A model failing baselines is recorded as such; do not manufacture a positive portfolio result.

Acceptance: outcome fields never enter preprocessing or inference; held-out data never fits transforms; persisted artifact used by service matches evaluated model/feature versions. New inference does not retrain on current outcomes. Artifact checksum/version and train cutoff are logged.

## 4. Build current runtime evidence and actions

Implement local Python service under Docker Compose. n8n passes a run ID/window to the runtime; runtime ingests and validates current input, loads the saved model, scores eligible current orders, computes current measured KPIs from properly matured/observed outcome data, aggregates flagged fractions with numerator/denominator/minimum support, and stores immutable evidence.

Minimum support must be an explicit configurable policy validated against sample availability (a provisional demo default such as 20 means none of the current 1–10-row groups qualifies). Suppressed/insufficient-support groups are visible, never promoted as reliable hotspots. Rate comparisons use unrounded numbers; rounding is display only. Clearly label measured cancellation rate versus model-flagged fraction. Avoid ranking counts as rates.

Evidence schema includes `source_dataset`, checksum/window/as-of, `source_order_ids` or membership-backed `aggregation_id`, `run_id`, restaurant, delivery_zone, numerator, denominator, measured_rate, metric_kind, threshold, sample_size, uncertainty, generated_at, quality/freshness, model/scoring mode and policy versions. Reject invalid ratios/missing lineage. Action mapping supplies approved investigation/escalation steps by evidence type and support; it never invents root causes, staffing counts or promised effects.

Acceptance: every briefing fact resolves to immutable current-run evidence; replay reproduces metrics/citations; fresh source changes are reflected in inference and aggregation.

## 5. Add runtime LLM formatting and deterministic citations

Hosted provider is configurable and optional. During the live hosted demonstration, call it after evidence construction on that run, with minimal approved evidence/actions and a constrained response schema. Use timeouts and bounded retries; store redacted request/response lineage, model, timestamps and generation status. Validate numeric claims, metric type, reference IDs and action IDs; reject novel unsupported instructions. Pipeline renders citations by looking up validated IDs; LLM does not invent provenance. If provider is absent/unavailable or output validation fails, use deterministic brief and log fallback. Escape notification HTML/text.

Acceptance: unsupported menus/pricing/staffing, altered rates, fake citations and prompt injection from source text are rejected. Configured hosted path records a real runtime call; fallback path has no dependency on credentials/network and is visibly labeled.

## 6. Portable n8n Community Edition Docker automation

Compose contains n8n plus the Python runtime service and persistent local run state. Pin versions when verified. Internal HTTP API avoids shell/code-execution privileges inside n8n. Set workflow and runtime timezone explicitly to Asia/Kolkata; preserve UTC timestamp storage. Import a public, inactive workflow with placeholders/config expressions and no personal emails, Drive/channel/credential/webhook/instance IDs. Document local credential binding, source provider setup, LLM setup, recipients, schedule enablement and artifact mounting. No cloud-only nodes/services are required.

Workflow controls run initialization, runtime call, explicit DATA FAILURE / valid alert / valid within-policy branches, formatter status, Slack and Gmail delivery and execution records. Preserve immutable evidence/KPI payload across provider responses; independently handle each notification, log delivery outcome and retry state, and use run/channel idempotency to prevent duplicate sends. Notification failure remains visible even if the other channel succeeds. Do not overwrite a failed run with the last good output.

Acceptance: fresh CE Docker environment imports and runs after local configuration; invalid input routes to DATA FAILURE; Slack/Gmail response objects cannot erase KPIs; credentials and outputs survive intended container restarts securely. Exact node/API parameter behavior is verified against the installed version.

## 7. Demonstrate and document live behavior

With Phase-2 execution authorization and user-configured credentials/destinations, capture a real scheduled run with current input manifest, validation, live model inference artifact identity, KPI/hotspot/evidence, hosted runtime LLM request/output validation, actual Slack/Gmail delivery receipts and execution log. Preserve a sanitized portfolio execution record. A manual test run is useful but does not replace scheduled-trigger proof. Change current input between runs to demonstrate freshness; separately show data failure, insufficient support, hosted-provider fallback, notification failure and idempotent retry. No external calls or notifications are authorized by this Phase-1 plan itself.

Acceptance: end-to-end execution record links each stage to the same run ID; public export contains no environment identifiers/secrets; docs distinguish synthetic demonstration from production operations, historic assignment results from leakage-safe evaluation, and validated runtime capabilities from model limitations. Measure actual cancellation outcomes over defined matured windows for intervention monitoring; a declining model-flag fraction alone is not intervention success.

## Minimal scope

Use Python/sklearn, a small HTTP runtime, filesystem or SQLite run storage, n8n Community Edition and Docker Compose, configured hosted formatting, Slack/Gmail. Keep original notebooks as reference; production logic is in src, evaluation/tests are separate, and curated generated artifacts are justified evidence. No LangGraph, vector database/RAG, Kubernetes, unnecessary agents or decorative cloud infrastructure.
