import json

from urbaneats.config import ROOT


def test_evaluation_provenance_and_disjoint_splits():
    report = json.loads((ROOT / "evaluation/results/metrics.json").read_text())
    dev, hold = set(report["development_order_ids"]), set(report["holdout_order_ids"])
    assert dev.isdisjoint(hold)
    assert len(dev) == 60 and len(hold) == 20
    for candidate in report["candidates"].values():
        coverage = [0] * 60
        for fold in candidate["fold_membership"]:
            assert set(fold["fit_row_indices"]).isdisjoint(fold["validation_row_indices"])
            for i in fold["validation_row_indices"]:
                coverage[i] += 1
        assert coverage == [5] * 60
    best = min(report["threshold_candidates"],
               key=lambda r: (r["cost"], r["flagged_count"], -r["threshold"]))
    assert best["threshold"] == report["threshold"]["probability_threshold"]
