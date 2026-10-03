# Current runtime — accepted Phase 3B

The API reads the configured latest placement-v1 JSON batch and loads the existing trusted
saved model/threshold. It never retrains during a request. Freshness, prediction-point
features, Delivered-vs-Cancelled target population and units are specified in
[FEATURE_CONTRACT.md](FEATURE_CONTRACT.md). Historical scored CSVs are not live input.

Flow: current batch → validation → inference → supported restaurant-zone hotspots →
evidence + approved actions → deterministic/LLM-ready briefing → n8n → Slack/Gmail →
persistent delivery audit. Minimum support, hotspot policy, facts and thresholds are unchanged.
No observed cancellation KPI is inferred from placement-only input.

Model limitation: exploratory, uncalibrated, conditional Delivered-vs-Cancelled; no
production-quality claim. See [evaluation](EVALUATION.md). RED means manual review only;
GREEN means no supported predicted-risk hotspot detected.

## API and local execution

Python 3.12, existing pinned dependencies and trusted artifact under artifacts/model.
GET /health returns READY only when model and threshold load. POST /process-current
rereads URBANEATS_SOURCE_FILE; POST /process-batch uses a supplied placement envelope.
Invalid/missing/stale input returns DATA_FAILURE. Runtime/model/log failures fail closed.
The API emits immutable evidence/actions and cited brief; unsupported formatter output
or unavailable provider uses deterministic fallback. TEST_MODE=true blocks hosted transport.

```powershell
$env:PYTHONPATH = 'src'
.venv\Scripts\python.exe -m uvicorn urbaneats.service:app --host 127.0.0.1 --port 8765
# Separate shell, while this loopback API is running:
.venv\Scripts\python.exe scripts/verify_api.py
```

Docker uses docker/compose.yaml, existing saved artifact, a read-only data mount and
writeable runs mount. The API is reachable at localhost:8000 and urbaneats-api:8000 on
urbaneats_private. Do not rebuild models to address deployment/runtime issues.

## Persistence and orchestration

API run/evidence logs remain under ignored runs/. The existing /delivery endpoint and
filesystem claims remain unchanged and regression-tested for compatibility; the Phase-3B
workflow uses native n8n Data Tables for all delivery claims/audits instead.

API-generated DATA_FAILURE preserves API evidence. An offline/unusable response produces
independent orchestration DATA_FAILURE in n8n, with no invented model facts or stale
successful evidence. The 22-node export retains bounded request/delivery retry behavior,
unique persistent claims, independent channel receipts and completion audit.

Settings test_mode=true independently gates n8n sends; API TEST_MODE=true independently
blocks hosted calls. Both stay true. The export is inactive at 07:30 Asia/Kolkata, with
one Slack and one Gmail node disabled/unbound. See [automation](LIVE_AUTOMATION.md).
Native verification sends local request fixtures to /process-batch without changing
current_batch.json. No external services, credentials, notifications or activation are
needed for verification. Earlier runtime instructions are [historical](history/README.md).
