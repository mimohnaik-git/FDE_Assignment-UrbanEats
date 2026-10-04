"""Bounded public-file secret/identifier scan; never emit matching values."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "provider_key_candidate": r"(?:gsk_[A-Za-z0-9_-]{15,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,})",
    "github_pat_candidate": r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})",
    "oauth_token_candidate": r"ya29\.[A-Za-z0-9_-]{20,}",
    "slack_channel_id": r"\b[CG](?=[A-Z0-9]{8,12}\b)(?=[A-Z0-9]*[0-9])[A-Z0-9]+\b",
    "drive_private_url": r"https://(?:drive\.google\.com|docs\.google\.com)/[^\s\"<>]+",
    "slack_token_candidate": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "personal_email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
}


def main(output=None):
    findings = []
    files = []
    for file in ROOT.rglob("*"):
        relative = file.relative_to(ROOT)
        if not file.is_file() or any(p in {
            ".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "runs",
        } or p.startswith(".pytest_tmp") for p in relative.parts):
            continue
        if str(relative).replace("\\", "/").startswith("docker/local/"):
            continue
        if file.suffix not in {".py", ".js", ".cjs", ".json", ".ipynb", ".md", ".toml", ".yaml", ".txt", ".example"}:
            continue
        files.append(str(relative))
        text = file.read_text(encoding="utf-8", errors="replace")
        text = text.replace("https://drive.google.com/uc?export=download&id=YOUR_FILE_ID", "")
        for kind, pattern in PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({"type": kind, "file": str(relative),
                                 "line": text.count("\n", 0, match.start()) + 1,
                                 "remediation": "Remove public value; configure locally; rotate if secret"})
    for file in [ROOT / "UrbanEats_n8n_workflow.json", *ROOT.glob("workflows/n8n/**/*.json")]:
        workflow = json.loads(file.read_text(encoding="utf-8"))
        if workflow.get("meta", {}).get("instanceId") or workflow.get("id"):
            findings.append({"type": "instance_metadata", "file": str(file.relative_to(ROOT))})
        for node in workflow["nodes"]:
            if node.get("credentials") or node.get("webhookId"):
                findings.append({"type": "credential_or_webhook_id",
                                 "file": str(file.relative_to(ROOT)), "node": node["name"]})
    report = {"scope": "current public text and workflow metadata; excludes local runs/environment",
              "files_scanned": len(files), "findings": findings,
              "historical_exposure": "Baseline Git history and read-only backup still contain original identifiers"}
    target = Path(output) if output is not None else ROOT / "evaluation/results/security_scan.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Preserve historical scan evidence by choosing a new output")
    main(parser.parse_args().output)
