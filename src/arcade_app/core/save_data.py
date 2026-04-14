from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SAVE_DATA = {
    "app": {
        "last_played_game_id": None,
        "recent_game_ids": [],
        "updated_at": None,
        "settings": {
            "fullscreen": False,
            "sound_enabled": True,
            "music_enabled": True,
        },
    },
    "games": {},
}


class SaveDataManager:
    def __init__(self, app_name: str = "PythonArcade") -> None:
        self.app_name = app_name
        self.save_dir = self._build_save_dir()
        self.save_file = self.save_dir / "save_data.json"
        self.data: dict[str, Any] = deepcopy(DEFAULT_SAVE_DATA)

        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.load()

    def _build_save_dir(self) -> Path:
        roaming = Path.home() / "AppData" / "Roaming"
        if roaming.exists():
            return roaming / self.app_name

        return Path.home() / f".{self.app_name.lower()}"

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def load(self) -> None:
        if not self.save_file.exists():
            self.save()
            return

        try:
            loaded = json.loads(self.save_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.data = deepcopy(DEFAULT_SAVE_DATA)
                self.data.update(loaded)

                if "app" not in self.data or not isinstance(self.data["app"], dict):
                    self.data["app"] = deepcopy(DEFAULT_SAVE_DATA["app"])

                if "games" not in self.data or not isinstance(self.data["games"], dict):
                    self.data["games"] = {}

                app_settings = self.data["app"].get("settings")
                if not isinstance(app_settings, dict):
                    self.data["app"]["settings"] = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
                else:
                    merged_settings = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
                    merged_settings.update(app_settings)
                    self.data["app"]["settings"] = merged_settings

                recent_games = self.data["app"].get("recent_game_ids")
                if not isinstance(recent_games, list):
                    self.data["app"]["recent_game_ids"] = []
        except (json.JSONDecodeError, OSError):
            self.data = deepcopy(DEFAULT_SAVE_DATA)
            self.save()

    def save(self) -> None:
        self.data["app"]["updated_at"] = self._timestamp()
        self.save_file.write_text(
            json.dumps(self.data, indent=2),
            encoding="utf-8",
        )

    def ensure_game_entry(self, game_id: str) -> dict[str, Any]:
        games = self.data.setdefault("games", {})
        if game_id not in games:
            games[game_id] = {
                "play_count": 0,
                "last_score": None,
                "best_score": None,
                "best_round": None,
                "best_wave": None,
                "best_lines": None,
                "best_hits": None,
                "best_accuracy": None,
                "best_reaction_ms": None,
                "last_played_at": None,
            }
        return games[game_id]

    def set_last_played(self, game_id: str) -> None:
        self.data["app"]["last_played_game_id"] = game_id

        recent_ids = self.data["app"].setdefault("recent_game_ids", [])
        recent_ids = [existing for existing in recent_ids if existing != game_id]
        recent_ids.insert(0, game_id)
        self.data["app"]["recent_game_ids"] = recent_ids[:5]

        game_entry = self.ensure_game_entry(game_id)
        game_entry["last_played_at"] = self._timestamp()
        self.save()

    def record_game_session(self, game_id: str, payload: dict[str, Any]) -> None:
        game_entry = self.ensure_game_entry(game_id)

        game_entry["play_count"] += 1
        game_entry["last_played_at"] = self._timestamp()

        score = payload.get("score")
        if isinstance(score, int):
            game_entry["last_score"] = score
            best_score = game_entry.get("best_score")
            if best_score is None or score > best_score:
                game_entry["best_score"] = score

        round_value = payload.get("round")
        if isinstance(round_value, int):
            best_round = game_entry.get("best_round")
            if best_round is None or round_value > best_round:
                game_entry["best_round"] = round_value

        wave_value = payload.get("wave")
        if isinstance(wave_value, int):
            best_wave = game_entry.get("best_wave")
            if best_wave is None or wave_value > best_wave:
                game_entry["best_wave"] = wave_value

        lines_value = payload.get("lines")
        if isinstance(lines_value, int):
            best_lines = game_entry.get("best_lines")
            if best_lines is None or lines_value > best_lines:
                game_entry["best_lines"] = lines_value

        hits_value = payload.get("hits")
        if isinstance(hits_value, int):
            best_hits = game_entry.get("best_hits")
            if best_hits is None or hits_value > best_hits:
                game_entry["best_hits"] = hits_value

        accuracy_value = payload.get("accuracy")
        if isinstance(accuracy_value, (int, float)):
            accuracy_float = float(accuracy_value)
            best_accuracy = game_entry.get("best_accuracy")
            if best_accuracy is None or accuracy_float > best_accuracy:
                game_entry["best_accuracy"] = round(accuracy_float, 1)

        reaction_ms_value = payload.get("reaction_ms")
        if isinstance(reaction_ms_value, int):
            best_reaction = game_entry.get("best_reaction_ms")
            if best_reaction is None or reaction_ms_value < best_reaction:
                game_entry["best_reaction_ms"] = reaction_ms_value

        self.save()

    def get_last_played_game_id(self) -> str | None:
        return self.data.get("app", {}).get("last_played_game_id")

    def get_recent_game_ids(self) -> list[str]:
        recent_games = self.data.get("app", {}).get("recent_game_ids", [])
        if isinstance(recent_games, list):
            return [game_id for game_id in recent_games if isinstance(game_id, str)]
        return []

    def get_game_stats(self, game_id: str) -> dict[str, Any]:
        return deepcopy(self.data.get("games", {}).get(game_id, {}))

    def get_settings(self) -> dict[str, Any]:
        settings = self.data.get("app", {}).get("settings", {})
        merged = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
        if isinstance(settings, dict):
            merged.update(settings)
        return merged

    def set_setting(self, key: str, value: Any) -> None:
        app_data = self.data.setdefault("app", {})
        settings = app_data.setdefault("settings", deepcopy(DEFAULT_SAVE_DATA["app"]["settings"]))
        settings[key] = value
        self.save()