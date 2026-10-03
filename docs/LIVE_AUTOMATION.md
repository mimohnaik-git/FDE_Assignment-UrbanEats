# Current automation — 22-node Phase 3B

Canonical export: workflows/n8n/urbaneats_live.json. n8n Community Edition 2.41.6 is pinned
by digest in Compose and native verification. The accepted architecture has two triggers,
one Slack send node, one Gmail send node and shared normalization, claims, receipts and
audit. It stays inactive, credential-unbound and TEST_MODE=true at 07:30 Asia/Kolkata.

## Responsibility and flow

The API owns current-source validation, inference, KPIs/supported restaurant-zone hotspots,
evidence/actions, optional hosted formatting, validation and deterministic fallback.
It remains exploratory, uncalibrated and conditional Delivered-vs-Cancelled.

Schedule/Manual → Settings → API → Normalize Response/unified packet → bounded retry →
Claim Run → prepare/persist audit → duplicate/TEST_MODE gate → Slack/Gmail → parse receipts →
persist delivery audit → bounded retry/channel routing → merged completion audit.
[Phase 3B report](PHASE3B_REPORT.md) explains all 22 nodes and the six beyond the 16-node aim.

Valid API DATA_FAILURE/GREEN_SUMMARY/RED_ALERT preserve the API brief/evidence verbatim.
An unavailable/malformed API response generates deterministic orchestration DATA_FAILURE
with a separate orchestration ID, timestamp, failure stage/category, bounded attempt
history, service, known source batch, TEST_MODE and notification_required=true. It contains
no invented model version, scored count, hotspot facts or previous GREEN/RED assessment.
Both channels consume the same current packet; no LLM is needed for an outage brief.

## Retry, claims and audit

API timeout: 120 seconds per attempt; at most three total attempts, with one-second waits
for refusal/DNS/timeout/5xx/malformed responses. Other non-success HTTP responses stop
after one attempt. Successful retries use the latest response from that execution.

Delivery retries: only definite rate-limit rejection, at most three attempts per channel,
with two-second waits. Ambiguous outcomes remain UNKNOWN and claimed for reconciliation;
they are not automatically retried. One channel's outcome does not overwrite the other.

Native Data Tables in the workflow's project provide database-unique atomic claims and
append-only prepared/channel/completion audits. Initial persistence precedes either send.
Claim/storage errors block sends. Records retain start/completion times, evidence packet,
service/category, request attempts, channel states/attempts, duplicate suppression and
TEST_MODE. Storage survives restarts through the existing n8n_data volume.

API batches deduplicate by source batch identity (checksum fallback); different API run
IDs do not release claims. Outages use orchestration identity; names/schema remain
compatible with historical outage claims. Scheduled identity uses the Kolkata date/slot.
Manual executions normally receive new identities; set orchestration_run_id_override to
repeat the same logical outage. TEST_MODE consumes claim identities for every status.
An explicit force_retry_nonce makes a new namespace after prior receipt reconciliation;
clear override/nonce before scheduling. Do not delete claims or change project to bypass
suppression. Monitor native Data Table quota; retain claim metadata during archival.

## Existing Docker/n8n setup

Keep the existing n8n container, owner account, encryption configuration and n8n_data.
Compose's managed-n8n profile is opt-in; do not run a second n8n process on the same volume.
Use the existing service/network setup; only the API needs to be running for normal calls.

```powershell
docker compose -p urbaneats -f docker/compose.yaml config --quiet
Invoke-RestMethod http://127.0.0.1:8000/health
# Only if the existing n8n container is not already connected:
docker network connect urbaneats_private n8n
```

Do not recreate the existing owner, delete n8n_data, run down -v or replace the existing
container as a cleanup step. No network/account configuration changes were made here.

## Exact manual n8n verification

1. Sign in to the existing localhost:5678 account; create a new workflow and Import from
   File using workflows/n8n/urbaneats_live.json in the same project. Keep prior workflows inactive.
2. Keep this workflow unpublished/inactive; confirm Asia/Kolkata and cron `30 7 * * *`.
3. Inspect Settings: test_mode:true; empty override, force nonce and optional known source.
   Keep API TEST_MODE=true. Leave Slack/Gmail disabled, unbound and CONFIGURE_LOCALLY placeholders.
4. Execute Manual Trigger with the configured current source and inspect its current route,
   prepared/channel/completion audit, and native Data Table. Stale source correctly fails.
5. Use the native verifier below for isolated healthy/GREEN/RED/data failure/outage/malformed,
   duplicate, rate-limit and ambiguous-receipt checks without editing the current source.
6. Preserve claims and TEST_MODE settings after testing. Credential setup, channel-policy
   changes, provider-specific changes and activation require subsequent authorized work.

## Reproducible local verification

```powershell
.venv\Scripts\python.exe scripts/build_workflow.py
.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_tmp_checks
ruff check .
.venv\Scripts\python.exe scripts/security_scan.py
.venv\Scripts\python.exe scripts/verify_notification_integration.py
```

The verifier imports the public node graph with a temporary CLI-only workflow ID, since
n8n CLI import requires an ID. The sanitized public template remains ID-less. Disposable
CLI initialization enables the same native backend modules as n8n start; Data Table storage
is real isolated SQLite. TEST_MODE=false tests replace both send nodes with local Code
mocks. It stops only the API for outage verification and restores it in finally. It never
mounts n8n_data, changes the owner's account, mutates datasets, calls a hosted provider or
sends notifications. Current results: evaluation/results/phase3b1_native_verification.json.
Earlier automation instructions are preserved only in [history](history/README.md).
