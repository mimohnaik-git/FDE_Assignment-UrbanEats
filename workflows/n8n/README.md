# Current n8n orchestration

Import **urbaneats_live.json** only as the current workflow. It has 23 nodes,
Asia/Kolkata at 07:30, TEST_MODE=true, is inactive and has one disabled/unbound Slack
and Gmail send node each. Keep the existing project and n8n_data for persistent claims.

orchestration_logic.cjs owns transport classification, identity and independent outage
construction. notification_logic.cjs owns unified packets, persistent claim interpretation,
receipt parsing and audit completion. scripts/build_workflow.py embeds their reviewed
logic; scripts/verify_notification_integration.py checks the native workflow without
external sends or current-source mutation. [Setup](../../docs/LIVE_AUTOMATION.md).

Historical scaffold/outage exports are in history/ and are not current operating designs.
The original sanitized assignment workflow remains at the repository root for provenance.

GREEN skips Slack by policy; Gmail is required for all statuses. RED/failure require both.
The final 148-test suite, 24/24 native verification and actual canonical GREEN/RED/DATA_FAILURE
executions pass. [Final execution evidence](../../evaluation/results/final_n8n_execution_verification.json)
records TEST_MODE skips, bounded API retries and completion with zero notifications or hosted calls.
See [final remediation](../../docs/FINAL_CODE_REMEDIATION.md) and
[pre-freeze audit](../../docs/PREFREEZE_AUDIT.md). Phase reports remain historical evidence.
The saved model is exploratory and uncalibrated; GREEN is a supported-hotspot assessment,
not a production-health claim. Never commit local credentials or private recipients.
