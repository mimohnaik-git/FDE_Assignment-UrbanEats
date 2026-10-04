# Current automation - 23-node

Canonical export: workflows/n8n/urbaneats_live.json. n8n Community Edition 2.41.6 is pinned
by digest in Compose and native verification. The current architecture has two triggers,
one Slack send node, one Gmail send node and shared normalization, claims, receipts and
audit. It stays inactive, credential-unbound and TEST_MODE=true at 07:30 Asia/Kolkata.

## Responsibility and flow

The API owns current-source validation, inference, KPIs/supported restaurant-zone hotspots,
evidence/actions, optional hosted formatting, validation and deterministic fallback.
It remains exploratory, uncalibrated and conditional Delivered-vs-Cancelled.

Schedule/Manual → Settings → API → Normalize Response/unified packet → bounded retry →
Claim Run → prepare/persist audit → duplicate/TEST_MODE gate → Slack/Gmail → parse receipts →
persist delivery audit → bounded retry/channel routing → merged completion audit.
[Phase 3C report](PHASE3C_REPORT.md) explains the policy gate: 22 → 23 nodes, below the 24-node limit.

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
6. Preserve claims and TEST_MODE settings after testing. Credential setup, live provider/credential calls and activation require subsequent authorized work.

## Reproducible local verification

```powershell
.venv\Scripts\python.exe scripts/build_workflow.py --output docker/local/remediation/builder_check.json
.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_tmp_checks
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe scripts/security_scan.py --output docker/local/checks/security_scan.json
.venv\Scripts\python.exe scripts/verify_notification_integration.py --output docker/local/checks/native_verification.json
```

The verifier imports the public node graph with a temporary CLI-only workflow ID, since
n8n CLI import requires an ID. The sanitized public template remains ID-less. Disposable
CLI initialization enables the same native backend modules as n8n start; Data Table storage
is real isolated SQLite. TEST_MODE=false tests replace both send nodes with local Code
mocks. It stops only the API for outage verification and restores it in finally. It never
mounts n8n_data, changes the owner's account, mutates datasets, calls a hosted provider or
sends notifications. Final verification: evaluation/results/final_native_verification.json. Historical phase results remain unchanged.
Earlier automation instructions are preserved only in [history](history/README.md).

## Channel policy and presentation

| Status | Slack | Gmail |
|---|---|---|
| GREEN_SUMMARY | SKIPPED_POLICY, zero attempts | Required |
| RED_ALERT | Required | Required |
| DATA_FAILURE, including independent outage | Required | Required |

Policy skips take precedence for an unrequired Slack channel, including TEST_MODE and
repeated GREEN runs. Required channels distinguish SKIPPED_TEST_MODE and DUPLICATE_SUPPRESSED.
SUCCESS/FAILURE/UNKNOWN remain independent, and policy skip is never failure. One additional
Slack Required gate reuses the shared receipt/audit path; no per-status send branches exist.

The API adds briefing.channels presentation fields outside the evidence schema. Slack RED
contains supported hotspot fractions, approved actions and citations/provenance; GREEN has
no Slack message. Gmail retains fuller batch/support/evidence content with subject, source,
run/batch/model/timestamp and the explicit exploratory model limitation. DATA_FAILURE has
stage/category, system review, provenance and failure citation; orchestration outage uses
its independent deterministic brief without invented model evidence. No email dumps raw JSON.

## Groq preparation — no live request authorized here

Set LLM_PROVIDER=groq only for later authorized local configuration. GROQ_API_KEY is read
only from the environment (ignored .env); GROQ_BASE_URL supplies the HTTPS compatible API
prefix, and GROQ_MODEL supplies the locally chosen model. Docker passes these variables;
all defaults are empty. Groq never falls back to LLM_API_KEY. Do not put secrets in workflow,
docs/tests/results, or change TEST_MODE in this phase. No provider dependency was added.

The formatter receives canonical evidence/actions, routing and provenance plus deterministic
briefing. Its strict JSON items must copy canonical sentences with exact [evidence:ID]
citations and approved action IDs. It may reorder them; arbitrary rephrasing or causal advice
is deliberately disallowed. Required batch/supported-hotspot citations cannot be dropped.
Routing/provenance/model-language is system-rendered, never provider-controlled. Invalid,
empty, unavailable or malformed output uses deterministic fallback and retains valid routing
and notification delivery. TEST_MODE blocks hosted transport even when configuration exists.

For GPT-OSS strict-schema request details, safe fallback diagnostics and portable message
text, see [Phase 3C.1 repair](PHASE3C1_REPORT.md). No further live call is authorized by that report.

## Receipt reconciliation

Slack node 2.3 success requires ok:true, a non-empty channel, and a non-empty
message_timestamp (or message.ts fallback). Top-level ts alone is unverified.
A disabled send node's exact unchanged upstream audit object is not a send receipt,
including its Data Table row id: attempts stay zero, state UNKNOWN, category
CHANNEL_NOT_SENT, event delivery_not_sent. This preserves existing channel states.
Required UNKNOWN channels produce notification_unverified; terminal verified failures
produce notification_failed; successful/intentional-skip outcomes retain notification_complete.
Claims remain held and ambiguous/unverified outcomes never retry automatically.
Slack otherOptions.includeLinkToWorkflow=false disables supported n8n attribution.
See [Phase 3C.3 report](PHASE3C3_REPORT.md). No live sends are authorized by this documentation.

## Final accepted verification

148 pytest cases pass with zero warnings. The unchanged canonical 23-node graph imported
and executed GREEN_SUMMARY, RED_ALERT and DATA_FAILURE in disposable isolated n8n state.
TEST_MODE=true kept required channels SKIPPED_TEST_MODE; GREEN Slack was SKIPPED_POLICY.
DATA_FAILURE stopped after three HTTP 503 attempts; every run completed without delivery
errors. [Execution evidence](../evaluation/results/final_n8n_execution_verification.json)
and [pre-freeze audit](PREFREEZE_AUDIT.md) supersede historical phase counts.
Model `UE-23c30780e69023fb` remains exploratory, uncalibrated and conditional; no production
claim follows from transport verification. Credentials stay in ignored private configuration
or local n8n bindings and must never enter Git. Existing final evidence must not be overwritten
by repeat checks; use a new local output path.
