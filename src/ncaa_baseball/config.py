from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

@dataclass(slots=True)
class Config:
    data_dir: Path = Path("data")

    raw_dir: Path = Path("data/raw")
    raw_scoreboard_dir: Path = Path("data/raw/scoreboards")
    raw_contest_dir: Path = Path("data/raw/contests")
    raw_team_dir: Path = Path("data/raw/teams")
    raw_player_dir: Path = Path("data/raw/players")

    metadata_dir: Path = Path("data/metadata")
    parquet_dir: Path = Path("data/parquet")

    headless: bool = True

    min_delay_seconds: float = 5.0
    max_delay_seconds: float = 10.0

    navigation_timeout_ms: int = 45_000

    max_retries: int = 2


def load_config() -> Config:
    return Config()
