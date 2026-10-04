# Current status and remaining work

The final architecture consists of the saved-model placement API and the inactive
23-node n8n workflow. The API owns validation, inference, supported hotspots,
evidence and grounded briefing. n8n owns independent outage reporting, claims,
channel policy, bounded retries, receipts and persistent audit.

GREEN requires Gmail and skips Slack by policy. RED and DATA_FAILURE require both.
Portable defaults keep TEST_MODE enabled and notification nodes disabled/unbound.
Private setup and earlier manual acceptance remain separate from this isolated audit.
This pass does not repeat live acceptance or authorize activation or external calls.

The model remains exploratory, uncalibrated and conditional Delivered-vs-Cancelled.
Live-source validity, operational use, provider configuration and any schedule activation
require their own explicit scope. Preserve model artifacts, datasets, evaluation
fingerprints and historical verification evidence.

See FINAL_CODE_REMEDIATION.md for current checks and remaining technical debt;
LIVE_AUTOMATION.md for the canonical operating contract. Historical plans remain in history/.
