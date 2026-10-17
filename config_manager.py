""" JSON module practice: load, update, and save configs."""

import json
from datetime import datetime
from pathlib import Path


class UserPreference:
    def __init__(self, theme: str, notifications_enabled: bool, last_updated: datetime):
        self.theme = theme
        self.notifications_enabled = notifications_enabled
        self.last_updated = last_updated

    def __repr__(self):
        return (f"UserPreference(theme={self.theme!r}, "
                f"notifications_enabled={self.notifications_enabled}, "
                f"last_updated={self.last_updated.isoformat()})")


# ---------- Decoding ----------

PREF_KEYS = {"theme", "notifications_enabled", "last_updated"}


def _preference_hook(obj: dict):
    """object_hook: turn matching dicts into UserPreference instances."""
    if PREF_KEYS.issubset(obj):
        return UserPreference(
            theme=obj["theme"],
            notifications_enabled=obj["notifications_enabled"],
            # Replace a trailing 'Z' so this also works on Python < 3.11
            last_updated=datetime.fromisoformat(obj["last_updated"].replace("Z", "+00:00")),
        )
    return obj


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_hook=_preference_hook)


# ---------- Modifying ----------

def update_preference(config: dict, user_id: str, new_pref: UserPreference) -> None:
    """Insert or replace a user's preference under config['users']."""
    config.setdefault("users", {})[user_id] = new_pref


# ---------- Encoding ----------

class ConfigEncoder(json.JSONEncoder):
    """Serializes UserPreference and datetime objects (datetimes as ISO-8601)."""

    def default(self, obj):
        if isinstance(obj, UserPreference):
            return {
                "theme": obj.theme,
                "notifications_enabled": obj.notifications_enabled,
                "last_updated": obj.last_updated,  # handled by the datetime branch
            }
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def save_config(config: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, cls=ConfigEncoder, indent=4)


# ---------- Demo script ----------

if __name__ == "__main__":
    CONFIG_PATH = "config.json"

    # Seed a starter file if none exists so the demo runs out of the box
    if not Path(CONFIG_PATH).exists():
        save_config({"app_name": "mytool", "version": "1.0", "users": {}}, CONFIG_PATH)

    config = load_config(CONFIG_PATH)
    print("Loaded:", config)

    new_pref = UserPreference(
        theme="dark",
        notifications_enabled=True,
        last_updated=datetime.now(),
    )
    update_preference(config, "user_123", new_pref)

    save_config(config, CONFIG_PATH)
    print("Saved updated config to", CONFIG_PATH)