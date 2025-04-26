import json
import os
from pathlib import Path

# Config file for mappings and settings
_CONFIG_PATH = Path.home() / '.reminder_warrior_config.json'

def get_config_path() -> str:
    return str(_CONFIG_PATH)

def load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        with open(_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        bak = _CONFIG_PATH.with_suffix('.bak')
        os.replace(str(_CONFIG_PATH), str(bak))
        return {}

def save_config(cfg: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)