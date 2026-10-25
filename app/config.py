import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "configs"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "debate_judge.sqlite3"

with open(CONFIG_DIR / "model_config.json", encoding="utf-8") as f:
    MODEL_CONFIG = json.load(f)
with open(CONFIG_DIR / "rubric_v1.json", encoding="utf-8") as f:
    RUBRIC = json.load(f)

DATA_DIR.mkdir(parents=True, exist_ok=True)
