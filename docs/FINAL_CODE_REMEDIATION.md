# Final code remediation and pre-freeze audit

Original assignment: `c62430075fc5ccaaa5db487a7556d531ac128c63`. Starting/current HEAD: `35f814a44e12bc52c9e8aa4bbe476358b5b7b905`.

## Evolution and authority

The original eight-node workflow fetched historical scored CSV and split RED/GREEN into separate Slack/Gmail chains. The notebooks were exploratory assignment code, not the runtime.
Phase 1 identified malformed-input all-clear risk, leakage and missing reproducibility. Phase 2 established placement validation, frozen model loading, evidence, cited briefing and tests. Phase 3 provided API/Docker orchestration; 3A added independent outage reporting and native persistence. Phase 3B consolidated the 79-node transitional graph into 22 nodes; 3B.1 reconciled exports and history. Phase 3C added the Gmail-all/Slack-RED-and-failure policy and canonical formatting (23 nodes). 3C.1 repaired GPT-OSS envelope/fallback compatibility. There is no separately stored 3C.2 report; no missing phase commit or acceptance is invented. 3C.3 corrected native Slack receipts, disabled-node pass-through handling and unverified completion; its hardened harness and historical 24-case PASS are retained.
Git history contains assignment and reconciliation boundaries, not an independent commit for every phase. Reverse log, log stat and baseline diff were inspected privately; original identifiers are never reproduced here.
Final validated contracts govern this review; older phase reports are provenance. Current source was independently inspected rather than restored to a phase snapshot.

## Refactoring and responsibility

- briefing.py now owns one canonical cited-item construction and one required-citation policy. Hosted prompts and deterministic rendering use the same canonical items; sentence computation is once per packet rather than once per fact.
- Removed unused FormatterProvider protocol and its typing import: no callers, annotations, exports or tests referenced it. Provider injection remains structural through generate().
- service.py merges two consecutive success-result updates and replaces the obsolete scaffold docstring; failure branches and response fields remain unchanged.
- Provider transport remains in provider.py; evidence validation/fallback stays at the briefing boundary for injectable providers as well as hosted providers. Moving these interfaces solely for file naming would add coupling without a behavioral benefit.
- Builder, scanner, API smoke and native verifier accept explicit output paths so checks preserve frozen historical evidence. Existing defaults remain compatible. Verifier checks API TEST_MODE before creating containers.
- Removed unused sample variables URBANEATS_LLM_MODE, SLACK_CHANNEL and GMAIL_RECIPIENT: reference search found only declarations. Provider selection uses LLM_PROVIDER; notification destinations bind locally in n8n. Private configuration is untouched.
- Current docs remove stale phase architecture/result pointers and distinguish portable defaults from private local configuration.

## Removed and retained code

No runtime module, compatibility endpoint, dataset, notebook or historical evidence file was deleted. Repeated formatter item construction and mandatory-citation expressions were consolidated; the dead protocol was removed. Previously eliminated per-status workflow chains remain historical only.
The /delivery endpoint is retained because it remains a public, tested filesystem-claim API. Its persistence boundary differs from n8n Data Tables. Orchestration outage helpers and unified notification helpers are both required; the latter calls the former. Node exports support offline tests; embedded copies are generated runtime content, not independently maintained business logic. Evaluation code remains the reproducibility source and was not executed. Configurable compatible-provider support is retained as a tested interface; Groq has separate key selection.

## Workflow source of truth

orchestration_logic.cjs + notification_logic.cjs → build_workflow.py → canonical urbaneats_live.json → native verification. Private builder output equals canonical JSON structurally and deterministically. Canonical bytes and JS source are unchanged in this pass.
23 nodes; active=false; Asia/Kolkata; cron 30 7 * * *; TEST_MODE=true; one disabled/unbound Slack and Gmail node; no credential/webhook bindings.
Final canonical SHA256: `1f1b1a4f3c3431c9c79dfcf0f98cae01fc29682f1fb71165f214540ffe2ba52b`.
The instructions allow workflow implementation changes but also require all 48 protected bytes. No canonical change was needed, so both requirements are satisfied. Historical Phase 3C.3 evidence is untouched; final_native_verification.json is a new execution artifact.

## Verifier hardening and diagnostics

Docker commands default to 30 seconds; initialization/import/execute use 120 seconds. Explicit stages cover setup/import/cases/recovery/cleanup. Timeout failures retain completed cases, precise stage, FAIL/INTERRUPTED and cleanup results. Import markers distinguish IMPORT_FAILED, IMPORT_TIMEOUT and PROCESS_EXIT_TIMEOUT when successful import precedes a shutdown timeout. Raw failure logs remain under ignored docker/local; public diagnostics expose only allowlisted milestones, sizes and hashes. No repeated import/send is added automatically.
The original interrupted import root cause remains unproven; prior exit 137 with no OOM event does not establish initialization/import/shutdown causality. This run reports actual stages rather than guessing. The disposable execute-module initialization workaround remains necessary for native Data Table modules in pinned n8n 2.41.6.

## Tests and behavioral comparison

146 → 148 tests. No existing case removed. File mapping: test_phase3c.py → test_channel_briefing.py; test_phase3c1.py → test_formatter_transport.py; test_phase3c3.py → test_receipts.py. Test functions and parametrizations are unchanged. Two new tests prove unsafe API preflight blocks container creation and explicit interrupted output preserves historical PASS bytes.
17 recovered-snapshot/current comparisons are equal: RED, GREEN, support 19/20, invalid/leaking/stale input, READY/missing-artifact health, missing-model failure, valid reordered formatter output, rejected/unavailable fallback, and mocked Groq strict/generic request envelopes. Run UUID/time are controlled; entire responses and requests match. Hosted transport is MockTransport only. Existing tests independently cover receipts, retries, duplicate suppression, citations and workflow safety.
Initial pytest default-temp setup failed with Windows permissions; workspace-local basetemp resolved all errors. A stale cache permission warning prompted a fresh local cache for the final run; no dependency or warning-filter change was made.

## Verification gates

- pip check: PASS; no broken requirements.
- pytest: 148 passed in 44.28 seconds; zero warnings using workspace basetemp and a fresh local cache.
- Ruff: PASS.
- git diff --check: PASS, zero output (final gate required after this report).
- Protected raw integrity: 48/48 PASS; expected hashes, metrics/fingerprints and historical evidence unchanged.
- Security: 0 current findings; new final_security_scan.json preserves historical security_scan.json.
- API Docker smoke: PASS on port 8000; READY, UE-23c30780e69023fb, model_loaded=true, threshold_loaded=true; DATA_FAILURE/GREEN/RED routes; zero external calls. Historical smoke evidence unchanged.
- Native: PASS; 24/24 cases; see new final_native_verification.json.
- Behavioral diff: PASS, 17 comparisons; no unintended contract change.

Saved model/feature/threshold artifacts, placement feature contract, minimum support 20, strict hotspot fraction, predicted-risk interpretation, MANUAL_REVIEW, citation IDs and detached formatter input remain unchanged. Synthetic demo input was used for isolated inference only; no training/evaluation regeneration occurred. Dependencies and byte-preservation attributes match the recovered starting inventory.

## Module size and function counts

| Module | LOC before → after | Functions before → after |
|---|---|---|
| src/urbaneats/service.py | 342 → 339 | 8 → 8 |
| src/urbaneats/briefing.py | 183 → 182 | 8 → 9 |
| src/urbaneats/provider.py | 107 → 100 | 3 → 3 |
| src/urbaneats/presentation.py | 41 → 41 | 1 → 1 |
| scripts/build_workflow.py | 148 → 155 | 7 → 7 |
| scripts/security_scan.py | 58 → 63 | 1 → 1 |
| scripts/verify_notification_integration.py | 399 → 410 | 9 → 9 |
| workflows/n8n/notification_logic.cjs | 148 → 148 | 6 → 6 |
| workflows/n8n/orchestration_logic.cjs | 68 → 68 | 3 → 3 |

Counts include all physical lines and nested functions; no compression solely to reduce LOC.

Eight reproducible cache directories were removed after checking each absolute path remained inside the repository. Private recovery/remediation evidence was retained; no Git clean was used.

## File-by-file disposition

| File | Classification | Reason |
|---|---|---|
| .dockerignore | FINAL_REQUIRED | Current documentation or repository/build policy. |
| .env.example | FINAL_REQUIRED | Current documentation or repository/build policy. |
| .gitattributes | FINAL_REQUIRED | Current documentation or repository/build policy. |
| .gitignore | FINAL_REQUIRED | Current documentation or repository/build policy. |
| AUDIT.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| README.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| UrbanEats_classifier_langchain.ipynb | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| UrbanEats_n8n_workflow.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| UrbanEats_profiling_gx.ipynb | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| artifacts/model/feature_contract.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| artifacts/model/metadata.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| artifacts/model/threshold.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| data/processed/.gitkeep | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| data/raw/README.md | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| docker/compose.yaml | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| docker/runtime.Dockerfile | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| docs/CLEANUP_REPORT.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/EVALUATION.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/FEATURE_CONTRACT.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/FINAL_CODE_REMEDIATION.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/LIVE_AUTOMATION.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/N8N_SETUP.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/PHASE3B_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/PHASE3C1_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/PHASE3C3_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/PHASE3C_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/PHASE3_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/REMEDIATION_PLAN.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/RUNTIME.md | FINAL_REQUIRED | Current documentation or repository/build policy. |
| docs/history/AUDIT_PHASE1_3.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/LIVE_AUTOMATION_PHASE3_3A.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/PHASE3_3A_REPORT.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/README.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/README_PRE_3B1.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/REMEDIATION_PLAN_PHASE1_3.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| docs/history/RUNTIME_PHASE2_3.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/__init__.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/evaluate.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/cleanup_verification.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/final_api_smoke.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/final_behavioral_diff.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/final_native_verification.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/final_security_scan.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/local_smoke.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/metrics.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/phase3_docker_smoke.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3_smoke.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3a_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3b1_native_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3b_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c1_native_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c1_protected.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c1_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c3_native_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c_native_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c_protected.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/phase3c_verification.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| evaluation/results/security_scan.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| evaluation/results/verification.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| notebooks/original/README.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| pyproject.toml | FINAL_REQUIRED | Current documentation or repository/build policy. |
| requirements-dev.txt | FINAL_REQUIRED | Current documentation or repository/build policy. |
| requirements.txt | FINAL_REQUIRED | Current documentation or repository/build policy. |
| runs/.gitkeep | FINAL_REQUIRED | Current documentation or repository/build policy. |
| scripts/build_workflow.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| scripts/current_demo.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| scripts/history/README.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| scripts/history/sanitize_legacy_workflow.py | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| scripts/security_scan.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| scripts/verify_api.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| scripts/verify_notification_integration.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/__init__.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/actions.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/briefing.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/config.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/delivery.py | REQUIRED_COMPATIBILITY | Public /delivery endpoint uses filesystem claims; native workflow uses isolated Data Tables. |
| src/urbaneats/evidence.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/features.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/hotspots.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/inference.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/metrics.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/model.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/presentation.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/provider.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/run_logging.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/schemas.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/service.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| src/urbaneats/validation.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/conftest.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/js_runner.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_channel_briefing.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_evaluation.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_formatter_transport.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_history.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_live.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_model.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_native_verifier.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_notification.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_outage.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_receipts.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| tests/test_runtime.py | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| urbaneats_alerts.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| urbaneats_delivery_orders.csv | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| urbaneats_delivery_orders_scored.csv | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| urbaneats_ops_brief.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| workflows/n8n/README.md | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| workflows/n8n/history/README.md | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| workflows/n8n/history/urbaneats_core_scaffold.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| workflows/n8n/history/urbaneats_phase3a.json | HISTORICAL | Assignment/phase provenance; retained, outside current runtime entry points. |
| workflows/n8n/notification_logic.cjs | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| workflows/n8n/orchestration_logic.cjs | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |
| workflows/n8n/urbaneats_live.json | FINAL_REQUIRED | Current implementation, regression coverage, reproducibility, or operating artifact. |

## Files changed relative to recovered start

- `.env.example`
- `AUDIT.md`
- `README.md`
- `docs/FINAL_CODE_REMEDIATION.md`
- `docs/LIVE_AUTOMATION.md`
- `docs/REMEDIATION_PLAN.md`
- `docs/RUNTIME.md`
- `evaluation/results/final_api_smoke.json`
- `evaluation/results/final_behavioral_diff.json`
- `evaluation/results/final_native_verification.json`
- `evaluation/results/final_security_scan.json`
- `scripts/build_workflow.py`
- `scripts/security_scan.py`
- `scripts/verify_api.py`
- `scripts/verify_notification_integration.py`
- `src/urbaneats/briefing.py`
- `src/urbaneats/provider.py`
- `src/urbaneats/service.py`
- `tests/test_channel_briefing.py`
- `tests/test_formatter_transport.py`
- `tests/test_native_verifier.py`
- `tests/test_receipts.py`
- `workflows/n8n/README.md`

Removed paths are the three renamed test files only:
- `tests/test_phase3c.py`
- `tests/test_phase3c1.py`
- `tests/test_phase3c3.py`

## Root and local-content audit

Root CSVs/notebooks/alerts/brief/original workflow are historical provenance; README/AUDIT/config are current policy. artifacts and evaluation preserve trusted state; data is input/reproducibility; src/scripts/tests/workflows are implementation; docs is current guidance plus explicitly preserved history. .git is version control; .venv is the accepted environment; runs is local audit state. docker/local contains recovery and remediation diagnostics and is IGNORE_LOCAL. Cache directories/pyc are DELETE_SAFE_TEMP only when reproducible and contained in the workspace; no git clean is used. Native verifier fixtures and logs are retained locally for diagnostics, not added to Git.

## Untracked candidate disposition

| File | Disposition |
|---|---|
| .gitattributes | INCLUDE |
| docs/FINAL_CODE_REMEDIATION.md | INCLUDE |
| docs/PHASE3C1_REPORT.md | INCLUDE |
| docs/PHASE3C3_REPORT.md | INCLUDE |
| docs/PHASE3C_REPORT.md | INCLUDE |
| evaluation/results/final_api_smoke.json | INCLUDE |
| evaluation/results/final_behavioral_diff.json | INCLUDE |
| evaluation/results/final_native_verification.json | INCLUDE |
| evaluation/results/final_security_scan.json | INCLUDE |
| evaluation/results/phase3c1_native_verification.json | INCLUDE |
| evaluation/results/phase3c1_protected.json | INCLUDE |
| evaluation/results/phase3c1_verification.json | INCLUDE |
| evaluation/results/phase3c3_native_verification.json | INCLUDE |
| evaluation/results/phase3c_native_verification.json | INCLUDE |
| evaluation/results/phase3c_protected.json | INCLUDE |
| evaluation/results/phase3c_verification.json | INCLUDE |
| src/urbaneats/presentation.py | INCLUDE |
| tests/test_channel_briefing.py | INCLUDE |
| tests/test_formatter_transport.py | INCLUDE |
| tests/test_native_verifier.py | INCLUDE |
| tests/test_receipts.py | INCLUDE |

No untracked candidate is deleted on uncertainty. Ignored environment keys, runs, model binary and private diagnostic snapshots remain IGNORE_LOCAL; existing model distribution strategy is retained.

## Remaining technical debt and limits

The saved model is exploratory and not production-ready. Historical reports include superseded operating claims; current docs link them as history. No separately versioned intermediate phase commits exist. CLI import is slow and the original stall cause remains unproven; bounded diagnostics are retained. The current Docker image was smoke-tested without deployment changes; local refactored source was separately tested and compared. Public security scan does not rewrite original Git history; historical exposure is recorded without printing identifiers. Local run/claim retention and n8n quota still need an operational policy. No unknown code or private diagnostic was deleted.

## Final Git status

The working tree already contained extensive accepted phase/recovery changes at start. This pass does not claim those changes as newly authored. No staging, commit, push, merge, tag, activation or live acceptance occurred.

```text
## feat/urbaneats-ops-intelligence-rebuild
 M .env.example
 M AUDIT.md
 M README.md
 M UrbanEats_n8n_workflow.json
 M artifacts/model/feature_contract.json
 M artifacts/model/metadata.json
 M artifacts/model/threshold.json
 M docker/compose.yaml
 M docker/runtime.Dockerfile
 M docs/CLEANUP_REPORT.md
 M docs/LIVE_AUTOMATION.md
 M docs/N8N_SETUP.md
 M docs/PHASE3B_REPORT.md
 M docs/PHASE3_REPORT.md
 M docs/REMEDIATION_PLAN.md
 M docs/RUNTIME.md
 M docs/history/AUDIT_PHASE1_3.md
 M docs/history/LIVE_AUTOMATION_PHASE3_3A.md
 M docs/history/PHASE3_3A_REPORT.md
 M docs/history/README.md
 M docs/history/README_PRE_3B1.md
 M docs/history/REMEDIATION_PLAN_PHASE1_3.md
 M docs/history/RUNTIME_PHASE2_3.md
 M evaluation/results/cleanup_verification.json
 M evaluation/results/local_smoke.json
 M evaluation/results/metrics.json
 M evaluation/results/phase3_docker_smoke.json
 M evaluation/results/phase3_smoke.json
 M evaluation/results/phase3_verification.json
 M evaluation/results/phase3a_verification.json
 M evaluation/results/phase3b1_native_verification.json
 M evaluation/results/phase3b_verification.json
 M evaluation/results/security_scan.json
 M notebooks/original/README.md
 M pyproject.toml
 M requirements.txt
 M scripts/build_workflow.py
 M scripts/current_demo.py
 M scripts/history/README.md
 M scripts/history/sanitize_legacy_workflow.py
 M scripts/security_scan.py
 M scripts/verify_api.py
 M scripts/verify_notification_integration.py
 M src/urbaneats/briefing.py
 M src/urbaneats/delivery.py
 M src/urbaneats/evidence.py
 M src/urbaneats/hotspots.py
 M src/urbaneats/provider.py
 M src/urbaneats/run_logging.py
 M src/urbaneats/service.py
 M tests/js_runner.py
 M tests/test_history.py
 M tests/test_live.py
 M tests/test_notification.py
 M tests/test_outage.py
 M tests/test_runtime.py
 M urbaneats_alerts.json
 M urbaneats_ops_brief.md
 M workflows/n8n/README.md
 M workflows/n8n/history/README.md
 M workflows/n8n/history/urbaneats_phase3a.json
 M workflows/n8n/notification_logic.cjs
 M workflows/n8n/orchestration_logic.cjs
 M workflows/n8n/urbaneats_live.json
?? .gitattributes
?? docs/FINAL_CODE_REMEDIATION.md
?? docs/PHASE3C1_REPORT.md
?? docs/PHASE3C3_REPORT.md
?? docs/PHASE3C_REPORT.md
?? evaluation/results/final_api_smoke.json
?? evaluation/results/final_behavioral_diff.json
?? evaluation/results/final_native_verification.json
?? evaluation/results/final_security_scan.json
?? evaluation/results/phase3c1_native_verification.json
?? evaluation/results/phase3c1_protected.json
?? evaluation/results/phase3c1_verification.json
?? evaluation/results/phase3c3_native_verification.json
?? evaluation/results/phase3c_native_verification.json
?? evaluation/results/phase3c_protected.json
?? evaluation/results/phase3c_verification.json
?? src/urbaneats/presentation.py
?? tests/test_channel_briefing.py
?? tests/test_formatter_transport.py
?? tests/test_native_verifier.py
?? tests/test_receipts.py
```

CODE_REMEDIATION_COMPLETE

READY_FOR_FINAL_PREFREEZE

## Subsequent execution confirmation and release hygiene

The final canonical graph subsequently passed actual isolated n8n GREEN_SUMMARY, RED_ALERT
and DATA_FAILURE executions; see [retained execution evidence](../evaluation/results/final_n8n_execution_verification.json).
The graph remained 23 nodes, inactive and TEST_MODE=true, without credential bindings.
Each run completed without delivery errors or real notifications/hosted requests.
DATA_FAILURE preserved the three-attempt HTTP 503 bound. Post-execution regression was
148 passing tests with zero warnings; integrity 48/48 and security zero findings.
The Git inventory above records remediation-time state. The current release inventory,
remaining local-file dispositions and commit-readiness gates are in [PREFREEZE_AUDIT.md](PREFREEZE_AUDIT.md).
