# Historical snapshot — not current operating instructions

Preserved before Phase 3B.1 reconciliation. Use [current runtime](../RUNTIME.md) and
[current automation](../LIVE_AUTOMATION.md). Commands, counts and filenames below describe
their historical phases; they are not active implementation guidance.

# UrbanEats Phase 3 verification report

The current workflow is the verified 22-node Phase-3B export. See
[Phase 3B report](../PHASE3B_REPORT.md) for simplification, updated verification and
current credential-setup steps; six-send instructions below are historical.

## Phase 3A addendum — independent outage readiness

This addendum supersedes the former outage blocker in sections 22 and 27 below.
Phase 3A changes only orchestration outage handling, its verification and necessary docs.
Saved model, threshold, API scoring/delivery code and Docker configuration are unchanged.

1. **Root cause:** an offline API cannot return failure evidence or service its own
   delivery-claim/log endpoints. The workflow now constructs and persists an independent
   orchestration DATA_FAILURE before entering the existing failure notification gates.
2. **Created:** `workflows/n8n/outage_logic.cjs`, `scripts/build_outage_workflow.py`,
   `scripts/verify_outage_integration.py`, `tests/test_outage.py`,
   `evaluation/results/phase3a_verification.json`; ignored disposable fixtures/diagnostics.
3. **Modified:** `workflows/n8n/urbaneats_live.json`, `scripts/security_scan.py`,
   `evaluation/results/security_scan.json`, this report, LIVE_AUTOMATION.md, RUNTIME.md,
   README.md. Other working-tree changes predate Phase 3A.
4. **Flow:** trigger/settings/identity -> API/validator -> bounded retry -> final failure
   -> Prepare Outage Evidence -> Claim Orchestration Run -> Determine Outage Claim ->
   Persist Outage Evidence -> Restore Outage Context -> independent Slack/Gmail failure
   gates/placeholders -> channel audit -> merged completion audit. Valid API responses
   follow existing API routing; no API endpoint is needed for outage claim/persistence.
5. **Schema:** schema_version, evidence_origin=orchestration, orchestration_run_id,
   generated_at, routing_status=DATA_FAILURE, failure_stage=URBANEATS_API,
   failure_category, attempt_count, api_service, source_batch_id (known or null),
   test_mode, notification_required=true, sanitized attempt history. No fabricated
   model_version, records_scored, hotspot facts or model evidence IDs. Deterministic
   brief explicitly says no GREEN/RED assessment was produced and requests system review.
6. **Retries:** three total API attempts, 120-second per-attempt timeout, one-second
   waits for refusal/DNS/timeout/5xx/malformed; other HTTP errors stop after one attempt.
   Notification retries require definite rate-limit rejection, max three attempts,
   two-second waits. Ambiguous receipts are UNKNOWN and require manual reconciliation.
7. **Idempotency:** database-unique native Data Table name claims the run once. Same
   scheduled slot/explicit manual override suppresses both channels, including after
   process restarts. Manual execution IDs differ by default. Explicit force nonce makes
   a new namespace only after receipt reconciliation. TEST_MODE consumes its outage
   identity; use a fresh identity for credential tests. Do not delete claims/change project.
8. **Logging:** append-only native project Data Tables persist evidence, attempt history,
   start/completion times, service, category, route, test mode, each channel state/attempts
   and duplicate suppression. Send gates require successful initial persistence.
   Existing n8n_data holds production storage; verification never mounts that volume.
9. **Tests added:** 24 actual-JavaScript unit/contract cases; Docker/native execution
   tests healthy, stopped API, refusal, DNS, timeout, 500, 503, malformed, poisoned prior
   RED response, duplicate outage and recovery. Unit tests also reject prior GREEN data.
10. **Pytest:** 73 passed; two pre-existing dependency deprecation warnings.
11. **Lint:** Ruff check . passed.
12. **Docker outage:** PASS: healthy, stopped API, duplicate, refusal, DNS, timeout,
    500/503, malformed, poisoned prior RED and recovery (11 executions). See
    `evaluation/results/phase3a_verification.json`. Installed CE 2.41.6 native Data Tables
    are used, without storage mocks.
    CLI execute omits backend modules; only the disposable container initializes the
    same modules as n8n start. Stopped-service DNS failure is expected on this Docker host.
13. **Recovery:** PASS: API health READY, model/threshold loaded; native recovery returned
    the normal API RED_ALERT route on attempt 2, also proving successful retry uses the
    latest response. Existing n8n remains intact; disposable containers were removed.
14. **Security:** current public scan includes the new JS/CJS; zero findings. Workflow
    inactive; six send nodes disabled/unbound; no external LLM or Slack/Gmail calls,
    owner changes, existing volume deletion, commits, pushes or history rewrite.
15. **Remaining boundary:** real credentials/OAuth/receipts, live source and exploratory
    model suitability await later authorized work. Data Table storage quota/retention
    needs operational monitoring; preserve claim metadata. Not production readiness.
16. **Manual next steps:** import inactive export into existing n8n project; keep six
    send nodes disabled/unbound and Orchestration Settings test_mode=true; verify shared
    Docker network, execute healthy/outage/duplicate tests and inspect native tables.
    See LIVE_AUTOMATION.md Phase 3A for exact steps, force semantics and future live gates.
17. **Recommendation: READY FOR LIVE CREDENTIAL TEST.** The outage blocker is resolved.
    No publication or schedule activation is authorized by this work. Production readiness
    and real provider receipts are not claimed.

## 1. Phase-2 audit outcome
34 original tests passed and supplied holdout metrics reproduced. Saved model loads.
Direct inspection found the scaffold's wrong volume choice, absent hosted transport,
delivery claims and health/failure evidence, plus a real installed-package model-path
bug discovered during Docker execution. These were fixed. Model remains exploratory:
precision .4167, recall .5556, F1 .4762, ROC-AUC .4545, AP .5613; TN/FP/FN/TP 4/7/4/5.
production_ready=false. No intervention automation.

## 2. Files created
- .dockerignore
- src/urbaneats/provider.py
- src/urbaneats/delivery.py
- workflows/n8n/urbaneats_live.json
- tests/test_live.py
- scripts/phase3_smoke.py
- docs/LIVE_AUTOMATION.md
- docs/N8N_SETUP.md
- docs/PHASE3_REPORT.md
- evaluation/results/phase3_verification.json
- evaluation/results/phase3_smoke.json
- evaluation/results/phase3_docker_smoke.json
- Ignored local Docker/n8n mock scripts/fixtures/state under docker/local; run/delivery logs.

## 3. Files modified
README.md; AUDIT.md; docs/RUNTIME.md; docs/REMEDIATION_PLAN.md;
workflows/n8n/README.md; docker/compose.yaml; docker/runtime.Dockerfile;
.env.example; requirements.txt; pyproject.toml; src/urbaneats/service.py;
src/urbaneats/briefing.py; src/urbaneats/evidence.py; src/urbaneats/hotspots.py;
src/urbaneats/run_logging.py; scripts/current_demo.py; scripts/security_scan.py;
tests/test_runtime.py; evaluation/results/security_scan.json.
Evaluation reran and regenerated the exploratory saved artifact/results with identical metrics.
Original notebook/CSV/alerts/brief bytes are retained; no Phase-3 changes to legacy workflow.

## 4. Final directory tree
Public and operational tree; excludes Git internals, virtualenv, caches and individual local log files:

```text
Assignment-UrbanEats_CLEAN/
  .dockerignore  .env.example  .gitignore
  AUDIT.md  README.md  pyproject.toml  requirements.txt  requirements-dev.txt
  UrbanEats_classifier_langchain.ipynb  UrbanEats_profiling_gx.ipynb
  UrbanEats_n8n_workflow.json
  urbaneats_delivery_orders.csv  urbaneats_delivery_orders_scored.csv
  urbaneats_alerts.json  urbaneats_ops_brief.md
  artifacts/model/
    pipeline.joblib (trusted local ignored artifact)
    metadata.json  threshold.json  feature_contract.json
  data/
    current_batch.json (ignored controlled synthetic source)
    raw/README.md  processed/.gitkeep
  docker/
    compose.yaml  runtime.Dockerfile
    local/ (ignored disposable verification scripts/fixtures/mock state)
  docs/
    EVALUATION.md  FEATURE_CONTRACT.md  RUNTIME.md  REMEDIATION_PLAN.md
    LIVE_AUTOMATION.md  N8N_SETUP.md  PHASE3_REPORT.md
  evaluation/
    __init__.py  evaluate.py
    results/
      metrics.json  verification.json  local_smoke.json  security_scan.json
      phase3_verification.json  phase3_smoke.json  phase3_docker_smoke.json
  notebooks/original/README.md
  runs/
    .gitkeep  UE-*.json (ignored execution evidence)  delivery/ (ignored events/claims)
  scripts/
    current_demo.py  smoke_test.py  phase3_smoke.py  security_scan.py
    sanitize_legacy_workflow.py
  src/urbaneats/
    __init__.py  actions.py  briefing.py  config.py  delivery.py  evidence.py
    features.py  hotspots.py  inference.py  metrics.py  model.py  provider.py
    run_logging.py  schemas.py  service.py  validation.py
  tests/
    conftest.py  test_evaluation.py  test_live.py  test_model.py
    test_runtime.py  test_scaffold.py
```

## 5. Docker architecture
Two runtime services: urbaneats-api and n8n, one bridge network urbaneats_private.
No additional database/service. Transient isolated verification containers are disposed.
Host ports bind only loopback. API calls use service DNS, never n8n localhost.

## 6. Docker Compose design
Pinned Python base digest and locally observed n8n 2.41.6 digest. Explicit artifact/source/
run paths, TEST_MODE default true, read-only data, writable run logs, API healthcheck.
Managed n8n is opt-in via profile and depends on API health. Asia/Kolkata timezone.
Existing n8n can join the network manually without replacement.

## 7. Existing n8n preservation strategy
Verified running container n8n and n8n_data:/home/node/.n8n. No stop/recreate/import/owner/
credential/configuration changes on that container. No volume deletion. Docker tests used
separate disposable n8n state. Keep original encryption configuration for any future migration.

## 8. UrbanEats API contract
GET /health returns explicit model/threshold readiness/version. POST /process-batch and
/process-current return DATA_FAILURE, GREEN_SUMMARY or RED_ALERT with run/evidence/brief.
POST /delivery records atomic claims/attempt outcomes, never sends messages. Runtime never trains.

## 9. Current-source contract
Mounted fresh placement-v1 JSON or equivalent API payload. Immutable producer batch ID,
generated_at/source_timestamp, canonical SHA256, received/scored counts and freshness.
One-hour freshness, strict types/ranges/categories/unique IDs/timestamps, no outcome fields.
No historical scored CSV. Unknown restaurants use trained unknown-category policy.

## 10. Final n8n node flow
Schedule 07:30 Asia/Kolkata or Manual Trigger -> Acquire Current Batch -> API ->
Validate API Response -> Audit Available -> explicit status switch -> route brief ->
independent Slack/Gmail claims -> send gates -> send -> receipt -> log -> bounded retry.
API performs evidence, hosted formatting, validation and fallback before response.
Unverified/unavailable API -> sanitized DATA_FAILURE -> local n8n execution log, no send.
Public export inactive, all six real send nodes disabled and no live environment identifiers.

## 11. LLM provider abstraction
FormatterProvider.generate; configurable openai-compatible HTTPS transport via LLM_PROVIDER,
LLM_BASE_URL, LLM_MODEL, LLM_API_KEY. TEST_MODE blocks hosted transport. No provider chosen/called.

## 12. LLM output validation
Detached evidence/actions/schema only. Valid evidence/action IDs, exact canonical sentences,
required evidence retained. Altered numbers/causes/actions/provenance rejected. Canonical
rendering preserves routing. Conservative wording permits reordering, not arbitrary prose.
Timeout/HTTP/invalid output uses deterministic fallback with sanitized trace.

## 13. Slack credential design
Real Slack nodes, disabled and unbound; local channel placeholder. Bind local Slack credential
and channel on all three routing branches. RED says manual review required; all carry provenance.

## 14. Gmail credential design
Real Gmail nodes, disabled and unbound; local recipient placeholder. Local Google OAuth/Gmail
API setup and test recipient; no personal address or credential ID in export.

## 15. Retry strategy
API max 3 attempts/120-second timeout; log HTTP max 3/30 seconds; LLM max 3/15 seconds,
1/2-second backoff for transient errors. Notification explicit rate-limit nonacceptance max
3 attempts/two-second wait. Every attempt logged. Ambiguous/timeout/5xx/unrecognized receipts
remain claimed for manual reconciliation. No blind delivery retry or infinite loops.

## 16. Idempotency strategy
Atomic persisted source_batch_id + channel claims (checksum fallback for invalid/missing IDs),
owned by one run, durable across restarts. Changed source needs new ID. Same batch retry is
suppressed per channel. No automatic expiry. Authorized forced resend requires provider receipt
reconciliation and targeted claim release; no public force endpoint.

## 17. Execution/delivery logging design
Atomic per-run JSON records timestamps/source/validation/routing/model/threshold/evidence/LLM
trace. Separate per-attempt events record channel/attempts/result/error category/retry/duplicate
suppression. Join on run_id. No provider headers/keys/raw exceptions in runtime logs.

## 18. TEST_MODE behavior
Default true: no hosted transport; claim send=false; no live delivery claims consumed; real
send nodes also disabled. Fixtures failure, green (4 rows insufficient support), red (24 rows).
Mock transport/isolated claim stores prove fallback/retries/duplicates without external calls.

## 19. Tests run and results
49 pytest passed, 0 failed, 2 known dependency deprecation warnings. ruff check . passed with
historical notebooks explicitly excluded. Evaluation reproduced holdout. pip check passed.
Loopback and Docker API smokes passed. Native n8n import and all three routes passed with sends
skipped. Native n8n mock send loops passed two rate limits then success on attempt three; a second
execution of the same batch suppressed both channels with zero mock sends.
See evaluation/results/phase3_verification.json and phase3_docker_smoke.json.

## 20. Docker verification results
Docker client/server 29.8.1; Compose config passed; image build passed; API healthy and saved
artifact loads in Linux container. Health and 0/4/24-record routing smokes passed. n8n CE 2.41.6
disposable import/execution passed; CLI needs temporary ID, absent from public workflow.
Existing n8n running and volume retained. TEST_MODE API left running on localhost:8000.

## 21. Security scan results
No candidates found in scanned current public text/notebook outputs/workflow identifiers.
Patterns cover provider keys, PATs, OAuth/Slack tokens, emails, Slack IDs, Drive/private URLs,
credential/webhook/workflow instance metadata. Only type/file/remediation output for findings.
Historical baseline identifiers remain; no history rewrite. Local environment/run/mock state excluded.

## 22. Unresolved issues
The former offline API claim/log blocker is resolved by the Phase-3A addendum above.
Native provider error shapes/OAuth/actual receipts await authorized
credential tests. Current producer, units, maturity/target semantics and exploratory model are
not production validated. No scheduled/publication or real external integration demonstration.

## 23. Exact manual Docker commands next
Run in repository root, with Docker Desktop running. API is already healthy; build/up below are
safe repeatable API-only commands. Preserve existing n8n. Do not invoke managed-n8n profile yet.

```powershell
docker ps --format '{{.Names}} {{.Image}}'
docker volume inspect n8n_data
docker inspect n8n --format '{{range .Mounts}}{{println .Name .Destination}}{{end}}'
docker compose -p urbaneats -f docker/compose.yaml config --quiet
docker compose -p urbaneats -f docker/compose.yaml build urbaneats-api
docker compose -p urbaneats -f docker/compose.yaml up -d urbaneats-api
docker inspect n8n --format '{{json .NetworkSettings.Networks}}'
# Run only if n8n is not already attached to urbaneats_private:
docker network connect urbaneats_private n8n
Invoke-RestMethod http://localhost:8000/health
$env:PYTHONPATH='src'
.venv\Scripts\python.exe scripts/current_demo.py --scenario failure
```

## 24. Exact n8n UI steps next
1. Sign in to existing localhost:5678 owner account; do not recreate it.
2. New workflow -> Import from File -> workflows/n8n/urbaneats_live.json.
3. Keep inactive/unpublished; timezone Asia/Kolkata, cron 30 7 * * *.
4. Keep six Slack/Gmail send nodes disabled/unbound. Verify service URLs.
5. Execute Manual Trigger for failure/green/red fixture sequence below.
6. Confirm claims TEST_MODE_DISABLED, correct evidence/provenance and no sends.
7. For later authorized credential testing, locally bind Slack/Gmail credentials/destinations, select
   hosted provider, enable send nodes while TEST_MODE remains true. Only then deliberately
   change TEST_MODE for authorized credential tests. Verify receipts before publish decision.

## 25. Exact credentials/accounts/API key still required
Hosted compatible provider account/API key/base URL/model; Slack workspace/app credential
with permission/access to chosen test channel; Gmail account plus Google Cloud OAuth client/
consent configuration with Gmail API enabled and exact n8n redirect URI; local test recipient.
No new n8n account. No real secrets created/read/configured by this work.

## 26. Exact live test sequence
The Phase-3A addendum fixes the outage-notification gap. Current safe tests:

```powershell
$env:PYTHONPATH='src'
.venv\Scripts\python.exe scripts/current_demo.py --scenario failure
# Execute Manual Trigger; DATA_FAILURE, no inference/send.
.venv\Scripts\python.exe scripts/current_demo.py --scenario green
# Execute Manual Trigger; GREEN_SUMMARY, insufficient support, no health claim.
.venv\Scripts\python.exe scripts/current_demo.py --scenario red
# Execute Manual Trigger; RED_ALERT, manual review only.
.venv\Scripts\python.exe -m pytest -q tests/test_live.py
```

Later authorized credential tests: fresh failure -> both actual failure receipts; fresh green ->
both green receipts; fresh red -> both red receipts; same red batch -> both duplicate suppressions;
new red with provider configured -> validated formatter trace; provider unavailable -> new red
with deterministic fallback; verify rate-limit bounds/unknown receipt reconciliation and logs.
Configure 07:30 Asia/Kolkata and publish only after all gates pass and you choose to activate.

## 27. Recommendation
The historical Phase-3 recommendation was NOT READY FOR LIVE CREDENTIAL TEST.
The Phase-3A addendum supersedes it after independent outage verification.
No real LLM/Slack/Gmail calls, workflow activation, commits, pushes or history rewrite.
