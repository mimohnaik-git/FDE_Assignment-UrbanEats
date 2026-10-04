"""Repeated OOF selection on development data, then untouched stratified holdout.

Run: python -m evaluation.evaluate
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path

from urbaneats.config import ROOT
from urbaneats.features import FEATURE_CONTRACT, FEATURES
from urbaneats.model import build_pipeline


def measures(y, probability, threshold):
    from sklearn.metrics import (
        average_precision_score,
        brier_score_loss,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    labels = probability >= threshold
    return {
        "sample_count": len(y), "positives": int(sum(y)),
        "precision": float(precision_score(y, labels, zero_division=0)),
        "recall": float(recall_score(y, labels, zero_division=0)),
        "f1": float(f1_score(y, labels, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probability)),
        "pr_auc_average_precision": float(average_precision_score(y, probability)),
        "brier": float(brier_score_loss(y, probability)),
        "confusion_matrix_tn_fp_fn_tp": confusion_matrix(y, labels, labels=[0, 1]).ravel().tolist(),
        "flagged_count": int(sum(labels)),
    }


def repeated_oof(x, y, candidate):
    import numpy as np
    from sklearn.model_selection import RepeatedStratifiedKFold

    sums = np.zeros(len(y))
    counts = np.zeros(len(y), dtype=int)
    folds = []
    splitter = RepeatedStratifiedKFold(n_splits=4, n_repeats=5, random_state=42)
    for fold, (train, valid) in enumerate(splitter.split(x, y)):
        pipeline = build_pipeline(candidate)
        pipeline.fit(x.iloc[train], y[train])
        p = pipeline.predict_proba(x.iloc[valid])[:, 1]
        sums[valid] += p
        counts[valid] += 1
        folds.append({"fold": fold, "fit_row_indices": train.tolist(),
                      "validation_row_indices": valid.tolist()})
    if not np.all(counts == 5):
        raise ValueError("Incomplete OOF coverage")
    return sums / counts, folds


def evaluate(root: Path = ROOT):
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split

    source = root / "urbaneats_delivery_orders.csv"
    df = pd.read_csv(source)
    population = df[df.order_status.isin(["Delivered", "Cancelled"])].reset_index(drop=True)
    x = population[FEATURES]
    y = (population.order_status == "Cancelled").astype(int).to_numpy()
    dev, holdout = train_test_split(np.arange(len(y)), test_size=.25, stratify=y, random_state=42)
    xd, yd = x.iloc[dev].reset_index(drop=True), y[dev]
    candidates = {}
    tables = []
    oofs = {}
    for candidate in ["dummy", "logistic", "random_forest"]:
        probability, folds = repeated_oof(xd, yd, candidate)
        oofs[candidate] = probability
        candidates[candidate] = {"oof_metrics_at_0_5": measures(yd, probability, .5),
                                 "fold_membership": folds}
    # Candidate selection is development OOF PR-AUC, with deterministic tie order.
    selected = max(["logistic", "random_forest"], key=lambda name: (
        candidates[name]["oof_metrics_at_0_5"]["pr_auc_average_precision"],
        name == "logistic",
    ))
    probability = oofs[selected]
    for threshold in np.arange(.10, .91, .05):
        threshold = round(float(threshold), 2)
        m = measures(yd, probability, threshold)
        _, fp, fn, _ = m["confusion_matrix_tn_fp_fn_tp"]
        tables.append({"threshold": threshold, "cost": 2 * fn + fp, **m})
    chosen = min(tables, key=lambda row: (row["cost"], row["flagged_count"], -row["threshold"]))
    threshold_config = {
        "probability_threshold": chosen["threshold"],
        "selection_data": "development repeated OOF; not independent validation",
        "policy": "demo cost: missed cancellation=2, false review=1; tie favors fewer reviews",
        "selection_metrics": chosen,
        "calibration": "not calibrated; insufficient data for robust calibration",
    }
    # Holdout touched only after both candidate and threshold are frozen.
    selected_pipeline = build_pipeline(selected)
    selected_pipeline.fit(x.iloc[dev], y[dev])
    hold_probability = selected_pipeline.predict_proba(x.iloc[holdout])[:, 1]
    hold_metrics = measures(y[holdout], hold_probability, chosen["threshold"])
    dummy = build_pipeline("dummy")
    dummy.fit(x.iloc[dev], y[dev])
    dummy_hold = measures(y[holdout], dummy.predict_proba(x.iloc[holdout])[:, 1], chosen["threshold"])
    report = {
        "dataset_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "population": {"included": len(y), "Delivered": int(sum(y == 0)),
                       "Cancelled": int(sum(y)), "excluded_Delayed_Refunded": len(df) - len(y)},
        "development_count": len(dev), "holdout_count": len(holdout),
        "strategy": "stratified 75/25 split seed 42; development 4-fold x 5-repeat stratified OOF",
        "selection_metric": "development OOF average precision; threshold cost=2FN+FP",
        "candidates": candidates, "threshold_candidates": tables,
        "selected_model": selected, "threshold": threshold_config,
        "independent_holdout_metrics": hold_metrics, "dummy_holdout_metrics": dummy_hold,
        "development_order_ids": population.iloc[dev].order_id.tolist(),
        "holdout_order_ids": population.iloc[holdout].order_id.tolist(),
        "limitations": [
            "Synthetic n=80; no production-quality or calibrated-probability claims",
            "Conditional Delivered/Cancelled target; Delayed/Refunded outside supervised scope",
            "Random holdout does not establish temporal generalization or label maturity",
            "Development metrics are selection evidence and optimistic for final choices",
            "Final artifact refits all 80 labels after holdout evaluation; no independent final-artifact test",
        ],
    }
    results = root / "evaluation/results"
    results.mkdir(parents=True, exist_ok=True)
    (results / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame({"order_id": population.iloc[dev].order_id.to_numpy(), "target": yd,
                  **{f"{k}_oof_probability": v for k, v in oofs.items()}}).to_csv(
        results / "development_oof.csv", index=False
    )
    pd.DataFrame({"order_id": population.iloc[holdout].order_id.to_numpy(),
                  "target": y[holdout], "probability": hold_probability}).to_csv(
        results / "holdout.csv", index=False
    )
    final = build_pipeline(selected)
    final.fit(x, y)
    directory = root / "artifacts/model"
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(final, directory / "pipeline.joblib")
    dependencies = {name: importlib.metadata.version(name) for name in [
        "scikit-learn", "numpy", "pandas", "scipy", "joblib", "threadpoolctl",
    ]}
    version = "UE-" + hashlib.sha256(json.dumps({
        "data": report["dataset_sha256"], "selected": selected,
        "threshold": chosen["threshold"], "features": FEATURE_CONTRACT,
        "dependencies": dependencies, "seed": 42,
    }, sort_keys=True).encode()).hexdigest()[:16]
    metadata = {
        "model_version": version, "candidate": selected, "dependencies": dependencies,
        "artifact_sha256": hashlib.sha256((directory / "pipeline.joblib").read_bytes()).hexdigest(),
        "training_rows": len(y), "features": FEATURES, "seed": 42,
        "source_sha256": report["dataset_sha256"], "target_population": FEATURE_CONTRACT["target"],
        "production_ready": False,
    }
    for name, value in [("threshold", threshold_config), ("feature_contract", FEATURE_CONTRACT)]:
        (directory / f"{name}.json").write_text(json.dumps(value, indent=2), encoding="utf-8")
        metadata[f"{name}_sha256"] = hashlib.sha256(
            (directory / f"{name}.json").read_bytes()
        ).hexdigest()
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"model": selected, "threshold": chosen["threshold"],
                      "holdout": hold_metrics, "dummy_holdout": dummy_hold}, indent=2))
    return report


if __name__ == "__main__":
    evaluate()
