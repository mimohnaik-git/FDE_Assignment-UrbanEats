# Phase 3C.1 - Groq compatibility and presentation repair

The current source did not reproduce either reported string: fact_sentences already emits
"Current batch", while render assembled the limitation and citation in an inline f-string.
The observed malformed text therefore came from an older/stale rendered result or runtime;
the precise historical producer cannot be recovered from current source. The renderer now
uses a shared citation-line constructor and explicit output regression tests; no live Groq call is made.

Groq GPT-OSS request handling was introduced in Phase 3C.1 and is unchanged here.
For reference, GPT-OSS uses response_format json_schema with strict:true and an explicit items schema. Both objects forbid additional properties and require all fields;
action_ids is an array of strings. Application-level exact cited sentence/action/evidence
validation remains mandatory. Generic compatible providers retain JSON Object Mode.
Temperature remains 0. GPT-OSS does not support reasoning_format: include_reasoning:false
is used instead, and only final message.content is consumed. No reasoning is exposed.

Sources checked 2026-10-04: [Groq structured outputs](https://console.groq.com/docs/structured-outputs)
and [Groq reasoning](https://console.groq.com/docs/reasoning).

Safe trace reasons: PROVIDER_HTTP_FAILED, PROVIDER_TRANSPORT_FAILED,
PROVIDER_RESPONSE_MALFORMED, PROVIDER_OUTPUT_REJECTED, PROVIDER_UNAVAILABLE.
No response body/header, authorization, key or raw exception is persisted. Existing
three-attempt transport/429/5xx retry behavior and deterministic fallback are preserved.

Message headers/separators use portable ASCII instead of emoji/em dashes. Every appended
citation has a preceding space. This avoids terminal encoding ambiguity without altering
evidence. Current active source/workflow/docs were scanned for encoding defects;
historical documents remain historical. Workflow has 23 nodes and unchanged channel policy,
schedule, retry/claim/outage semantics, inactive state and disabled/unbound send nodes.

Tests: 128 pytest passed (two existing warnings); Ruff and diff check PASS.
New mocked tests exercise schema/request/reasoning exclusion, valid acceptance, bad JSON,
bad envelope/schema/evidence, safe HTTP/transport failures, retries/recovery, secret exclusion,
all routing presentations and citation spacing. Initial pytest teardown hit Windows shared
temp permissions; rerun with workspace-local basetemp passed normally.

Docker source-only build uses existing local image, network none, pull false; verification
enforces API TEST_MODE=true through ignored docker/local/phase3c1/verify.yaml. Existing
credentials are not read, printed or changed. The API is left with TEST_MODE=true after tests;
this is an operational safety gate, not a semantic change. No real provider/channel calls.

Native: n8n 2.41.6 public import PASS and all 23 native executions PASS.
Recovered Docker health READY (model/threshold loaded). Final public secret scan PASS.
Recommendation: READY FOR SECOND GROQ CREDENTIAL TEST; live success is not yet verified.
Model, threshold, feature contract, hotspot policy, evidence facts and approved actions
are untouched. Eighteen protected files match the previous Phase-3C manifest; ignored
current_batch.json already differs from that historical snapshot and is not written by this
repair. Native verification uses isolated process-batch fixtures.

No commits or pushes. Live compatibility remains to be tested separately with authorization.
