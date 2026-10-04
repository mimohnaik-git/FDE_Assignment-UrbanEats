ACTION_CATALOG = {
    "MANUAL_REVIEW": {
        "action_id": "MANUAL_REVIEW",
        "description": "Manually review the flagged current orders; verify before intervening.",
        "trigger_condition": "supported group predicted_risk_rate exceeds hotspot policy",
        "evidence_requirement": "validated group, sample_size >= minimum support, hotspot=true",
    },
    "CHECK_DATA": {
        "action_id": "CHECK_DATA",
        "description": "Inspect source freshness/schema and resolve the reported validation failure.",
        "trigger_condition": "DATA_FAILURE",
        "evidence_requirement": "logged validation or runtime error code",
    },
}


def approved_actions(groups):
    return ["MANUAL_REVIEW"] if any(g["is_hotspot"] for g in groups) else []
