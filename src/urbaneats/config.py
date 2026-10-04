import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    model_dir: Path = ROOT / "artifacts/model"
    runs_dir: Path = ROOT / "runs"
    source_file: Path = ROOT / "data/current_batch.json"
    max_age_seconds: int = 3600
    min_support: int = 20
    hotspot_rate: float = 0.30

    def __post_init__(self):
        if self.max_age_seconds <= 0 or self.min_support < 20:
            raise ValueError("Freshness must be positive; minimum support must be at least 20")
        if not 0 < self.hotspot_rate <= 1:
            raise ValueError("Hotspot rate must be in (0, 1]")

    @classmethod
    def from_env(cls):
        return cls(
            model_dir=Path(os.getenv("URBANEATS_MODEL_DIR", ROOT / "artifacts/model")),
            runs_dir=Path(os.getenv("URBANEATS_RUNS_DIR", ROOT / "runs")),
            source_file=Path(os.getenv("URBANEATS_SOURCE_FILE", ROOT / "data/current_batch.json")),
            max_age_seconds=int(os.getenv("URBANEATS_MAX_AGE_SECONDS", "3600")),
            min_support=int(os.getenv("URBANEATS_MIN_SUPPORT", "20")),
            hotspot_rate=float(os.getenv("URBANEATS_HOTSPOT_RATE", "0.30")),
        )
