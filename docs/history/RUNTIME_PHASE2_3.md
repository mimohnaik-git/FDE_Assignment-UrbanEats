# Historical snapshot — not current operating instructions

Preserved before Phase 3B.1 reconciliation. Use [current runtime](../RUNTIME.md) and
[current automation](../LIVE_AUTOMATION.md). Commands, counts and filenames below describe
their historical phases; they are not active implementation guidance.

# Phase 3 live integration (2026-10-03)

Local API/provider/delivery architecture and sanitized inactive workflow are implemented.
TEST_MODE defaults true; no external LLM calls, Slack/Gmail sends or workflow activation.
Docker config/build/health/API routes and disposable n8n 2.41.6 import/all three routes
passed. Phase 3A verifies independent, persistent n8n DATA_FAILURE handling when the API
is offline: **READY FOR LIVE CREDENTIAL TEST**. This is not production readiness.
Bounded retries cover definite rate-limit rejections; ambiguous
delivery outcomes remain suppressed for manual reconciliation.
See [live automation setup](../LIVE_AUTOMATION.md) for exact commands, credentials, tests, retries and preservation strategy.
Model remains exploratory: precision .4167, recall .5556, F1 .4762, ROC-AUC .4545,
AP .5613, TN/FP/FN/TP 4/7/4/5; production_ready=false. RED is manual review only.
GREEN means no supported predicted-risk hotspot detected.

API-generated DATA_FAILURE uses API run evidence, deterministic brief and existing
filesystem delivery claims. Offline/unusable API responses generate orchestration
DATA_FAILURE inside n8n after bounded attempts, with separate run IDs, no invented
model facts and native Data Table audit/claims in n8n_data. Both outage channels consume
the independent brief. Phase 3B consolidates the workflow to 22 nodes; n8n owns native
claims/audits for every status and no longer calls the API delivery endpoints. Settings
test_mode defaults true independently of API TEST_MODE; both stay true during setup.
The export remains inactive with its single Slack and single Gmail nodes disabled/unbound.
See PHASE3B_REPORT.md and LIVE_AUTOMATION.md for retries, TEST_MODE claim consumption,
same-run override/force semantics, storage retention and exact manual steps.

The Phase-2/historical sections below record earlier implementation status; the Phase-3
setup above supersedes their Docker, provider, logging and idempotency statements.

---

# Local runtime and Phase-3 boundary

Python target: 3.12. Install the pinned requirements into a project virtual environment
when dependency installation is permitted. Phase 2 verification uses existing local
packages copied offline into .venv; no package download or external service call.

```powershell
$env:PYTHONPATH = 'src'
.venv\Scripts\python.exe -m evaluation.evaluate
.venv\Scripts\python.exe scripts/current_demo.py
.venv\Scripts\python.exe -m uvicorn urbaneats.service:app --host 127.0.0.1 --port 8000
```

The evaluation command writes the saved pipeline, metadata, contract, selected threshold
and measured evaluation report. Joblib is executable serialization: load only this
locally generated trusted artifact. Integrity hash is an accidental-corruption check,
not an authenticity signature. Restart service after replacing artifacts.

GET /health returns 200 READY only if the model loads, otherwise 503 NOT_READY.
POST /process-batch accepts the placement-v1 envelope. POST /process-current rereads
URBANEATS_SOURCE_FILE each call, making ingestion suitable for the scheduled n8n step.
Neither endpoint calls an external provider or sends notifications. Semantic errors
return HTTP 200 with DATA_FAILURE to make explicit n8n routing possible; transport
failure/HTTP errors must also be routed to failure in Phase 3. Malformed JSON is logged
as invalid data. Runtime/model/log failures can never return GREEN_SUMMARY.

Response includes run_id, status (SUCCESS/DATA_FAILURE), validation_status,
routing_status (DATA_FAILURE/GREEN_SUMMARY/RED_ALERT), received count, errors,
per-order predictions, metrics, all supported/suppressed groups, immutable evidence
and cited briefing. DATA_FAILURE returns no inference for invalid inputs. On logging
failure, response is forced to DATA_FAILURE even after successful computation.

Each run is persisted atomically as runs/UE-<uuid>.json: timestamps, source batch,
validation, received/scored counts, routing, model/threshold, evidence IDs, sanitized
error codes, notification status and complete result/evidence/briefing. Local files
contain order lineage and are ignored by Git. Retention/access control and authenticated
service boundary remain Phase-3 production-hardening decisions. Repeated invocations
receive separate run IDs; delivery deduplication is not implemented in Phase 2.

Formatter interface is injectable and tested with local stubs. It receives a detached
structured evidence packet with approved actions. Phase 2 accepts only structured
selection/ordering of exact canonical fact sentences and approved action IDs; arbitrary
rephrasing is intentionally deferred because number/citation checks alone cannot
exclude invented causal prose. Required batch and hotspot evidence cannot be omitted.
Any invalid output or provider exception triggers deterministic fallback. Stub success
is labeled provider_stub, never hosted generation. Citation strings are rendered by
the pipeline; validators resolve every evidence ID and run/source reference.

Actions are limited to supported-hotspot MANUAL_REVIEW and failure CHECK_DATA.
No staffing, preparation-SLA, menu/pricing or causal recommendation is justified by
the present evidence. Catalog entries contain action_id, description, trigger_condition
and evidence_requirement. Failure run errors justify CHECK_DATA; hotspot facts carry
MANUAL_REVIEW IDs only when supported and above policy threshold.

Docker/n8n files are inactive design scaffolding. Phase 3 must pin/test an exact CE
version, import/routing verify, add hosted formatter transport (with factual guards),
independent Slack/Gmail branches, safe credentials, delivery retries/idempotency and
logs. No containers or workflows are launched by Phase-2 verification. Fresh synthetic
input demonstrates the local contract only; real source, scheduled trigger, hosted
generation and actual notifications remain unproven until Phase 3.

Verification on 2026-10-03: 34 pytest tests passed; Ruff and pip check passed;
evaluation completed; loopback HTTP smoke passed with health READY, 24 predictions,
RED_ALERT, and invalid/stale DATA_FAILURE. Two dependency deprecation warnings are
recorded in evaluation/results/verification.json; no warnings were suppressed.
Test temporary directories were redirected inside the workspace after the first
run hit sandbox restrictions during pytest's shared OS-temp cleanup. The final run
completed normally. No external downloads/APIs, hosted calls, messages or activation.
