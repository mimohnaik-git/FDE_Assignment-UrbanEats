import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError

from urbaneats.config import ROOT
from urbaneats.features import FEATURES, PROHIBITED, feature_frame
from urbaneats.model import build_pipeline, load_artifact


def test_prohibited_features_excluded(batch):
    assert not set(FEATURES) & PROHIBITED
    records = [dict(batch["orders"][0], order_status="Cancelled", delivery_time_mins=100)]
    assert list(feature_frame(records).columns) == FEATURES


def test_transforms_unfitted_until_fold_fit():
    import pytest

    pipeline = build_pipeline("logistic")
    with pytest.raises(NotFittedError):
        pipeline.predict_proba(pd.DataFrame(columns=FEATURES))
    assert not hasattr(pipeline.named_steps["preprocess"], "transformers_")
    df = pd.DataFrame({
        "restaurant_name": ["A", "B", "A", "B", "ONLY_IN_VALIDATION"],
        "delivery_zone": ["North"] * 5, "payment_method": ["UPI"] * 5,
        "order_value": [100., 200., 300., 400., 99999.], "discount_applied": [0.] * 5,
    })
    pipeline.fit(df.iloc[:4], [0, 1, 0, 1])
    transform = pipeline.named_steps["preprocess"]
    encoder = transform.named_transformers_["categorical"].named_steps["encode"]
    imputer = transform.named_transformers_["numeric"].named_steps["impute"]
    assert "ONLY_IN_VALIDATION" not in encoder.categories_[0]
    assert imputer.statistics_[0] == 250
    assert np.isfinite(pipeline.predict_proba(df.iloc[4:])).all()


def test_saved_artifact_loads(artifact_metadata):
    pipeline, metadata, threshold = load_artifact(ROOT / "artifacts/model")
    assert list(pipeline.feature_names_in_) == FEATURES
    assert metadata == artifact_metadata
    assert 0 < threshold["probability_threshold"] < 1


def test_artifact_corruption_rejected(tmp_path):
    import shutil

    import pytest

    for path in (ROOT / "artifacts/model").glob("*"):
        if path.is_file():
            shutil.copy2(path, tmp_path / path.name)
    with (tmp_path / "pipeline.joblib").open("ab") as handle:
        handle.write(b"corrupt")
    with pytest.raises(ValueError, match="integrity"):
        load_artifact(tmp_path)
