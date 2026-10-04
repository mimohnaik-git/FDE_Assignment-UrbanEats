"""Deterministic channel presentation; never changes model/evidence or approved actions."""
from .briefing import MODEL_LIMITATION, fact_sentences


def channel_messages(result):
    packet = result["evidence"]
    route = result["routing_status"]
    batch = result.get("source_batch_id") or "unavailable"
    run = result["run_id"]
    timestamp = packet["generated_at"]
    if route == "DATA_FAILURE":
        fact = packet["facts"][0]
        errors = result.get("errors", [])
        stage = ", ".join(sorted({e.get("location", "runtime") for e in errors})) or "runtime"
        categories = ", ".join(sorted({e.get("code", "unavailable") for e in errors})) or "unavailable"
        citation = f"[evidence:{fact['evidence_id']}]"
        text = (f"UrbanEats DATA FAILURE\nStage: {stage}; category: {categories}. {citation}\n"
                "No GREEN/RED assessment produced. Manual system review required.\n"
                f"Action CHECK_DATA: {packet['approved_actions'][0]['description']} {citation}\n"
                f"[run:{run}] [source:{batch}]\nGenerated: {timestamp}")
        return {"slack_text": text, "gmail_subject": "UrbanEats DATA_FAILURE",
                "gmail_text": text + f"\nModel version: {result.get('model_version') or 'unavailable'}\n"
                + MODEL_LIMITATION + f". {citation}"}
    sentences = fact_sentences(packet)
    supported = [f for f in packet["facts"] if f.get("is_hotspot")]
    slack = ["UrbanEats RED ALERT - manual review required"]
    for fact in supported[:3]:
        eid = fact["evidence_id"]
        slack.append(f"{sentences[eid]} [evidence:{eid}]")
        for aid in fact["approved_action_ids"]:
            action = next(a for a in packet["approved_actions"] if a["action_id"] == aid)
            slack.append(f"Action {aid}: {action['description']} [evidence:{eid}]")
    if len(supported) > 3:
        slack.append("Additional supported hotspots appear in Gmail.")
    slack += [f"[run:{run}] [source:{batch}]", f"{MODEL_LIMITATION}. [evidence:KPI-BATCH]"]
    gmail = (result["briefing"]["text"] + f"\nSource: {packet['source_dataset']}\nGenerated: {timestamp}\n"
             f"Model version: {packet['model_version']} [evidence:KPI-BATCH]\n"
             "Supported hotspots: " + ("see cited hotspot facts above" if supported else "none")
             + " [evidence:KPI-BATCH]")
    return {"slack_text": "\n".join(slack) if route == "RED_ALERT" else "",
            "gmail_subject": f"UrbanEats {route}", "gmail_text": gmail}
