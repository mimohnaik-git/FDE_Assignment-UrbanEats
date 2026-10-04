// Shared portfolio orchestration. API business/model evidence is never recomputed.
function identityHash(text) {
  // SHA-256 keeps arbitrary source identities out of native table names.
  const bytes = Array.from(unescape(encodeURIComponent(text)), c => c.charCodeAt(0));
  const length = bytes.length * 8;
  bytes.push(128);
  while (bytes.length % 64 !== 56) bytes.push(0);
  bytes.push(0, 0, 0, 0, (length >>> 24) & 255, (length >>> 16) & 255,
    (length >>> 8) & 255, length & 255);
  const primes = [], initial = [], constants = [];
  for (let n = 2; primes.length < 64; n++) {
    if (primes.some(p => n % p === 0)) continue;
    primes.push(n);
    if (initial.length < 8) initial.push((Math.sqrt(n) % 1 * 2 ** 32) | 0);
    constants.push((Math.cbrt(n) % 1 * 2 ** 32) | 0);
  }
  const rotate = (n, b) => (n >>> b) | (n << (32 - b));
  let hash = initial;
  for (let offset = 0; offset < bytes.length; offset += 64) {
    const w = [];
    for (let i = 0; i < 64; i++) {
      if (i < 16) {
        const p = offset + i * 4;
        w[i] = (bytes[p] << 24) | (bytes[p + 1] << 16) | (bytes[p + 2] << 8) | bytes[p + 3];
      } else {
        const x = w[i - 15], y = w[i - 2];
        w[i] = (w[i - 16] + (rotate(x, 7) ^ rotate(x, 18) ^ (x >>> 3))
          + w[i - 7] + (rotate(y, 17) ^ rotate(y, 19) ^ (y >>> 10))) | 0;
      }
    }
    let [a, b, c, d, e, f, g, h] = hash;
    for (let i = 0; i < 64; i++) {
      const t1 = (h + (rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25))
        + ((e & f) ^ (~e & g)) + constants[i] + w[i]) | 0;
      const t2 = ((rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22))
        + ((a & b) ^ (a & c) ^ (b & c))) | 0;
      [a, b, c, d, e, f, g, h] = [(t1 + t2) | 0, a, b, c, (d + t1) | 0, e, f, g];
    }
    hash = hash.map((v, i) => (v + [a, b, c, d, e, f, g, h][i]) | 0);
  }
  return hash.map(v => (v >>> 0).toString(16).padStart(8, '0')).join('');
}

function normalizeNotification(response, settings, execution, attempt, previous, now) {
  const context = initializeOrchestration(settings, execution, settings.started_at || now);
  const classified = classifyApiResponse(response);
  const attempts = [...previous, {attempt, at: now,
    category: classified.failure_category || 'API_RESPONSE', http_status: classified.http_status || null}];
  if (!classified.api_response && attempt < 3 && classified.failure_category !== 'HTTP_ERROR')
    return {retry_api: true, attempt_count: attempt, attempt_history: attempts};
  const api = classified.api_response;
  const outage = api ? null : constructOutage(context,
    {...classified, attempt_count: attempt, attempt_history: attempts}, now);
  const evidence = api ? api.evidence : outage.outage_evidence;
  const source = api ? api.source_batch_id || evidence.source_batch_id : context.source_batch_id;
  const origin = api ? 'api' : 'orchestration';
  // API batches deduplicate across different API run IDs; outages retain Phase-3A identities.
  const identity = api ? `batch:${source || evidence.source_sha256 || api.run_id}`
    : `outage:${context.orchestration_run_id}`;
  const force = settings.force_retry_nonce || '';
  const claim = api ? `UE_NOTIFY_${identityHash(identity + (force ? ':force:' + force : ''))}`
    : context.claim_table_name; // preserves Phase-3A outage claims across upgrade
  return {retry_api: false, attempt_count: attempt, attempt_history: attempts,
    orchestration_run_id: context.orchestration_run_id, started_at: context.started_at,
    test_mode: context.test_mode, source_batch_id: source || null, claim_table_name: claim,
    evidence_origin: origin, routing_status: api ? api.routing_status : 'DATA_FAILURE',
    api_run_id: api ? api.run_id : null, failure_category: api ? '' : classified.failure_category,
    evidence, text: api ? api.briefing.text : outage.notification_text,
    subject: `UrbanEats ${api ? api.routing_status : 'DATA_FAILURE'}`,
    channel_policy: {slack: !api || api.routing_status !== 'GREEN_SUMMARY', gmail: true},
    slack_text: api ? api.briefing.channels?.slack_text ?? api.briefing.text : outage.notification_text,
    gmail_text: api ? api.briefing.channels?.gmail_text ?? api.briefing.text : outage.notification_text};
}

function notificationAudit(packet, now, event, state, duplicate = false) {
  return {orchestration_run_id: packet.orchestration_run_id, started_at: packet.started_at,
    completed_at: now, api_service: 'urbaneats-api:8000', attempt_count: packet.attempt_count,
    failure_category: packet.failure_category, routing_status: packet.routing_status,
    test_mode: packet.test_mode, duplicate_suppression: duplicate,
    slack_delivery_state: packet.routing_status === 'GREEN_SUMMARY' ? 'SKIPPED_POLICY' : state,
    gmail_delivery_state: state, event_type: event,
    // Retain Phase-3A columns; packet_json is stored inside evidence_json for schema compatibility.
    evidence_json: JSON.stringify({packet, evidence: packet.evidence}), delivery_channel: '',
    slack_attempts: 0, gmail_attempts: 0, retry_allowed: false, delivery_error_category: ''};
}

function prepareNotificationClaim(result, packet, now) {
  const owns = typeof result?.id === 'string' && result.name === packet.claim_table_name;
  const error = typeof result?.error === 'string' ? result.error : JSON.stringify(result?.error || {});
  const duplicate = !owns && /already exists|unique constraint|duplicate/i.test(error);
  if (!owns && !duplicate) throw Error('Persistent notification claim failed; delivery blocked');
  return notificationAudit(packet, now, 'notification_prepared',
    duplicate ? 'DUPLICATE_SUPPRESSED' : packet.test_mode ? 'SKIPPED_TEST_MODE' : 'PENDING', duplicate);
}

function notificationReceipt(initial, channel, receipt, attempt, now) {
  const packet = JSON.parse(initial.evidence_json).packet;
  const row = notificationAudit(packet, now, 'delivery_attempt', 'PENDING', initial.duplicate_suppression);
  const policySkip = channel === 'slack' && packet.routing_status === 'GREEN_SUMMARY';
  const skipped = policySkip || initial.duplicate_suppression || packet.test_mode;
  const slackTimestamp = receipt?.message_timestamp ?? receipt?.message?.ts;
  // A disabled node returns the upstream audit item unchanged, not a send receipt.
  const passThrough = !skipped && receipt && typeof receipt === 'object'
    && Object.keys(receipt).length === Object.keys(initial).length
    && Object.keys(initial).every(key => JSON.stringify(receipt[key]) === JSON.stringify(initial[key]));
  const ok = !passThrough && (channel === 'slack' ? receipt.ok === true
    && typeof receipt.channel === 'string' && receipt.channel.trim().length > 0
    && typeof slackTimestamp === 'string' && slackTimestamp.trim().length > 0
    : typeof receipt.id === 'string' && !receipt.error);
  const rate = channel === 'slack'
    ? receipt.ok === false && ['ratelimited', 'rate_limited'].includes(receipt.error)
    : receipt.statusCode === 429 || receipt.error?.statusCode === 429;
  const state = policySkip ? 'SKIPPED_POLICY' : skipped ? initial[`${channel}_delivery_state`] : ok ? 'SUCCESS' : rate ? 'FAILURE' : 'UNKNOWN';
  row[`${channel}_delivery_state`] = state;
  row.delivery_channel = channel;
  row[`${channel}_attempts`] = skipped || passThrough ? 0 : attempt;
  row.retry_allowed = !skipped && !passThrough && rate && attempt < 3;
  row.delivery_error_category = skipped || ok ? '' : passThrough ? 'CHANNEL_NOT_SENT' : rate ? 'RATE_LIMITED' : 'UNVERIFIED_RECEIPT';
  row.event_type = skipped ? 'delivery_skipped' : passThrough ? 'delivery_not_sent' : 'delivery_attempt';
  return row;
}

function completeNotification(initial, rows, now) {
  const packet = JSON.parse(initial.evidence_json).packet;
  const slack = rows.find(r => r.delivery_channel === 'slack');
  const gmail = rows.find(r => r.delivery_channel === 'gmail');
  if (!slack || !gmail || rows.length !== 2 || rows.some(r => r.retry_allowed
      || r.orchestration_run_id !== packet.orchestration_run_id)) throw Error('Delivery audit mismatch');
  const row = notificationAudit(packet, now, 'notification_complete', 'PENDING', initial.duplicate_suppression);
  for (const channel of ['slack', 'gmail']) {
    const result = channel === 'slack' ? slack : gmail;
    row[`${channel}_delivery_state`] = result[`${channel}_delivery_state`];
    row[`${channel}_attempts`] = result[`${channel}_attempts`];
  }
  if (['slack', 'gmail'].some(channel => row[`${channel}_delivery_state`] === 'UNKNOWN'))
    row.event_type = 'notification_unverified';
  else if (['slack', 'gmail'].some(channel => row[`${channel}_delivery_state`] === 'FAILURE'))
    row.event_type = 'notification_failed';
  return row;
}

// Node exports
if (typeof module !== 'undefined') {
  const legacy = require('./orchestration_logic.cjs');
  var {initializeOrchestration, classifyApiResponse, constructOutage} = legacy;
  module.exports = {identityHash, normalizeNotification, notificationAudit,
    prepareNotificationClaim, notificationReceipt, completeNotification};
}
