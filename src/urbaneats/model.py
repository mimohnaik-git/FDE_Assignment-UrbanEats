import hashlib
import importlib.metadata
import json

from .features import CATEGORICAL, FEATURE_CONTRACT, FEATURES, NUMERIC


def build_pipeline(candidate, seed=42):
    from sklearn.compose import ColumnTransformer
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    estimators = {
        "logistic": LogisticRegression(max_iter=2000, random_state=seed),
        "random_forest": RandomForestClassifier(
            n_estimators=200, min_samples_leaf=3, random_state=seed, n_jobs=1
        ),
        "dummy": DummyClassifier(strategy="prior"),
    }
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    return Pipeline([
        ("preprocess", ColumnTransformer([
            ("categorical", categorical, CATEGORICAL), ("numeric", numeric, NUMERIC),
        ], remainder="drop")),
        ("classifier", estimators[candidate]),
    ])


def load_artifact(directory):
    """Load locally trusted joblib only, checking saved contract and digest."""
    import joblib

    metadata = json.loads((directory / "metadata.json").read_text())
    threshold = json.loads((directory / "threshold.json").read_text())
    contract = json.loads((directory / "feature_contract.json").read_text())
    path = directory / "pipeline.joblib"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != metadata["artifact_sha256"] or contract != FEATURE_CONTRACT:
        raise ValueError("Artifact integrity or feature contract mismatch")
    for name in ["threshold", "feature_contract"]:
        if hashlib.sha256((directory / f"{name}.json").read_bytes()).hexdigest() != metadata[
            f"{name}_sha256"
        ]:
            raise ValueError("Artifact configuration integrity mismatch")
    for name, version in metadata["dependencies"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError("Artifact dependency version mismatch")
    if not 0 < threshold["probability_threshold"] < 1:
        raise ValueError("Invalid threshold")
    pipeline = joblib.load(path)
    if list(pipeline.feature_names_in_) != FEATURES:
        raise ValueError("Artifact predictors mismatch")
    if list(pipeline.classes_) != [0, 1]:
        raise ValueError("Artifact classes mismatch")
    return pipeline, metadata, threshold
