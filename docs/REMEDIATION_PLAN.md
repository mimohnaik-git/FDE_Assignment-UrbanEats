# Current status and deferred work

The accepted architecture is Phase 3B: saved-model API plus a 22-node inactive n8n workflow
with independent outage DATA_FAILURE, bounded retries, persistent duplicate suppression,
TEST_MODE gates, one Slack/Gmail node each and unified delivery audit. Manual end-to-end
TEST_MODE verification has been completed. [Current instructions](LIVE_AUTOMATION.md).

Phase 3B.1 reconciles the repository and documentation only. Model/data/features/evidence,
API routing, hotspot policy, schedule, retry/idempotency and TEST_MODE behavior are unchanged.
No credentials, provider-specific configuration, channel-policy changes or new architecture
are implemented. Earlier implementation plans are [historical](history/README.md).

Remaining work requires a separate authorized phase: channel policy and provider choice,
credential/OAuth setup and actual receipt validation, live source/units/maturity validation,
then any decision to activate a schedule. No external action is authorized by this document.

Model remains exploratory, uncalibrated, conditional Delivered-vs-Cancelled; no production
quality or intervention claim. Preserve the [feature contract](FEATURE_CONTRACT.md),
[evaluation evidence](EVALUATION.md), assignment baseline and datasets. Model redevelopment
is outside repository cleanup and outside any assumption of current operational readiness.
