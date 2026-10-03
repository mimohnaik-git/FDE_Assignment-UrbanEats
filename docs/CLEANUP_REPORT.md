# Phase 3B.1 cleanup and reconciliation audit

Cleanup only: the accepted 22-node Phase-3B behavior is unchanged. No Phase 3C policy/provider
changes, credentials, dependency additions, external calls, notifications, commits or pushes.

## Audit before removal

154 files were inventoried excluding Git, environment/cache internals and local API run state;
83 were public/project files and 71 were ignored verification artifacts. 40 protected files
were hashed before changes: every src module, datasets/current source, saved artifact/threshold,
feature/evaluation contract and metrics, supplied notebooks/CSVs/alerts/brief/root workflow,
requirements, environment example and Docker configuration. All 40 hashes still match.
The before inventory and hashes are retained in evaluation/results/cleanup_verification.json.

## Kept

All src API/runtime/model/evidence/formatter/delivery code, model artifacts, feature and
prediction-point contracts, thresholds, datasets, evaluation modules and result evidence,
Docker configuration/dependencies, original supplied assignment artifacts, and all 92 test
cases. The compatibility API delivery endpoint remains tested and unchanged. Original baseline
Git provenance remains intact. Current notebook bytes are preserved; pre-cleanup public
sanitization must not be confused with untouched original baseline bytes.

Active tooling: scripts/build_workflow.py, current_demo.py, verify_api.py, security_scan.py,
verify_notification_integration.py. Active helpers: orchestration_logic.cjs and
notification_logic.cjs. One shared tests/js_runner.py replaces three duplicate Node bridges.

## Removed, renamed and archived

| Previous path/code | Action and rationale |
|---|---|
| scripts/verify_outage_integration.py | Removed unused alias; one native verifier now owns Phase 3B checks |
| scripts/smoke_test.py | Removed duplicate narrower smoke script; verify_api.py and native tests retain API coverage |
| scripts/build_outage_workflow.py | Renamed build_workflow.py; it generates only current Phase 3B |
| scripts/phase3_smoke.py | Renamed verify_api.py; regression scope includes the retained API delivery endpoint |
| workflows/n8n/outage_logic.cjs | Renamed orchestration_logic.cjs; three live transport/identity/outage helpers kept verbatim |
| claimOutage, outageAuditRow, outageDeliveryRow | Removed uncalled superseded functions from helper and embedded workflow code; outage tests migrated to live Phase-3B claim/receipt code |
| scripts/sanitize_legacy_workflow.py | Archived scripts/history/ as one-time assignment provenance utility |
| tests/test_scaffold.py | Renamed test_history.py; retained historical sanitization tests |
| workflows/n8n/urbaneats_core_scaffold.json | Archived workflows/n8n/history/; not a current export |
| ignored Phase-3A workflow snapshot | Preserved sanitized workflows/n8n/history/urbaneats_phase3a.json; no builder or activation |
| README, AUDIT, RUNTIME, LIVE_AUTOMATION, REMEDIATION_PLAN, PHASE3_REPORT prior content | Snapshots preserved in docs/history/; current entry points now describe only accepted Phase 3B |
| Ignored obsolete/recreated verification artifacts | Removed after checking they are generated test files, not real API runs, datasets or n8n_data; per-file rationale below |

No runtime file was deleted. Local API runs/claims under runs/ and native n8n_data were
not cleaned or recreated. Removing mock retryrun claims below does not remove real claims.
Normal tooling environments/caches remain ignored; generated pytest scratch directories
were removed only after tests finished. The current verifier regenerates its disposable fixtures.

## Modified

Canonical JSON (uncalled definitions removed only), renamed builder/core helper, notification
module's core import, native verifier (isolated /process-batch request fixtures replace current
source writes; results go to a new Phase-3B.1 file), migrated outage tests/shared JS test bridge,
security scanner (includes archived workflow metadata), current README/AUDIT/runtime/automation/
plan/setup references, Phase-3B report command names and provenance READMEs. Original Phase-3B
and earlier result files are retained; new evidence is written separately.

## Surface and behavior proof

- Current workflow exports: 2 → 1; 22 nodes → 22 nodes. Two graphs are explicitly historical.
- Active top-level Python tools: 8 → 5; obsolete aliases/duplicate script removed or archived.
- Three dead helper functions removed; three duplicate Node test bridges consolidated.
- Mixed historical/current instructions replaced with current docs plus labeled snapshots.
- Workflow object equality holds after subtracting exactly the three uncalled definitions:
  node names/types/parameters, connections, schedule, active JS statements and settings match.
- TEST_MODE=true, inactive state, one disabled/unbound Slack/Gmail node each, 07:30
  Asia/Kolkata, outage fail-closed, persistent idempotency and bounded retry semantics match.
- Exploratory, uncalibrated, conditional Delivered-vs-Cancelled; production_ready=false.
  No production-quality claim or hotspot/evidence policy change.

## Verification

92 pytest tests passed; two existing dependency deprecation warnings. Ruff and git diff
--check pass. All 17 isolated native n8n 2.41.6 execution cases pass: API DATA_FAILURE/GREEN/
RED, stopped API, refusal/DNS/timeout/500/503/malformed/prior-RED-body rejection, duplicate
suppression, TEST_MODE skips, definite rate-limit retries and ambiguous UNKNOWN receipts.
The public node graph imports with a temporary CLI-only ID; public export stays sanitized.
API recovered READY with model/threshold loaded; existing n8n account/container/volume are
preserved. Source data/current_batch.json is hash-identical: native tests now submit local
request fixtures without overwriting it. Secret scan has zero findings including historical
workflow metadata. Current references/imports resolve; historical old names are labeled history.

Evidence: evaluation/results/cleanup_verification.json and phase3b1_native_verification.json.
Remaining inactive history is intentional provenance; no identified live dead/stale artifacts.
Phase 3C remains deferred. **READY FOR PHASE 3C** after final cleanup checks.

## Per-file ignored artifact deletion rationale

All targets were resolved and checked to remain inside this workspace before deletion.

| Deleted generated path | Rationale |
|---|---|
| docker/local/phase3_before_3a.json | Duplicate obsolete backup; current builder/verifier and historical graph/report retained |
| docker/local/summarize-duplicate.js | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/summarize-retry.js | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/summarize.js | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/verify-n8n.sh | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/verify-retry.sh | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/workflow_retry.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/workflow_test.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/fixtures/failure.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/fixtures/green.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/fixtures/red.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3a/dns.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/healthy.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/http500.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/http503.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/initialize_cli.cjs | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/malformed.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/mock_transport.py | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/native_failure.log | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/prior_red_body.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/recovery.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/refused.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/stopped_api.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/summarize.cjs | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3a/timeout.json | Superseded native test fixture/diagnostic; sanitized Phase-3A results/graph retained |
| docker/local/phase3b/build_phase3a.py | Duplicate obsolete backup; current builder/verifier and historical graph/report retained |
| docker/local/phase3b/data_failure.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/dns.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/green.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/healthy.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/http500.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/http503.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/initialize_cli.cjs | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/malformed.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/mock_retry.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/mock_transport.py | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/mock_unknown.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/phase3a.json | Duplicate obsolete backup; current builder/verifier and historical graph/report retained |
| docker/local/phase3b/prior_red_body.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/public.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/recovery.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/refused.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/stopped_api.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/summarize.cjs | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/timeout.json | Reproducible disposable test fixture/script; current native verifier and sanitized results retained |
| docker/local/phase3b/verify_phase3a.py | Duplicate obsolete backup; current builder/verifier and historical graph/report retained |
| docker/local/retryruns/UE-253f737a2caa44b497e75ebf4ab6e5db.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/UE-4fc74e8049a6470bad29bb017bcb591e.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/UE-98b23226fd1349129151d362636271a3.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/21db58b1e2ce494d860d52445abf679d.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/27fad85268744b0392b26fbc33c4aee1.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/2b2bdc08e7de4c8fbc4578b6f9efd8e6.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/335d26b5313fdfb2d71b5103637afd5d96255f89dde3a143d4ec50c9480bd3f8.claim | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/4e457950e2cd4991aacab027745eb61f.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/529a57066ab84c3b92011fa01785398c.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/53ef972bb0b5288870e8a1eaf9d9dee1d7137ecd54c48e4dfd35000ceb360b16.claim | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/54b9c445505f4a1581968f49017be5b5.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/69e0c36ba51c2a01f96230bf39bd164f181b58a1f44a1c2571f95449c2d4a43a.claim | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/6d81dee5b5cf8f021e69efe327f5bb0854cb7f0d7b8dc11e1cbded7ce0c8dee7.claim | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/72a4d6e614654255a0904c3c2e6b104a.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/78a3cd02b40c433cb6d092d8c72601c9.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/797ea25b5cd6470492bd5689b52bafd3.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/89ff4faaaf7d41eeaa9a13cefe196421.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/8f273c2fc2d84b1592f3a26771fdf72c.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/944f3df3a728409088af149ff6e28574.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/a152bf4f4db04d82973f9ecd823c1fde.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/a47cf08846174d269a096d4dce369db2.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/ac2347b3c0384f2bb5b989467cfdb811.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/adb8a1b1d8a74babb19279cf09e8b8f6.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/d48c4267852d4cbb8bc7f936072f66fa.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
| docker/local/retryruns/delivery/f2fc13c2cd00471d84784667c101e9ae.json | Generated isolated mock run/claim state; actual runs and n8n_data preserved |
