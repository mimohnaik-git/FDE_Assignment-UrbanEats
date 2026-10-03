# Current n8n orchestration

Import **urbaneats_live.json** only as the current Phase-3B workflow. It has 22 nodes,
Asia/Kolkata at 07:30, TEST_MODE=true, is inactive and has one disabled/unbound Slack
and Gmail send node each. Keep the existing project and n8n_data for persistent claims.

orchestration_logic.cjs owns transport classification, identity and independent outage
construction. notification_logic.cjs owns unified packets, persistent claim interpretation,
receipt parsing and audit completion. scripts/build_workflow.py embeds their reviewed
logic; scripts/verify_notification_integration.py checks the native workflow without
external sends or current-source mutation. [Setup](../../docs/LIVE_AUTOMATION.md).

Historical scaffold/outage exports are in history/ and are not current operating designs.
The original sanitized assignment workflow remains at the repository root for provenance.
