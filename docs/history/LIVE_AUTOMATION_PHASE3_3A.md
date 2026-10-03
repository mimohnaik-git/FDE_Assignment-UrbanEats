# Historical snapshot — not current operating instructions

Preserved before Phase 3B.1 reconciliation. Use [current runtime](../RUNTIME.md) and
[current automation](../LIVE_AUTOMATION.md). Commands, counts and filenames below describe
their historical phases; they are not active implementation guidance.

# Phase 3 / 3A / 3B local live automation setup

## Current Phase 3B export

The current `workflows/n8n/urbaneats_live.json` has 22 nodes, replacing the 79-node
Phase-3A design. Use this export only. All statuses share one Slack node, one Gmail
node, packet builder, persistent native claim and audit path. Both send nodes remain
disabled/unbound. Settings defaults `test_mode:true`; API TEST_MODE remains independently
true. The workflow remains inactive at 07:30 Asia/Kolkata.

Import into the same existing n8n project without changing n8n_data. Keep the previous
workflow inactive. Execute manually and inspect Persist Completed Audit and native
Data Tables. Preserve existing outage claims; TEST_MODE now consumes API batch claims
as well. Fresh batch identity or explicit reconciled force nonce is required for later
credential testing. Do not activate, configure credentials or enable sends in Phase 3B.
Run `scripts/verify_notification_integration.py` for the current isolated native checks.
See [Phase 3B report](../PHASE3B_REPORT.md) for exact flow, behavior changes and justification
for the six nodes beyond the 16-node target. All earlier six-send/branch instructions
below describe the historical Phase-3/3A design and are superseded by this section.

## Phase 3A independent API-outage path

Recommendation: **READY FOR LIVE CREDENTIAL TEST** after 73 passing pytest tests, Ruff,
clean public security scan and 11 passing native executions including actual API stop,
duplicate suppression and healthy recovery. No credentials or external sends were used.

The inactive export now generates DATA_FAILURE independently of the API. API-generated
DATA_FAILURE retains the existing API evidence/brief and delivery claims. Orchestration
DATA_FAILURE has `evidence_origin=orchestration`, a separate run ID, deterministic brief,
and native n8n Data Table persistence; it does not call the API to claim or log delivery.
No model version, score count, hotspot facts or model evidence IDs are invented.

Flow: trigger -> Orchestration Settings -> Initialize Orchestration -> API request ->
Validate API Response -> retry (at most three attempts) -> Audit Available. Valid API
responses use existing routing. Final transport/unusable responses -> Prepare Outage
Evidence -> unique Data Table claim -> persist evidence -> both existing failure gates
and Slack/Gmail placeholders -> persist channel states -> persist completion audit.
All six real send nodes remain disabled and credential-unbound. `test_mode=true` in
Orchestration Settings independently blocks outage sends even when the API is stopped.

Each API attempt has a 120-second timeout. Connection refusal, DNS/service failure,
timeout, HTTP 5xx and malformed/unusable responses receive at most three total attempts,
with one-second waits. Other non-success HTTP responses stop after one attempt. The
maximum request/wait budget is approximately 362 seconds, plus workflow overhead.
Successful retries use the latest response. A 5xx body containing previous RED/GREEN
data is discarded. Notification retries are limited to definite rate-limit rejection,
three total attempts and two-second waits; ambiguous receipts remain UNKNOWN for review.

`UE_ORCH_<orchestration_run_id>` is a native Data Table in the workflow's project.
Its database-enforced unique name is the atomic claim. The table contains append-only
prepared, channel and completion audit rows: run/start/completion times, service,
attempt count/history, category, DATA_FAILURE, both channel states, duplicate flag and
TEST_MODE. SQLite storage survives n8n restarts through the existing `n8n_data` volume.
Persistence must succeed before either send gate. Storage/claim errors fail closed.
This creates one small table per outage run; monitor n8n's Data Table storage quota.
Do not delete claim tables to retry a delivery or change the workflow's project.

Scheduled identity is the Kolkata date and 07:30 slot. Manual runs normally use execution
ID; to re-execute the same logical outage, set `orchestration_run_id_override` to its
original ID. Internal API retries retain one identity; duplicate claims suppress both
channels and append duplicate audit rows. TEST_MODE claims also consume that identity:
use a fresh ID for later credential tests. After reconciling previous receipts, an
explicit manual force sets a new `force_retry_nonce`; this deliberately creates a new
claim namespace and may deliver again. Clear override/nonce before scheduling.

Next manual n8n steps:
1. Sign in to the existing owner account; import `workflows/n8n/urbaneats_live.json`
   as a new workflow in the same project. Keep it unpublished/inactive.
2. Keep all six send nodes disabled/unbound. Inspect Orchestration Settings:
   `test_mode=true`, empty override/nonce; enter a source batch ID only if already known.
3. Ensure existing n8n can resolve `urbaneats-api` on `urbaneats_private` using the
   existing network setup instructions below; do not recreate n8n or its volume.
4. Execute Manual Trigger; verify the normal API route. For the isolated outage check
   run `.venv\Scripts\python.exe scripts/verify_outage_integration.py` from the repository.
   It stops only the API, restores it in finally, and never accesses `n8n_data`.
5. Inspect n8n Data Tables and execution output: outage evidence, both SKIPPED_TEST_MODE
   states, completion timestamps and duplicate suppression with a fixed override.
6. Future explicitly authorized credential tests require local credentials/destinations,
   enabling appropriate send nodes, and coordinated API TEST_MODE and orchestration
   `test_mode` settings. Keep both true during setup. Do not publish/activate now.

Verification uses the installed CE 2.41.6 image. Its CLI `execute` omits backend module
initialization, so the disposable test container initializes the same native modules
as `n8n start`. No persistence mocks, user container modification, owner recreation or
external credentials are involved. Raw execution diagnostics stay ignored locally.
See `evaluation/results/phase3a_verification.json` for sanitized native results.

The Phase-3 sections below are historical where they describe the former outage gap;
this Phase-3A path supersedes that limitation. Live provider receipts remain untested.

Status: Docker Compose config, API image build/health/all routes, and disposable n8n
2.41.6 import/credential-free execution of all three routes are verified. No hosted calls, sends, activation, commits or pushes.
The model remains exploratory, production_ready=false. RED means manual review required.
GREEN means no supported predicted-risk hotspot detected. No business intervention.

## Architecture and current source

One Compose bridge network `urbaneats_private`: `urbaneats-api:8000` plus n8n.
A bridge allows later authorized HTTPS provider access; it is not Internet isolation.
Only loopback host ports 8000/5678 are published. No database or extra containers.
API healthcheck loads the saved model and threshold; managed n8n waits for API health.
API mounts data read-only and runs read/write. n8n uses external existing `n8n_data`.
The managed-n8n profile is opt-in. Never start it while existing n8n owns port 5678.
Set N8N_IMAGE to the existing exact image digest before any managed-profile migration.
The Compose default pins the locally observed n8n 2.41.6 image digest. Keep your existing image and settings for any migration. Preserve encryption key configuration
and mounts if you later migrate; this guide deliberately reuses the current container.

Current source: mounted `data/current_batch.json`, placement-v1 envelope; /process-current
rereads every invocation. /process-batch accepts the same payload directly for a future
external adapter. Source timestamp is generated_at; source checksum hashes canonical
validated JSON; source_batch_id is immutable producer identity. Source and placements
must be timezone-aware and <=3600 seconds old (60 second future skew tolerated).
No historical scored CSV is read. Missing/invalid/stale/outcome fields fail closed.
See FEATURE_CONTRACT.md for exact fields, units and unresolved source semantics.

GET /health: status, model_loaded, model_version, threshold_loaded, runtime_status.
POST /process-current or /process-batch: run_id, routing_status, validation_status,
model/threshold, predictions, current KPIs/groups, evidence and notification-ready brief.
DATA_FAILURE has deterministic FAILURE evidence and CHECK_DATA; no invalid inference.
Every scored order retains order_id, probability, flag, model_version and run_id.
Support floor remains 20; groups below it cannot trigger RED. Evidence retains lineage,
source timestamp/checksum, counts, ratios, supported/suppressed groups and approved actions.
No observed cancellation KPI exists in placement-only data.

## Formatter, delivery and retries

LLM_PROVIDER=openai-compatible selects a small HTTPS chat-completions adapter.
LLM_BASE_URL must include provider API prefix (for example the provider's /v1);
LLM_MODEL and LLM_API_KEY are configured locally in ignored .env. Swap providers by
changing the compatible base URL/model, or implement FormatterProvider.generate.
No provider has been chosen or called here. TEST_MODE=true disables configured transport.
Provider gets detached evidence/actions/output schema. Conservative validation allows
only exact canonical sentences with valid evidence/action IDs; hosted formatting can
reorder them. Free prose/rephrasing is deliberately restricted because arbitrary semantic
claims cannot be reliably verified by regex. Deterministic rendering preserves routing,
provenance and exploratory limitations. Unsupported numbers/actions/causes fall back.
Provider retries transient HTTP 429/5xx or transport errors at most 3 times, timeout
15 seconds each, backoffs 1/2 seconds. Invalid output and permanent errors fall back.
Trace records provider/model, attempts, validated/fallback state and generic reason.
API call uses 120-second timeout and max 3 attempts; log calls use 30 seconds/max 3.

Workflow nodes: Schedule (07:30 Asia/Kolkata) OR Manual Trigger -> acquire mounted-source
contract -> API (ingestion/validation/inference/KPIs/evidence/optional hosted formatting/
validation/fallback) -> Validate API Response -> switch DATA_FAILURE/GREEN_SUMMARY/RED_ALERT
-> route brief -> independent Slack and Gmail claim -> send gate -> real send node ->
receipt validation -> per-channel Delivery Log. Formatter stages are encapsulated in the
API to avoid exposing the LLM key to n8n or duplicating evidence validation logic.
Unknown routes or unverified API responses use the independent Phase-3A orchestration
DATA_FAILURE path above. Outage claim/audit records use native n8n storage while the
API is offline; API-generated evidence and delivery claims retain the existing path.

/delivery accepts stored run_id, channel=slack|gmail, operation=claim|complete,
outcome=success|failure|unknown and attempts (0..3). It never sends anything itself.
Atomic exclusive filesystem claims key on immutable source batch ID + channel,
across API restarts/runs. Reusing a batch ID with changed content remains suppressed:
producers must assign a new ID for new data. No TTL silently releases claims.
TEST_MODE=true returns send=false and logs disabled delivery; no claims are consumed.
After a live claim, ambiguous/failed deliveries remain claimed for manual reconciliation.
Slack/Gmail retry only an explicit not-accepted rate-limit response (Slack ok=false
with ratelimited/rate_limited; Gmail explicit statusCode=429). Receipt -> delivery log ->
retry gate -> two-second Wait -> send loops are bounded to three total attempts.
Timeouts, 5xx and unrecognized n8n error shapes remain UNKNOWN and are not blindly retried
because acceptance may be ambiguous. Every attempt is logged, and the original per-channel
claim stays owned by this run. Offline n8n mock receipts validate these loops; native
provider error shapes still require authorized credential verification. Further retries
after the budget or ambiguous results require explicit receipt reconciliation.
Explicit force is not exposed; authorized manual resend requires backing up/removing the
specific channel claim after checking the provider receipt. Never clear all claims.
Claims prevent a second send sequence for the same batch/channel; bounded rejection
retries stay in the original sequence. This does not guarantee exactly-once delivery.

Execution JSON records source/validation/routing/model/threshold/evidence/LLM trace;
separate immutable delivery events record run/channel/status/attempts/duplicate suppression.
Join events to runs by run_id. API errors are generic codes; provider response/headers/keys
are never stored. n8n execution logs remain local and can contain recipient/receipt data.
Historical notebooks are excluded from ruff checks to preserve original assignment bytes.
Local API is unauthenticated: loopback/controlled Docker network only, not public exposure.

## Exact safe Docker commands (PowerShell at repository root)

Docker must first be available in your PowerShell. Open Docker Desktop and a new shell.
These commands preserve the already created owner account and current container.

```powershell
docker ps --format '{{.Names}} {{.Image}}'
$n8nContainer = Read-Host 'Enter your existing n8n container name'
docker inspect --format '{{range .Mounts}}{{println .Name .Destination}}{{end}}' $n8nContainer
docker volume inspect n8n_data
$env:N8N_IMAGE = docker inspect --format '{{.Image}}' $n8nContainer
# Keep this exact digest for future migration. Inspect output must show n8n_data -> /home/node/.n8n.
# Do not proceed with migration if this mount differs; preserve that actual volume instead.
docker compose -p urbaneats -f docker/compose.yaml config
docker compose -p urbaneats -f docker/compose.yaml build urbaneats-api
docker compose -p urbaneats -f docker/compose.yaml up -d urbaneats-api
# Only if inspect shows existing n8n is not already on this network:
docker network connect urbaneats_private $n8nContainer
Invoke-RestMethod http://localhost:8000/health
$env:PYTHONPATH = 'src'
.venv\Scripts\python.exe scripts/current_demo.py --scenario red
Invoke-RestMethod -Method Post http://localhost:8000/process-current
```

Never run `down -v`, volume rm, system prune, or recreate the owner account.
Do not automatically replace/recreate the existing container. Its original environment,
encryption key and startup configuration have not been inspected here. Do not mount the
same n8n volume into two concurrently running n8n processes. The opt-in Compose service
is for a separately planned, backed-up migration, not required for this verification.
For an independently running n8n that lacks Asia/Kolkata environment settings, the workflow
itself explicitly sets Asia/Kolkata; recreate environment only during a safe migration.

## Exact n8n UI steps

1. Open your existing http://localhost:5678 and sign in to the existing owner account.
2. Create a new workflow -> menu -> Import from File -> workflows/n8n/urbaneats_live.json.
3. Keep it unpublished/inactive. Check workflow settings timezone Asia/Kolkata.
4. Verify HTTP nodes point to http://urbaneats-api:8000; inspect source contract node.
5. Leave all Slack/Gmail credentials unbound for initial TEST_MODE manual tests.
6. Execute Manual Trigger for each fixture below; claim nodes must return send=false.
7. Confirm independent channel events in runs/delivery and run/evidence/brief provenance.
8. After Docker/import gates pass and you choose to test live credentials, create local
   Slack and Gmail credentials. Bind each of three Slack and three Gmail send nodes; enable them only at the authorized live-test stage.
   Set each channelId and sendTo locally. No public export should retain these values.
9. Slack: workspace/account allowing a bot/app to post to your chosen test channel;
   use n8n-supported Slack credential type with chat:write and channel access.
10. Gmail: Google account, Google Cloud OAuth client/consent setup with Gmail API enabled;
    copy the exact redirect URL shown by your installed n8n credential dialog into the
    OAuth client; authorize that account locally. Choose your test recipient locally.
11. Choose a compatible hosted provider account/model/key/base URL. Configure ignored .env;
    restart only urbaneats-api with --env-file .env. Never put real keys in exports.
12. Only for explicitly authorized live credential tests set TEST_MODE=false in .env and
    run `docker compose --env-file .env -p urbaneats -f docker/compose.yaml up -d urbaneats-api`.
    This enables claims/provider transport; n8n manual execution can now send.
13. Verify both actual provider receipts and delivery events before interpreting success.
14. Confirm Schedule cron `30 7 * * *` and timezone Asia/Kolkata. Publish/activate only after
    all acceptance gates pass and you explicitly decide to enable daily live notifications.
    Scheduled input must be refreshed by a real producer before 07:30; stale data fails.

## Exact fixture/test sequence

Keep TEST_MODE=true and run these at repo root with PYTHONPATH=src:

```powershell
.venv\Scripts\python.exe scripts/current_demo.py --scenario failure
# Execute Manual Trigger: DATA_FAILURE; deterministic failure evidence; both sends skipped.
.venv\Scripts\python.exe scripts/current_demo.py --scenario green
# Execute Manual Trigger: GREEN_SUMMARY; four rows, insufficient support; no health claim.
.venv\Scripts\python.exe scripts/current_demo.py --scenario red
# Execute Manual Trigger: RED_ALERT; 24 current synthetic orders; manual review only.
# Execute again without changing file: same source ID, different run. TEST_MODE logs disabled.
.venv\Scripts\python.exe -m pytest -q tests/test_live.py
# Offline mock transport proves timeout/429/invalid number/action fallback and live-mode
# claim suppression without invoking any external service or n8n notification node.
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m evaluation.evaluate
```

Future authorized live sequence: new failure batch -> verify Slack/Gmail failure receipts;
new green batch -> verify qualified green wording; new red batch -> verify manual-review
wording; repeat same red batch -> both claims suppress; choose hosted key/model -> new red
batch -> validated hosted trace; intentionally unconfigured provider -> new red batch ->
deterministic fallback; reconcile failures/unknown receipts. Restore TEST_MODE=true until
schedule publication is explicitly intended. Full TEST_MODE disposable n8n import and execution passed on the installed CE 2.41.6 image.
Real Slack/Gmail nodes are disabled in the public export to allow credential-free validation.
Enable all six send nodes only after binding credentials/destinations and deciding to test live;
leave API TEST_MODE=true and orchestration test_mode=true while making these local
configuration changes. A later authorized credential test must coordinate both settings.
