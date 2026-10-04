# Canonical n8n orchestration

[urbaneats_live.json](urbaneats_live.json) is the current **23-node** export. It is inactive,
scheduled for **07:30 Asia/Kolkata**, and defaults to **TEST_MODE=true**. One Slack and one
Gmail node remain disabled/unbound, with `CONFIGURE_LOCALLY` destinations and no exported
credentials. Private credentials and recipients must never enter Git.

## Source and responsibilities

[orchestration_logic.cjs](orchestration_logic.cjs) owns API response classification,
execution identity and independent outage DATA_FAILURE construction.
[notification_logic.cjs](notification_logic.cjs) owns unified packets, persistent claim
interpretation, channel policy, receipt classification and audit completion.
The [builder](../../scripts/build_workflow.py) embeds the reviewed logic into the canonical
graph. Its output deterministically equals the accepted export.

The API owns placement validation, inference, supported hotspots, evidence/actions and
grounded briefing with deterministic fallback. n8n owns transport, claims, sends and native
Data Table audit. An unusable API response never reuses prior GREEN/RED evidence. Claims
persist across executions; retries are bounded, and ambiguous required receipts remain
unverified rather than being automatically resent.

| Route | Slack policy | Gmail policy |
|---|---|---|
| GREEN_SUMMARY | SKIPPED_POLICY | Required |
| RED_ALERT | Required | Required |
| DATA_FAILURE | Required | Required |

Required channels become `SKIPPED_TEST_MODE` in TEST_MODE. GREEN means no supported
predicted-risk hotspot, not business health. The exploratory, uncalibrated model supplies
predicted-risk fractions rather than observed cancellation rates; **MANUAL_REVIEW** is
the approved hotspot action.

## Verification and operation

The accepted suite has **148 passing tests with zero warnings**. The
[native verifier](../../scripts/verify_notification_integration.py) passed
[24/24 integration cases](../../evaluation/results/final_native_verification.json).
The unchanged canonical graph also passed actual isolated n8n
[GREEN_SUMMARY, RED_ALERT and DATA_FAILURE executions](../../evaluation/results/final_n8n_execution_verification.json).
All completed in TEST_MODE with zero real notifications or hosted calls; DATA_FAILURE
stopped after three HTTP 503 attempts. Disposable state was removed after verification.

Use the [root README](../../README.md) for fresh-clone prerequisites and verification
commands, and [automation instructions](../../docs/LIVE_AUTOMATION.md) for local import
and persistent Data Table operation. Preserve an existing project's n8n_data and claim
state; disposable verification never mounts that volume. The API must retain TEST_MODE
to block hosted transport during isolated checks.

The [engineering report](../../docs/FINAL_CODE_REMEDIATION.md) and
[release audit](../../docs/PREFREEZE_AUDIT.md) document the accepted design and safety gates.
[Archived exports](history/README.md) and the sanitized root assignment workflow are
provenance snapshots. Import the canonical export for the current system; keep it inactive
unless a separate authorized deployment enables it.
