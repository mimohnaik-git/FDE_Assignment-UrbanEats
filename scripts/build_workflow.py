"""Build the 22-node inactive Phase-3B orchestration export from reviewed JS."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows/n8n/urbaneats_live.json"

AUDIT_COLUMNS = {
    "orchestration_run_id": "string", "started_at": "string", "completed_at": "string",
    "api_service": "string", "attempt_count": "number", "failure_category": "string",
    "routing_status": "string", "test_mode": "boolean", "duplicate_suppression": "boolean",
    "slack_delivery_state": "string", "gmail_delivery_state": "string", "event_type": "string",
    "evidence_json": "string", "delivery_channel": "string", "slack_attempts": "number",
    "gmail_attempts": "number", "retry_allowed": "boolean", "delivery_error_category": "string",
}


def build():
    logic = "\n".join((ROOT / "workflows/n8n" / name).read_text(encoding="utf-8").split("// Node exports")[0]
                      for name in ["orchestration_logic.cjs", "notification_logic.cjs"])
    nodes, connections = [], {}

    def add(name, kind, parameters, version=2, **extra):
        index = len(nodes)
        nodes.append({"id": name.lower().replace(" ", "-"), "name": name,
                      "type": "n8n-nodes-base." + kind, "typeVersion": version,
                      "position": [(index % 6) * 260, (index // 6) * 240],
                      "parameters": parameters, **extra})

    def code(name, source):
        add(name, "code", {"jsCode": logic + "\n" + source})

    def link(a, b, output=0, input_index=0):
        edges = connections.setdefault(a, {"main": []})["main"]
        while len(edges) <= output:
            edges.append([])
        edges[output].append({"node": b, "type": "main", "index": input_index})

    def boolean(name, expression):
        add(name, "if", {"conditions": {"options": {"typeValidation": "strict", "version": 2},
            "conditions": [{"leftValue": expression, "rightValue": True,
                "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
            "combinator": "and"}, "options": {}}, 2.2)

    def channel_switch(name):
        add(name, "switch", {"mode": "expression", "numberOutputs": 2,
            "output": "={{ $json.delivery_channel === 'slack' ? 0 : 1 }}"}, 3.2)

    def audit(name):
        add(name, "dataTable", {"resource": "row", "operation": "insert",
            "dataTableId": {"__rl": True, "mode": "name",
                "value": "={{ $('Normalize Response').last().json.claim_table_name }}"},
            "columns": {"mappingMode": "defineBelow",
                "value": {key: "={{ $json." + key + " }}" for key in AUDIT_COLUMNS},
                "schema": [{"id": key, "displayName": key, "type": kind,
                    "required": False, "display": True, "defaultMatch": False,
                    "canBeUsedToMatch": True} for key, kind in AUDIT_COLUMNS.items()]},
            "options": {}}, 1.1)

    add("Schedule Trigger", "scheduleTrigger", {"rule": {"interval": [
        {"field": "cronExpression", "expression": "30 7 * * *"}]}}, 1.2)
    add("Manual Trigger", "manualTrigger", {}, 1)
    add("Settings", "code", {"jsCode": """
const settings={test_mode:true, orchestration_run_id_override:'', force_retry_nonce:'', source_batch_id:''};
return [{json:{...settings,started_at:new Date().toISOString()}}];
"""})
    add("Call UrbanEats API", "httpRequest", {"method": "POST",
        "url": "http://urbaneats-api:8000/process-current", "options": {"timeout": 120000,
            "response": {"response": {"fullResponse": True, "responseFormat": "text", "neverError": True}}}},
        4.2, retryOnFail=False, onError="continueRegularOutput")
    code("Normalize Response", """
const prior=$runIndex ? $('Normalize Response').all(0,$runIndex-1)[0].json.attempt_history : [];
return [{json:normalizeNotification($json,$('Settings').first().json,$execution,$runIndex+1,prior,new Date().toISOString())}];
""")
    boolean("Retry API", "={{ $json.retry_api }}")
    add("API Retry Delay", "wait", {"resume": "timeInterval", "amount": 1, "unit": "seconds"}, 1.1)
    add("Claim Run", "dataTable", {"resource": "table", "operation": "create",
        "tableName": "={{ $json.claim_table_name }}",
        "columns": {"column": [{"name": key, "type": kind} for key, kind in AUDIT_COLUMNS.items()]},
        "options": {"createIfNotExists": False}}, 1.1, onError="continueRegularOutput")
    code("Prepare Audit and Gate", "return [{json:prepareNotificationClaim($json,$('Normalize Response').last().json,new Date().toISOString())}];")
    audit("Persist Prepared Audit")
    boolean("Duplicate and TEST_MODE Gate", "={{ !$json.duplicate_suppression && !$json.test_mode && $json.slack_delivery_state === 'PENDING' && $json.gmail_delivery_state === 'PENDING' }}")
    add("Slack", "slack", {"resource": "message", "operation": "post", "select": "channel",
        "channelId": {"__rl": True, "mode": "id", "value": "CONFIGURE_LOCALLY"},
        "text": "={{ JSON.parse($json.evidence_json).packet.text }}", "otherOptions": {}},
        2.3, disabled=True, retryOnFail=False, onError="continueRegularOutput")
    add("Gmail", "gmail", {"resource": "message", "operation": "send", "sendTo": "CONFIGURE_LOCALLY",
        "subject": "={{ JSON.parse($json.evidence_json).packet.subject }}", "emailType": "text",
        "message": "={{ JSON.parse($json.evidence_json).packet.text }}", "options": {}},
        2.1, disabled=True, retryOnFail=False, onError="continueRegularOutput")
    code("Parse Receipts", """
const initial=$('Persist Prepared Audit').first().json;
if($prevNode.name==='Duplicate and TEST_MODE Gate')
 return ['slack','gmail'].map(channel=>({json:notificationReceipt(initial,channel,{},0,new Date().toISOString())}));
const channel=$prevNode.name==='Slack' ? 'slack' : $prevNode.name==='Gmail' ? 'gmail' : null;
if(!channel) throw Error('Unexpected delivery source');
// The parser is shared; its runIndex is not either channel's attempt count.
let count=0;
for(let index=0;index<3;index++) {
 try { if($(channel==='slack' ? 'Slack' : 'Gmail').all(0,index).length) count=index+1; }
 catch { break; }
}
if(!count) throw Error('Missing delivery attempt');
return [{json:notificationReceipt(initial,channel,$json,count,new Date().toISOString())}];
""")
    audit("Persist Delivery Audit")
    boolean("Retry Delivery", "={{ $json.retry_allowed }}")
    add("Delivery Retry Delay", "wait", {"resume": "timeInterval", "amount": 2, "unit": "seconds"}, 1.1)
    channel_switch("Retry Channel")
    channel_switch("Completed Channel")
    add("Merge Channel Results", "merge", {"mode": "append", "numberInputs": 2}, 3.2)
    code("Complete Audit", "return [{json:completeNotification($('Persist Prepared Audit').first().json,$input.all().map(i=>i.json),new Date().toISOString())}];")
    audit("Persist Completed Audit")
    for trigger in ["Schedule Trigger", "Manual Trigger"]:
        link(trigger, "Settings")
    for a, b in [("Settings", "Call UrbanEats API"), ("Call UrbanEats API", "Normalize Response"),
                 ("Normalize Response", "Retry API"), ("Retry API", "API Retry Delay"),
                 ("API Retry Delay", "Call UrbanEats API"), ("Claim Run", "Prepare Audit and Gate"),
                 ("Prepare Audit and Gate", "Persist Prepared Audit"),
                 ("Persist Prepared Audit", "Duplicate and TEST_MODE Gate"),
                 ("Parse Receipts", "Persist Delivery Audit"), ("Persist Delivery Audit", "Retry Delivery"),
                 ("Retry Delivery", "Delivery Retry Delay"), ("Delivery Retry Delay", "Retry Channel"),
                 ("Merge Channel Results", "Complete Audit"), ("Complete Audit", "Persist Completed Audit")]:
        link(a, b)
    link("Retry API", "Claim Run", 1)
    link("Duplicate and TEST_MODE Gate", "Parse Receipts", 1)
    link("Retry Delivery", "Completed Channel", 1)
    for index, channel in enumerate(["Slack", "Gmail"]):
        link("Duplicate and TEST_MODE Gate", channel)
        link(channel, "Parse Receipts")
        link("Retry Channel", channel, index)
        link("Completed Channel", "Merge Channel Results", index, index)
    workflow = {"name": "UrbanEats Phase 3B - unified inactive orchestration", "active": False,
                "nodes": nodes, "connections": connections,
                "settings": {"timezone": "Asia/Kolkata", "executionOrder": "v1"}, "pinData": {}}
    WORKFLOW.write_text(json.dumps(workflow, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build()
