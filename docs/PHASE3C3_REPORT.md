# Phase 3C.3 - receipt and audit interpretation

Root cause: Slack receipt parser expected top-level ts instead of n8n 2.3 message_timestamp/message.ts.
The shared parser also counted disabled-node pass-through as an attempt; a native upstream audit row
id could falsely resemble a Gmail receipt. Exact unchanged upstream comparison now takes precedence
before provider success/error classification, with UNKNOWN/zero attempts/CHANNEL_NOT_SENT.
Real errors/receipts are not exact pass-through and retain existing parsing and bounded retry policy.
No new channel state or audit columns are introduced.

SUCCESS requires Slack ok:true, non-empty channel and non-empty supported timestamp. Ambiguous
responses remain UNKNOWN with no automatic retry. Final events are notification_unverified when
any channel is UNKNOWN, notification_failed for terminal failures, otherwise notification_complete.
Persistent claims remain held for reconciliation. Intentional skip states remain terminal skips.

Installed Slack V2 description and implementation confirm normal otherOptions.includeLinkToWorkflow
is supported (default true); canonical builder/export set false. No response manipulation is used.

Changed: notification_logic.cjs, build_workflow.py, canonical JSON, tests/test_notification.py,
new tests/test_phase3c3.py, native verifier, current operating docs and verification results.
Fixture uses the live receipt shape and timestamp, with channel identifier sanitized in public files.

Pytest: 137 passed, two existing dependency warnings. Ruff PASS.
Native import/execution, final security and Docker results: pending.
Model, data, threshold, features, evidence/actions/citations, Groq, routing/channel policy,
23-node topology, retry/idempotency/outage/TEST_MODE semantics unchanged.
Canonical export inactive; sends disabled/unbound; 07:30 Asia/Kolkata retained.
No live Slack/Gmail/Groq call, activation, commit or push.
