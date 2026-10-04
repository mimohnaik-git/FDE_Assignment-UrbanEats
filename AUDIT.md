# Current repository audit

The repository's only current n8n export is workflows/n8n/urbaneats_live.json: current
Phase 3C, 23 nodes, inactive, TEST_MODE=true, one disabled/unbound Slack/Gmail node each,
07:30 Asia/Kolkata. API business/model behavior is unchanged.

The API owns placement validation, saved-model inference, predicted-risk KPIs/support
hotspots, evidence/actions and deterministic/LLM-ready brief. n8n owns transport/outage,
claims, send gating, receipts and persistent native delivery audit. Its claim/audit path
works independently of an unavailable API. The model is exploratory, uncalibrated and
conditional Delivered-vs-Cancelled; production_ready=false and no production-quality claim.

[Cleanup report](docs/CLEANUP_REPORT.md) contains the audited inventory, deletion rationale,
protected-file hash comparison, workflow equivalence and verification results.
[Original audit history](docs/history/AUDIT_PHASE1_3.md) is preserved explicitly as history.
All assignment artifacts, model/evaluation evidence and the existing n8n account/volume
are retained. No external services, credentials, notifications, commits or pushes.

Phase 3C requires Gmail for GREEN/RED/failure, Slack only RED/failure, exact cited formatter
output and deterministic fallback. Groq remains environment-configurable without credentials
or live requests. Current audit: docs/FINAL_CODE_REMEDIATION.md. Phase reports record historical acceptance.
