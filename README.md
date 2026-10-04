# UrbanEats — placement-time operations intelligence

The runtime uses the **23-node** n8n workflow:

latest placement batch → validation → saved-model inference → supported restaurant-zone
hotspots → evidence + approved actions → deterministic/LLM-ready briefing → n8n
orchestration → Slack/Gmail → persistent delivery audit.

The API owns validation, inference, KPIs/hotspots, evidence/actions, optional compatible
hosted formatting, factual validation and deterministic fallback. n8n owns the triggers,
API invocation, independent outage DATA_FAILURE, persistent claims, TEST_MODE gate,
one Slack node (RED/failure only), one Gmail node (all statuses), receipt handling and delivery audit.

The workflow is inactive, scheduled for **07:30 Asia/Kolkata**, with **TEST_MODE=true**
and both send nodes disabled/unbound. The portable export contains no credential bindings; local private configuration is separate.
GREEN summaries require Gmail; RED and DATA_FAILURE require both channels. Hosted formatting is evidence-grounded and blocked by API TEST_MODE. Verification uses disposable state and local receipt mocks.

The model is **exploratory, uncalibrated and conditional on Delivered-vs-Cancelled**;
there is no production-quality claim. Holdout precision .4167, recall .5556, F1 .4762,
ROC-AUC .4545 and AP .5613; production_ready=false. RED requests manual review.
GREEN means no supported predicted-risk hotspot detected; it is not observed business health.

## Current files and operating instructions

- [Canonical workflow](workflows/n8n/urbaneats_live.json): the canonical inactive export.
- [Runtime](docs/RUNTIME.md) and [automation setup](docs/LIVE_AUTOMATION.md).
- [Feature/prediction-point contract](docs/FEATURE_CONTRACT.md) and [evaluation](docs/EVALUATION.md).
- [Measured results](evaluation/results/metrics.json) and [cleanup audit](docs/CLEANUP_REPORT.md).
- [Final remediation](docs/FINAL_CODE_REMEDIATION.md), [pre-freeze audit](docs/PREFREEZE_AUDIT.md)
  and [remaining work](docs/REMEDIATION_PLAN.md). Phase reports are historical evidence.

Accepted verification: **148 tests, zero warnings**, 24/24 native verifier cases, and
actual canonical n8n GREEN/RED/DATA_FAILURE executions all passed. See the
[final execution evidence](evaluation/results/final_n8n_execution_verification.json).
All three executions used TEST_MODE, completed without delivery errors, and sent no
notifications or hosted requests. The model version is `UE-23c30780e69023fb`.
Local credentials belong only in ignored environment configuration or local n8n bindings;
never commit credentials, tokens or private recipients.

With the existing Python 3.12 environment and Docker Desktop:

```powershell
.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_tmp_checks
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe scripts/security_scan.py --output docker/local/checks/security_scan.json
.venv\Scripts\python.exe scripts/build_workflow.py --output docker/local/remediation/builder_check.json
.venv\Scripts\python.exe scripts/verify_notification_integration.py --output docker/local/checks/native_verification.json
Invoke-RestMethod http://127.0.0.1:8000/health
```

The builder embeds reviewed JS in the inactive export. The native verifier uses isolated
n8n 2.41.6 storage and local fixtures; it restores the API after outage checks and never
rewrites the current source, configures credentials or mounts the existing n8n_data.
Do not rerun evaluation/training or replace artifacts as part of repository cleanup.

## Assignment provenance

The supplied CSVs, historical scored CSV, notebooks, alerts, operational brief and
sanitized original root workflow remain at their existing paths. They provide assignment
provenance and are not live input or runtime code. The original Git baseline is
`c62430075fc5ccaaa5db487a7556d531ac128c63` (`assignment-baseline-v1`); sanitization predates
this cleanup. [Historical README](docs/history/README_PRE_3B1.md) preserves assignment
instructions and prior phase commentary. [Historical workflows](workflows/n8n/history/README.md)
and [historical reports](docs/history/README.md) are explicitly archived references.
