import copy
import json
from pathlib import Path

from utils.paths import get_app_storage_dir


DEFAULT_CONFIG = {
    "company": {
        "name": "Your Enterprise Name",
        "sector": "Manufacturing",
        "facility": "Plant-A",
        "city": "Location",
        "employees": 0,
        "qe": "Admin",
    },
    "lines": [
        {"name": "Main Line", "shifts": 3, "target": 300},
    ],
    "quality": {
        "defects": [
            "Dimensional Deviation",
            "Surface Defect",
            "Porosity",
            "Shrinkage",
            "Flash",
        ],
        "scrap_target": 2.0,
        "default_total_produced": 300,
        "require_photo": False,
        "notes_enabled": True,
    },
    "spc_points": [
        {"point": "Diameter-A", "nom": 50.00, "usl": 50.10, "lsl": 49.90},
        {"point": "Diameter-B", "nom": 25.00, "usl": 25.05, "lsl": 24.95},
    ],
    "shifts": [
        {"name": "Shift 1 (08-16)", "label": "Morning", "start": 8, "end": 16, "active": True},
        {"name": "Shift 2 (16-00)", "label": "Evening", "start": 16, "end": 0, "active": True},
        {"name": "Shift 3 (00-08)", "label": "Night", "start": 0, "end": 8, "active": True},
    ],
    "notifications": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_pass": "",
        "target_email": "",
    },
}


CONFIG_PATH = get_app_storage_dir() / "settings.json"


def default_config() -> dict:
    return copy.deepcopy(DEFAULT_CONFIG)


def _deep_merge(defaults: dict, saved: dict) -> dict:
    merged = copy.deepcopy(defaults)
    for key, value in saved.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def normalize_config(config: dict | None) -> dict:
    cfg = _deep_merge(DEFAULT_CONFIG, config or {})

    cfg["lines"] = [
        {
            "name": str(line.get("name") or "Line").strip() or "Line",
            "shifts": int(line.get("shifts") or 3),
            "target": int(line.get("target") or cfg["quality"]["default_total_produced"]),
        }
        for line in cfg.get("lines", [])
    ] or copy.deepcopy(DEFAULT_CONFIG["lines"])

    cfg["quality"]["defects"] = [
        str(defect).strip()
        for defect in cfg["quality"].get("defects", [])
        if str(defect).strip()
    ] or copy.deepcopy(DEFAULT_CONFIG["quality"]["defects"])

    cfg["spc_points"] = [
        {
            "point": str(point.get("point") or "Measurement Point").strip() or "Measurement Point",
            "nom": float(point.get("nom") or 0),
            "usl": float(point.get("usl") or 0),
            "lsl": float(point.get("lsl") or 0),
        }
        for point in cfg.get("spc_points", [])
    ] or copy.deepcopy(DEFAULT_CONFIG["spc_points"])

    cfg["shifts"] = [
        {
            "name": str(shift.get("name") or "Shift").strip() or "Shift",
            "label": shift.get("label", ""),
            "start": int(shift.get("start") or 0),
            "end": int(shift.get("end") or 0),
            "active": bool(shift.get("active", True)),
        }
        for shift in cfg.get("shifts", [])
    ] or copy.deepcopy(DEFAULT_CONFIG["shifts"])

    cfg["notifications"]["smtp_port"] = int(cfg["notifications"].get("smtp_port") or 587)
    cfg["quality"]["scrap_target"] = float(cfg["quality"].get("scrap_target") or 0)
    cfg["quality"]["default_total_produced"] = int(cfg["quality"].get("default_total_produced") or 1)
    cfg["quality"]["require_photo"] = bool(cfg["quality"].get("require_photo", False))
    cfg["quality"]["notes_enabled"] = bool(cfg["quality"].get("notes_enabled", True))
    return cfg


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return default_config()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            return normalize_config(json.load(fh))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return default_config()


def save_config(config: dict) -> dict:
    cfg = normalize_config(config)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = Path(f"{CONFIG_PATH}.tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
    tmp_path.replace(CONFIG_PATH)
    return cfg
