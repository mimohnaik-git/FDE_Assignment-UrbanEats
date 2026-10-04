# Final pre-freeze audit

Date: 2026-10-04 (Asia/Calcutta). Release hygiene only; accepted architecture, source, tests, model, dependency versions and validated behavior unchanged.

Branch: `feat/urbaneats-ops-intelligence-rebuild`.
HEAD: `35f814a44e12bc52c9e8aa4bbe476358b5b7b905`.

## Final gates

| Gate | Result |
|---|---|
| python -m pip check | PASS; no broken requirements |
| python -m pytest -q | 148 passed in 39.74 seconds; zero warnings |
| python -m ruff check . | PASS |
| git diff --check | PASS; zero output |
| Current security scan | 0 findings; all current public text and workflow metadata |
| Protected artifact integrity | 48/48 raw SHA256 PASS; expected hashes unchanged |
| Accepted implementation/evidence bytes | Unchanged throughout this pre-freeze pass |
| API health | READY; UE-23c30780e69023fb; model_loaded=true; threshold_loaded=true |
| Canonical workflow | 23 nodes; active=false; TEST_MODE=true; builder equality PASS |
| Workflow safety | No credentials/webhook bindings; CONFIGURE_LOCALLY destinations; disabled send nodes |
| Schedule | 07:30 Asia/Kolkata; cron 30 7 * * * |
| Native verifier evidence | Retained 24/24 PASS; public import PASS; zero real notifications/hosted calls |
| Final canonical n8n execution evidence | Retained GREEN/RED/DATA_FAILURE PASS; zero real notifications/hosted calls |
| Behavioral comparison | Retained 17/17 identical |

Pytest used `--basetemp=.pytest_tmp_prefreeze_final -p no:cacheprovider` to keep temporary files inside the workspace and avoid the previously observed Windows cache-permission warning. Ruff used `--no-cache`; no warning filter, dependency or test change was made.
Existing security evidence was not overwritten; this pass used `scripts/security_scan.py --output docker/local/final_prefreeze/security_scan.json`. Private checker output/logs are ignored. Protected and accepted native/final execution hashes were checked again after cleanup. No native or live acceptance was rerun.

## Retained execution evidence

- [24-case native verification](../evaluation/results/final_native_verification.json).
- [Canonical n8n execution confirmation](../evaluation/results/final_n8n_execution_verification.json).
- [Behavioral comparison](../evaluation/results/final_behavioral_diff.json).

GREEN: one API attempt, Slack SKIPPED_POLICY, Gmail SKIPPED_TEST_MODE. RED: one API attempt, both channels SKIPPED_TEST_MODE. DATA_FAILURE: three HTTP 503 attempts, both channels SKIPPED_TEST_MODE. Each actual n8n execution completed with notification_complete, duplicate=false and empty delivery_error. Disposable containers/network were removed. This pass independently confirmed no verifier containers remain and API TEST_MODE is enabled. Persistent n8n_data was not mounted or mutated.

## Current-document reconciliation

README, RUNTIME, LIVE_AUTOMATION and workflow README now explicitly identify 148 tests, the inactive 23-node design, channel policy, TEST_MODE gates and the final canonical execution evidence. Repeat-check commands write local output paths so accepted evidence remains intact. Local credentials/tokens/private recipients belong in ignored configuration or local n8n bindings, never Git.
FINAL_CODE_REMEDIATION.md retains its remediation-time inventory and now links the subsequent canonical execution confirmation and this current audit. Its original Git-status block is explicitly a historical snapshot. No historical phase report, dataset, notebook, model artifact or verification JSON was edited here.
The model remains exploratory, uncalibrated and conditional Delivered-vs-Cancelled; production_ready=false. GREEN means no supported predicted-risk hotspot, not an observed-business-health or production-quality claim.

## Every modified tracked file

| File | Disposition | Reason |
|---|---|---|
| .env.example | INCLUDE | Safe formatter sample configuration, blank credentials; unused entries removed during remediation. |
| AUDIT.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| README.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| UrbanEats_n8n_workflow.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| artifacts/model/feature_contract.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| artifacts/model/metadata.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| artifacts/model/threshold.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docker/compose.yaml | INCLUDE | Accepted local API deployment and TEST_MODE/environment passthrough; persistent n8n profile remains opt-in. |
| docker/runtime.Dockerfile | INCLUDE | Status metadata only; current raw content equals HEAD. |
| docs/CLEANUP_REPORT.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/LIVE_AUTOMATION.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| docs/N8N_SETUP.md | INCLUDE | Status metadata only; current raw content equals HEAD. |
| docs/PHASE3B_REPORT.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| docs/PHASE3_REPORT.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/REMEDIATION_PLAN.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| docs/RUNTIME.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| docs/history/AUDIT_PHASE1_3.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/LIVE_AUTOMATION_PHASE3_3A.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/PHASE3_3A_REPORT.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/README.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/README_PRE_3B1.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/REMEDIATION_PLAN_PHASE1_3.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| docs/history/RUNTIME_PHASE2_3.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/cleanup_verification.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/local_smoke.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/metrics.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/phase3_docker_smoke.json | INCLUDE | Accepted sanitized verification evidence; frozen bytes retained. |
| evaluation/results/phase3_smoke.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/phase3_verification.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/phase3a_verification.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/phase3b1_native_verification.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/phase3b_verification.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| evaluation/results/security_scan.json | INCLUDE | Accepted sanitized verification evidence; frozen bytes retained. |
| notebooks/original/README.md | INCLUDE | Status metadata only; current raw content equals HEAD. |
| pyproject.toml | INCLUDE | Narrow known upstream-warning filters; dependency settings preserved. |
| requirements.txt | INCLUDE | Status metadata only; current raw content equals HEAD. |
| scripts/build_workflow.py | INCLUDE | Accepted deterministic builder, safety scanning, bounded verification/output-path hardening; no pre-freeze code change. |
| scripts/current_demo.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| scripts/history/README.md | INCLUDE | Status metadata only; current raw content equals HEAD. |
| scripts/history/sanitize_legacy_workflow.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| scripts/security_scan.py | INCLUDE | Accepted deterministic builder, safety scanning, bounded verification/output-path hardening; no pre-freeze code change. |
| scripts/verify_api.py | INCLUDE | Accepted deterministic builder, safety scanning, bounded verification/output-path hardening; no pre-freeze code change. |
| scripts/verify_notification_integration.py | INCLUDE | Accepted deterministic builder, safety scanning, bounded verification/output-path hardening; no pre-freeze code change. |
| src/urbaneats/briefing.py | INCLUDE | Accepted grounded formatting/service remediation; identical before/after behavior, no pre-freeze code change. |
| src/urbaneats/delivery.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| src/urbaneats/evidence.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| src/urbaneats/hotspots.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| src/urbaneats/provider.py | INCLUDE | Accepted grounded formatting/service remediation; identical before/after behavior, no pre-freeze code change. |
| src/urbaneats/run_logging.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| src/urbaneats/service.py | INCLUDE | Accepted grounded formatting/service remediation; identical before/after behavior, no pre-freeze code change. |
| tests/js_runner.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| tests/test_history.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| tests/test_live.py | INCLUDE | Accepted offline regression/receipt/provider coverage; no pre-freeze test change. |
| tests/test_notification.py | INCLUDE | Accepted offline regression/receipt/provider coverage; no pre-freeze test change. |
| tests/test_outage.py | INCLUDE | Status metadata only; current raw content equals HEAD. |
| tests/test_runtime.py | INCLUDE | Accepted offline regression/receipt/provider coverage; no pre-freeze test change. |
| urbaneats_alerts.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| urbaneats_ops_brief.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| workflows/n8n/README.md | INCLUDE | Current operating guidance or explicit historical-phase boundary; preserved phase/recovery content. |
| workflows/n8n/history/README.md | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| workflows/n8n/history/urbaneats_phase3a.json | INCLUDE | Line-ending preservation/recovery only; normalized content equals HEAD. |
| workflows/n8n/notification_logic.cjs | INCLUDE | Accepted 23-node channel policy/receipt implementation; verified canonical unchanged in pre-freeze. |
| workflows/n8n/orchestration_logic.cjs | INCLUDE | Accepted 23-node channel policy/receipt implementation; verified canonical unchanged in pre-freeze. |
| workflows/n8n/urbaneats_live.json | INCLUDE | Accepted 23-node channel policy/receipt implementation; verified canonical unchanged in pre-freeze. |

The working tree already contained accepted phase, remediation and byte-recovery changes relative to HEAD. Raw byte/EOL preservation changes are included deliberately to retain the expected artifact hashes; no broad normalization was performed. Status-only rows have no new raw-content delta to HEAD. These inherited changes are distinguished from the current documentation-only edits.

## Every untracked public candidate

| File | Disposition | Reason |
|---|---|---|
| .gitattributes | INCLUDE | Byte-preservation policy for frozen evidence. |
| docs/FINAL_CODE_REMEDIATION.md | INCLUDE | Current report or accepted phase provenance. |
| docs/PHASE3C1_REPORT.md | INCLUDE | Current report or accepted phase provenance. |
| docs/PHASE3C3_REPORT.md | INCLUDE | Current report or accepted phase provenance. |
| docs/PHASE3C_REPORT.md | INCLUDE | Current report or accepted phase provenance. |
| evaluation/results/final_api_smoke.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/final_behavioral_diff.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/final_n8n_execution_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/final_n8n_security_scan.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/final_native_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/final_security_scan.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c1_native_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c1_protected.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c1_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c3_native_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c_native_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c_protected.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| evaluation/results/phase3c_verification.json | INCLUDE | Accepted sanitized verification/evaluation evidence. |
| src/urbaneats/presentation.py | INCLUDE | Final deterministic channel presentation. |
| tests/test_channel_briefing.py | INCLUDE | Final product-behavior/harness regression coverage. |
| tests/test_formatter_transport.py | INCLUDE | Final product-behavior/harness regression coverage. |
| tests/test_native_verifier.py | INCLUDE | Final product-behavior/harness regression coverage. |
| tests/test_receipts.py | INCLUDE | Final product-behavior/harness regression coverage. |
| docs/PREFREEZE_AUDIT.md | INCLUDE | Current release-hygiene inventory and verified READY_TO_COMMIT gate record. |

INCLUDE means an intended release candidate for the later approved commit; no staging, index update, commit or push occurred. There are no REVIEW_REQUIRED candidates. The three previous phase test filenames were already renamed during remediation; the product-named files preserve their coverage.

## Ignored local-file disposition

| Scope | Disposition | Reason |
|---|---|---|
| .venv/ | IGNORE_LOCAL | Accepted installed environment; reproducible installation content, never a Git candidate. |
| artifacts/ | IGNORE_LOCAL | Trusted pipeline.joblib remains local under the accepted existing distribution/ignore policy; required model hashes are recorded in metadata. Do not retrain or remove. |
| data/ | IGNORE_LOCAL | Current local source batch may contain runtime data; existing ignore rule is intentional. Public input examples/contracts remain tracked. |
| docker/ | IGNORE_LOCAL | Private recovery reports, byte snapshots, baseline patches, audit tools and reproducibility fixtures. May contain historical/local information; ignored and excluded from public scans/build context. Retained for recovery/provenance, not current runtime entry points. |
| evaluation/ | IGNORE_LOCAL | Frozen development_oof.csv and holdout.csv retained locally under existing ignore policy; accepted public metrics/manifests preserve provenance. No regeneration. |
| runs/ | IGNORE_LOCAL | Immutable local API run and delivery claim/audit records; preserve operational state and privacy, never classify as disposable temp. |

Ignored categories were checked against Git ignore rules. The private environment/run/recovery/model content is intentionally outside the commit candidate set; it is not accidentally omitted source. No ignored local file was force-added. Environment secrets and original-history identifier values were never printed.

## Deleted reproducible junk

| Removed target | Category | Files removed | Disposition |
|---|---|---:|---|
| .ruff_cache | PYTEST_RUFF_SCRATCH_CACHE | 7 | DELETE_SAFE_TEMP |
| tests/__pycache__ | PYTHON_BYTECODE_CACHE | 13 | DELETE_SAFE_TEMP |
| scripts/__pycache__ | PYTHON_BYTECODE_CACHE | 3 | DELETE_SAFE_TEMP |
| .pytest_tmp_n8n_final | PYTEST_RUFF_SCRATCH_CACHE | 222 | DELETE_SAFE_TEMP |
| src/urbaneats/__pycache__ | PYTHON_BYTECODE_CACHE | 17 | DELETE_SAFE_TEMP |
| .pytest_tmp_prefreeze_final | PYTEST_RUFF_SCRATCH_CACHE | 222 | DELETE_SAFE_TEMP |
| docker/local/remediation/pytest_cache | PYTEST_RUFF_SCRATCH_CACHE | 4 | DELETE_SAFE_TEMP |
| docker/local/phase3b/native_failure.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/ruff.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/pytest.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/pytest_cache | PYTEST_RUFF_SCRATCH_CACHE | 4 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/security.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/pip_check.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/final_n8n_confirmation/diff_check.log | DISPOSABLE_VERIFIER_LOG | 1 | DELETE_SAFE_TEMP |
| docker/local/remediation/snapshot/src/urbaneats/__pycache__ | PYTHON_BYTECODE_CACHE | 17 | DELETE_SAFE_TEMP |

15 targets / 515 files removed. Each resolved absolute target was checked to stay inside the repository; native PowerShell Remove-Item was used. Accepted evidence, datasets, notebooks, model artifacts, reports, operational runs and recovery reports were preserved. No git clean was used. Post-cleanup scan found no cache/pyc/pytest scratch/editor/OS-temp leftovers outside the retained virtual environment.

## Every root-level entry

| Entry | Purpose |
|---|---|
| .dockerignore | Exclude private/unneeded image context. |
| .env.example | Credential-empty safe configuration template. |
| .git | Git history/index; untouched. |
| .gitattributes | Source LF policy plus frozen raw-byte exceptions. |
| .gitignore | Local/private/generated-file exclusions. |
| .pytest_tmp_n8n_final | DELETE_SAFE_TEMP; removed reproducible scratch/cache |
| .ruff_cache | DELETE_SAFE_TEMP; removed reproducible scratch/cache |
| .venv | Accepted installed environment; IGNORE_LOCAL. |
| artifacts | Frozen trusted model metadata, contract, threshold and local model binary. |
| AUDIT.md | Current architecture audit entry point. |
| data | Input contracts/examples; private current batch ignored, source unchanged. |
| docker | Pinned local deployment; docker/local holds ignored recovery/audit diagnostics. |
| docs | Current contracts/audits and explicit historical reports. |
| evaluation | Reproducibility code and frozen/accepted results; no regeneration. |
| notebooks | Assignment provenance, not runtime. |
| pyproject.toml | Packaging, pytest/Ruff configuration. |
| README.md | Current architecture and operating/verification entry point. |
| requirements-dev.txt | Accepted development pins. |
| requirements.txt | Accepted runtime pins. |
| runs | Local immutable run/delivery audit state; IGNORE_LOCAL, not disposable junk. |
| scripts | Reviewed build/verification/safety entry points and explicit history. |
| src | Production runtime modules. |
| tests | 148 offline regression cases. |
| urbaneats_alerts.json | Preserved assignment dataset/notebook/workflow/output provenance. |
| UrbanEats_classifier_langchain.ipynb | Preserved assignment dataset/notebook/workflow/output provenance. |
| urbaneats_delivery_orders.csv | Preserved assignment dataset/notebook/workflow/output provenance. |
| urbaneats_delivery_orders_scored.csv | Preserved assignment dataset/notebook/workflow/output provenance. |
| UrbanEats_n8n_workflow.json | Preserved assignment dataset/notebook/workflow/output provenance. |
| urbaneats_ops_brief.md | Preserved assignment dataset/notebook/workflow/output provenance. |
| UrbanEats_profiling_gx.ipynb | Preserved assignment dataset/notebook/workflow/output provenance. |
| workflows | Canonical reviewed logic/export and explicit historical graphs. |

No root reorganization was needed. Assignment provenance remains at its accepted paths. Current runtime entry points use src/scripts and the single canonical workflow; archived exports/reports are explicitly historical.

## Duplicate and stale-file audit

Every public candidate was read and hashed; current-facing documentation and Git differences were inspected. No temp/editor/OS file is a release candidate. Old phase counts and reports remain historical rather than being used as current operating evidence. Private byte snapshots and fixture inputs are recovery/reproduction records under docker/local, not competing runtime sources.
Exact duplicate-content groups retained with purpose:

- `data/processed/.gitkeep`, `runs/.gitkeep`: Empty package/retention marker files; each marks its own package or retained directory.

## Remaining technical debt

The exploratory model does not gain production readiness from hygiene or transport verification. Historical reports retain superseded claims by design; current docs identify authoritative evidence. Original Git history/read-only backup may retain historical identifiers; this current-content scan does not rewrite history. n8n claim/audit retention and quota still require an operational policy. The model binary and detailed evaluation CSVs remain under the existing local artifact-distribution policy; a fresh environment must provision the trusted artifact matching recorded hashes. This pass does not retrain or change distribution. CLI import slowness/root-cause uncertainty remains documented; bounded harness execution and cleanup are retained.

## Final Git status

No runtime, workflow, model, dependency or test modification was made during final pre-freeze. Current-facing documentation and this audit are the only public edits in this pass. Accepted files remain uncommitted and intentionally unstaged until approval.

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
?? docs/PREFREEZE_AUDIT.md
?? evaluation/results/final_api_smoke.json
?? evaluation/results/final_behavioral_diff.json
?? evaluation/results/final_n8n_execution_verification.json
?? evaluation/results/final_n8n_security_scan.json
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

READY_TO_COMMIT
