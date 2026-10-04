# Historical Phase-3B verification baseline

Superseded by Phase 3C (23 nodes/channel policy). Counts and behavior below record the
accepted earlier baseline, not current operating instructions. Use PHASE3C_REPORT.md.

# Phase 3B - simplified n8n orchestration

1. **Old node count:** 79 (verified from the Phase-3A export).
2. **New node count:** 22, a reduction of 57 nodes (72%). One Slack send node and one
   Gmail send node handle all statuses. Both remain disabled and credential-unbound.
3. **Consolidation:** removed status switches and six per-status channel chains; replaced
   API/outage-specific delivery claims and logs with one native n8n claim/audit path.
   Normalization builds the unified packet; shared receipt parsing and retry routing
   replace all repeated channel/status logic. No child workflows hide additional nodes.
4. **Final flow:** Schedule/Manual -> Settings -> Call UrbanEats API -> Normalize Response
   (including unified packet) -> Retry API / bounded delay -> Claim Run -> Prepare Audit
   and Gate -> Persist Prepared Audit -> Duplicate and TEST_MODE Gate -> Slack/Gmail ->
   Parse Receipts -> Persist Delivery Audit -> Retry Delivery / bounded delay / Retry
   Channel -> Completed Channel -> Merge Channel Results -> Complete Audit -> Persist
   Completed Audit. Gate skips produce both channel audit records through the same parser.
5. **Safety:** valid API statuses/brief/evidence are preserved verbatim. API business/model/
   formatter behavior is untouched. Unusable responses build deterministic orchestration
   DATA_FAILURE without model facts. Retries retain one execution's history; successful
   retry uses its latest response. Unique database claims persist across n8n processes,
   initial persistence precedes sends, independent channels have separate final states,
   and no ambiguous send is retried. TEST_MODE=true, inactive workflow, unbound credentials,
   Asia/Kolkata and `30 7 * * *` remain the defaults.
6. **Tests/results:** 92 pytest tests pass (including all former 73); two existing dependency
   deprecation warnings. All 17 native CE 2.41.6 executions passed, recorded in
   `evaluation/results/phase3b_verification.json`; delivery tests substitute local Code
   mocks for send nodes and do not contact Slack/Gmail. Ambiguous receipts stayed UNKNOWN
   after one attempt per channel; definite rate limits succeeded on Slack attempt 3/Gmail
   attempt 2. Ruff passed; public security scan has zero findings. The unchanged public
   node graph was separately imported with Docker networking disabled and a temporary
   CLI-only workflow ID. Raw CLI import rejects an ID-less template; UI Import from File
   into a new workflow assigns an instance ID. The public template remains ID-less.
7. **Behavior changes:** n8n now owns delivery claims/audits for all statuses. The API's
   `/delivery` endpoint remains unchanged but is no longer called by this workflow.
   API source identity (batch ID, or source checksum) is hashed into a native claim name,
   preserving same-batch suppression across different API run IDs. A claim covers both
   channels; partial or ambiguous outcomes remain claimed for manual reconciliation.
   TEST_MODE now consumes normal API batch identities as it already did for outages;
   use a fresh source batch or an explicit force nonce for a later credential test.
   Existing Phase-3A outage table names/schema are retained so earlier outage claims
   stay suppressed. Existing API filesystem claims are not migrated: there have been
   no real notifications, and only this inactive workflow should be used after upgrade.
8. **Security:** no credentials, hosted calls, real notifications, activation, publication,
   commits, pushes or history rewrite. Current public scanner includes JSON/JS/CJS.
9. **Import:** `workflows/n8n/urbaneats_live.json` is the only current live workflow export.
   Import into the same existing n8n project, leaving the previous workflow inactive.
   Keep Slack and Gmail disabled/unbound. Settings is a small Code node with `test_mode:true`,
   empty override/force/source fields. Keep API TEST_MODE=true independently. Native
   Data Table claims depend on project identity and preserved n8n_data; do not delete
   claim tables or change project to bypass deduplication. Run Manual Trigger and inspect
   Persist Completed Audit plus the claim table. Bind/enable/send only in later authorized
   credential work; retain 07:30 Kolkata without activating the schedule now.
10. **Readiness: READY FOR CREDENTIAL SETUP.** Native execution and exact-export import
    pass. Production suitability and real OAuth/provider receipts remain outside Phase 3B.

## Why 22 instead of 16

The six additional nodes below preserve the already validated retry and routing properties.
Using unconditional native send retries would retry ambiguous outcomes; dropping durable
logging or either independent channel would reduce reliability. There are no subworkflows.

| Additional node | Required purpose |
|---|---|
| Retry API | Repeat only retryable failures/malformed responses, at most three attempts |
| API Retry Delay | Bound request rate with one-second waits (120-second request timeout) |
| Retry Delivery | Repeat only definite rate-limit rejection, at most three attempts/channel |
| Delivery Retry Delay | Shared two-second delivery retry wait |
| Retry Channel | Return the shared retry loop to the correct single send node |
| Completed Channel | Feed each final channel result to its own merge input |

The other 16 nodes are the two triggers, Settings, request, normalization/packet builder,
native claim, claim/gate preparation, initial audit persistence, duplicate/TEST_MODE gate,
two sends, shared receipt parser, shared delivery persistence, merge, completion builder
and final persistence. API and delivery retries are explicit and countable. Claim/storage
errors block delivery. Monitor native Data Table quota and retain claims when archiving.

## Verification commands

```powershell
.venv\Scripts\python.exe scripts/build_workflow.py
.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_tmp_phase3b
ruff check .
.venv\Scripts\python.exe scripts/security_scan.py
.venv\Scripts\python.exe scripts/verify_notification_integration.py
```

Phase 3B.1 removes the obsolete verifier alias; use scripts/verify_notification_integration.py.
Disposable native CLI initialization uses the same backend modules as n8n start,
with real isolated SQLite Data Tables, no owner recreation and no n8n_data mount.
