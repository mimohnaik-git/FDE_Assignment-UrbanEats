"""Historical one-time assignment sanitization utility; not runtime/verification.

Remove environment identifiers from the historical public export.

Original bytes remain preserved by assignment-baseline-v1; graph/results are not
recast as rebuilt. No credentials are read from external stores or configured here.
"""
import json
from pathlib import Path


def sanitize(path):
    workflow = json.loads(path.read_text(encoding="utf-8"))
    workflow["active"] = False
    for key in ["id", "versionId", "meta"]:
        workflow.pop(key, None)
    workflow["pinData"] = {}
    for index, node in enumerate(workflow["nodes"]):
        node["id"] = f"legacy-node-{index}"
        node.pop("credentials", None)
        node.pop("webhookId", None)
        parameters = node["parameters"]
        if node["type"] == "n8n-nodes-base.httpRequest":
            parameters["url"] = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
        if node["type"] == "n8n-nodes-base.gmail":
            parameters["sendTo"] = "CONFIGURE_LOCAL_RECIPIENT"
        if node["type"] == "n8n-nodes-base.slack":
            parameters["channelId"] = {"value": "CONFIGURE_LOCAL_CHANNEL", "mode": "id", "__rl": True}
    path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sanitize(Path("UrbanEats_n8n_workflow.json"))
