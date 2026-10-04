import json

from urbaneats.config import ROOT


def test_historical_scaffold_inactive_and_sanitized():
    path = ROOT / "workflows/n8n/history/urbaneats_core_scaffold.json"
    workflow = json.loads(path.read_text())
    assert workflow["active"] is False
    assert workflow["settings"]["timezone"] == "Asia/Kolkata"
    assert "meta" not in workflow
    for node in workflow["nodes"]:
        assert not {"credentials", "webhookId"} & node.keys()
        assert node["type"] not in ["n8n-nodes-base.slack", "n8n-nodes-base.gmail"]


def test_legacy_workflow_public_identifiers_removed():
    workflow = json.loads((ROOT / "UrbanEats_n8n_workflow.json").read_text(encoding="utf-8"))
    assert not workflow["active"]
    assert not {"meta", "versionId", "id"} & workflow.keys()
    for node in workflow["nodes"]:
        assert not {"credentials", "webhookId"} & node.keys()
