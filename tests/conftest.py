import json
from pathlib import Path

import pytest

from scripts.current_demo import demo_batch
from urbaneats.config import ROOT, Config
from urbaneats.service import create_app


@pytest.fixture
def batch():
    return demo_batch()


@pytest.fixture
def config(tmp_path):
    return Config(model_dir=ROOT / "artifacts/model", runs_dir=tmp_path / "runs",
                  source_file=tmp_path / "source.json")


@pytest.fixture
def runtime(config):
    return create_app(config).state.runtime


@pytest.fixture
def artifact_metadata():
    path = ROOT / "artifacts/model/metadata.json"
    assert path.exists(), "Run python -m evaluation.evaluate first"
    return json.loads(Path(path).read_text())
