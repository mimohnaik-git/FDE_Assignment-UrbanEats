# Phase 3C — channel policy and grounded formatting

Current architecture: latest placement batch → validation → saved-model inference → supported
restaurant-zone hotspots → unchanged evidence/actions → grounded briefing → n8n channels →
persistent audit. No architectural rebuild or new dependency. Canonical workflow remains
inactive, TEST_MODE=true, sends disabled/unbound at 07:30 Asia/Kolkata.

1. **Files:** API provider/briefing/service plus new presentation.py; notification JS,
   workflow builder/export; Compose/environment example; native verifier; new Phase-3C tests
   and updated cited-output/node-count tests; concise current docs and verification results.
2. **Count:** 22 → 23 nodes. Only additional node: Slack Required policy gate.
3. **Flow:** normalize/unified packet → persistent claim/prepared audit → duplicate/test gate
   → Slack Required (send or shared policy-skip parser) and independent Gmail → shared
   receipt/retry/channel audit → merged completion. No per-status send branches.
4. **Slack:** GREEN SKIPPED_POLICY with zero attempts; RED/failure required. RED is concise
   supported hotspot fractions/actions/citations/run/batch/limitation. Failure includes
   stage/category/system review and current provenance. Outage remains API-independent.
5. **Gmail:** every status required; fuller cited batch/hotspot/actions/provenance/model/time
   brief. Human-readable plain text, never raw JSON. Slack outcome cannot suppress Gmail.
6. **Grounding:** LLM copies/reorders canonical evidence sentences with exact citations and
   action IDs. Closed schema accepts no free-form causes, numbers, routing, provenance or
   readiness claims. Required KPI and supported hotspot citations cannot be omitted.
   Every accepted metric/action sentence retains its citation. Routing/model/provenance
   presentation is deterministic and provider-independent. Evidence objects are untouched.
7. **Fallback:** missing/disabled provider renders deterministic text; unavailable, malformed
   or rejected output sets FALLBACK and retains valid routing and channel notification.
8. **Provider:** LLM_PROVIDER=groq selects GROQ_API_KEY only (never generic key fallback),
   GROQ_BASE_URL (HTTPS compatible prefix), GROQ_MODEL from environment. Empty defaults;
   TEST_MODE blocks transport. Existing compatible abstraction/httpx handles bounded
   provider retries; no Groq SDK/dependency or live request. Choose local configuration
   only in a later authorized credential test; never put values into public artifacts.
9. **Tests:** targeted policy/test gates, cited acceptance and rejection, fallback, Groq
   no-credential/no-transport, channel messages; native green policy/duplicate plus independent
   ambiguous and exhausted rate-limit channel failures. Existing safety cases retained.
10. **Pytest:** 115 passed, two pre-existing dependency deprecation warnings.
11. **Ruff:** PASS; git diff --check PASS.
12. **Native:** PASS: n8n 2.41.6 public import and all 23 native executions; results in evaluation/results/phase3c_native_verification.json.
   CLI import uses a temporary isolated workflow ID; public template stays sanitized.
   Tests use unique per-case synthetic batch IDs (Windows timestamp resolution may repeat),
   isolated /process-batch fixtures, real native SQLite claims, and local mock sends only.
   Stopped-service errors may be DNS/refusal/timeout; all classify and retry within bounds.
13. **Docker:** updated source is copied onto the existing local API image without downloads
   or dependency installation; saved artifact untouched. Only API is recreated; existing
   n8n and its data remain intact. Final recovered health is READY; API container healthy, existing n8n running, temporary containers removed.
   An initial bare-digest Docker build attempted a registry metadata lookup and failed;
   the corrected source-only build used an explicitly tagged existing local base. No
   Groq/LLM/Slack/Gmail request or credential was involved.
14. **Security:** PASS: public scan found zero findings; inactive/TEST_MODE/disabled/unbound workflow checks pass. Historical identifier exposure remains documented in the scan.
   No configured secrets, real sends, activation, commit, push, PR, merge or tag.
15. **Changes:** Gmail-only GREEN; policy skip remains distinct from TEST_MODE/duplicate
   suppression for required channels. Unrequired Slack always SKIPPED_POLICY, even on
   repeated GREEN runs; duplicate flag and Gmail DUPLICATE_SUPPRESSED still record repeat.
   New per-channel presentation fields live outside evidence; formatter citations now
   explicitly mandatory. Required-channel retries/claims/UNKNOWN behavior is unchanged.
16. **Preserved:** original data, supervised population/protocol, model selection/artifact,
   threshold, feature/prediction contract, support/hotspot/action policy and evidence facts.
   Model: exploratory, uncalibrated, conditional Delivered-vs-Cancelled model; no
   production-quality claim. Protected hashes are in phase3c_protected.json.
17. **Import:** workflows/n8n/urbaneats_live.json, 23 nodes. Import inactive in the existing
   project; keep Settings test_mode:true and API TEST_MODE=true; keep Slack/Gmail disabled
   and unbound. Preserve claim tables and n8n_data. Do not activate the schedule here.
18. **Boundary:** real Groq model/API/receipt compatibility and credentials await later
   authorized testing. No live provider/channel action is part of Phase 3C.
19. **Recommendation:** READY FOR GROQ CREDENTIAL TEST. This is preparation readiness, not verified live Groq compatibility. Stop here before credentials/provider/channel calls.

Current operating details: LIVE_AUTOMATION.md and RUNTIME.md. Phase-3B/Cleanup reports remain
historical snapshots of earlier verified baselines. This phase stops before live credentials.
