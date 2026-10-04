// Pure orchestration logic, embedded verbatim in the exported n8n Code nodes.
// It deliberately never copies model data or arbitrary error text into outage evidence.
function classifyApiResponse(response) {
  const status = Number(response?.statusCode || response?.status || 0);
  const error = response?.error;
  if (status >= 500) return {failure_category: 'HTTP_5XX', http_status: status};
  if (error) {
    const description = typeof error === 'string' ? error : JSON.stringify(error);
    if (/ENOTFOUND|EAI_AGAIN|getaddrinfo|incorrect host|name resolution/i.test(description))
      return {failure_category: 'DNS_SERVICE_FAILURE'};
    if (/ECONNREFUSED|refused.*connection|connection.*refused/i.test(description))
      return {failure_category: 'CONNECTION_REFUSED'};
    if (/ETIMEDOUT|ESOCKETTIMEDOUT|ECONNABORTED|timed?\s*out|timeout/i.test(description))
      return {failure_category: 'TIMEOUT'};
    return {failure_category: 'TRANSPORT_FAILURE'};
  }
  if (status && (status < 200 || status >= 300))
    return {failure_category: 'HTTP_ERROR', http_status: status};
  // n8n's text response uses `data` even when fullResponse is enabled.
  let body = response?.body ?? response?.data ?? response;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { return {failure_category: 'MALFORMED_RESPONSE'}; }
  }
  const valid = body && ['DATA_FAILURE', 'GREEN_SUMMARY', 'RED_ALERT'].includes(body.routing_status)
    && /^UE-[0-9a-f]{32}$/.test(body.run_id || '')
    && body.evidence?.routing_status === body.routing_status
    && Array.isArray(body.evidence?.facts) && body.evidence.facts.length > 0
    && typeof body.briefing?.text === 'string';
  return valid ? {api_response: body} : {failure_category: 'MALFORMED_RESPONSE'};
}

function initializeOrchestration(settings, execution, now) {
  const override = settings.orchestration_run_id_override || '';
  const force = settings.force_retry_nonce || '';
  if ((override && !/^[A-Za-z0-9_-]{1,48}$/.test(override))
      || (force && !/^[A-Za-z0-9_-]{1,16}$/.test(force))) throw Error('Invalid orchestration identity');
  const day = new Date(now).toLocaleDateString('en-CA', {timeZone: 'Asia/Kolkata'}).replaceAll('-', '');
  const base = override || (execution.mode === 'trigger' ? `ORCH-${day}-0730` : `ORCH-${execution.id}`);
  const id = force ? `${base}-F-${force}` : base;
  if (!/^[A-Za-z0-9_-]{1,48}$/.test(id)) throw Error('Invalid orchestration identity');
  return {orchestration_run_id: id, started_at: now, test_mode: settings.test_mode !== false,
    source_batch_id: /^[A-Za-z0-9_-]{1,100}$/.test(settings.source_batch_id || '')
      ? settings.source_batch_id : null, claim_table_name: `UE_ORCH_${id}`};
}

function constructOutage(context, failure, now) {
  const packet = {schema_version: 'orchestration-failure-v1', evidence_origin: 'orchestration',
    orchestration_run_id: context.orchestration_run_id, generated_at: now,
    routing_status: 'DATA_FAILURE', failure_stage: 'URBANEATS_API',
    failure_category: failure.failure_category, attempt_count: failure.attempt_count,
    api_service: 'urbaneats-api:8000', source_batch_id: context.source_batch_id,
    test_mode: context.test_mode, notification_required: true,
    attempts: failure.attempt_history};
  const text = ['UrbanEats automation failure - DATA_FAILURE.',
    'The scoring service could not provide a usable response after bounded attempts.',
    'No GREEN or RED operational assessment was produced. Manual system review is required.',
    `Orchestration run: ${packet.orchestration_run_id}; timestamp: ${now};`,
    `stage: ${packet.failure_stage}; category: ${packet.failure_category};`,
    `attempts: ${packet.attempt_count}; retries: ${Math.max(0, packet.attempt_count - 1)};`,
    `source batch: ${packet.source_batch_id ?? 'unavailable'}; evidence origin: orchestration.`].join('\n');
  return {orchestration_run_id: context.orchestration_run_id, started_at: context.started_at,
    test_mode: context.test_mode, source_batch_id: context.source_batch_id,
    claim_table_name: context.claim_table_name, evidence_origin: 'orchestration', routing_status: 'DATA_FAILURE',
    outage_evidence: packet, notification_text: text};
}

// Node exports (excluded from embedded n8n Code nodes).
module.exports = {classifyApiResponse, initializeOrchestration, constructOutage};
