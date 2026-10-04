"""Loopback-only Phase-3 API verification; TEST_MODE must be true in server."""
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

from current_demo import demo_batch


def request(path, payload=None):
    req = Request("http://127.0.0.1:" + str(int(os.getenv("URBANEATS_SMOKE_PORT", "8765"))) + path,
                  data=json.dumps(payload).encode() if payload is not None else None,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def main(output=None):
    report = {"health": request("/health"), "routes": [], "external_calls": False}
    for payload, expected in [({}, "DATA_FAILURE"), (demo_batch(4), "GREEN_SUMMARY"),
                              (demo_batch(24), "RED_ALERT")]:
        result = request("/process-batch", payload)
        assert result["routing_status"] == expected
        assert result["evidence"]["routing_status"] == expected
        for channel in ["slack", "gmail"]:
            event = request("/delivery", {"run_id": result["run_id"],
                                         "channel": channel, "operation": "claim"})
            assert not event["send"] and event["status"] == "TEST_MODE_DISABLED"
        report["routes"].append({"routing": expected, "run_id": result["run_id"],
                                 "records_scored": len(result["predictions"]),
                                 "evidence_ids": [f["evidence_id"] for f in result["evidence"]["facts"]]})
    target = Path(output) if output is not None else Path(
        "evaluation/results/phase3_docker_smoke.json" if os.getenv("URBANEATS_SMOKE_PORT") == "8000"
        else "evaluation/results/phase3_smoke.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Preserve historical smoke evidence by choosing a new output")
    main(parser.parse_args().output)
