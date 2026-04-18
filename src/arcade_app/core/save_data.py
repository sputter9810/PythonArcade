from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arcade_app.platform.achievements import build_achievement_rows, evaluate_achievements, get_achievement_row_map

DEFAULT_PROFILE_NAME = "Player One"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_profile(profile_id: str = "default", name: str = DEFAULT_PROFILE_NAME) -> dict[str, Any]:
    timestamp = _timestamp()
    return {
        "id": profile_id,
        "name": name,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_played_game_id": None,
        "recent_game_ids": [],
        "favorites": [],
        "games": {},
        "achievements": {
            "unlocked": {},
            "recent_unlocks": [],
            "popup_queue": [],
            "progress": {},
        },
        "last_run_summaries": {},
        "daily_challenges": {
            "history": {},
        },
    }


DEFAULT_SAVE_DATA = {
    "schema_version": 6,
    "app": {
        "active_profile_id": "default",
        "updated_at": None,
        "settings": {
            "fullscreen": False,
            "sound_enabled": True,
            "music_enabled": True,
        },
    },
    "profiles": {
        "default": _default_profile(),
    },
    "leaderboards": {},
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

    def _touch_profile(self, profile: dict[str, Any]) -> None:
        profile["updated_at"] = _timestamp()

    def _ensure_profiles_shape(self) -> None:
        profiles = self.data.get("profiles")
        if not isinstance(profiles, dict) or not profiles:
            self.data["profiles"] = deepcopy(DEFAULT_SAVE_DATA["profiles"])
            self.data["app"]["active_profile_id"] = "default"
            return

        for profile_id, profile in list(profiles.items()):
            if not isinstance(profile, dict):
                profiles[profile_id] = _default_profile(profile_id=profile_id, name=f"Player {profile_id}")
                continue

            merged = _default_profile(profile_id=profile_id, name=str(profile.get("name") or f"Player {profile_id}"))
            merged.update(profile)

            if not isinstance(merged.get("recent_game_ids"), list):
                merged["recent_game_ids"] = []
            if not isinstance(merged.get("favorites"), list):
                merged["favorites"] = []
            if not isinstance(merged.get("games"), dict):
                merged["games"] = {}
            if not isinstance(merged.get("last_run_summaries"), dict):
                merged["last_run_summaries"] = {}
            if not isinstance(merged.get("daily_challenges"), dict):
                merged["daily_challenges"] = {"history": {}}
            if not isinstance(merged["daily_challenges"].get("history"), dict):
                merged["daily_challenges"]["history"] = {}

            achievements = merged.get("achievements")
            if not isinstance(achievements, dict):
                achievements = deepcopy(_default_profile()["achievements"])
            else:
                base = deepcopy(_default_profile()["achievements"])
                base.update(achievements)
                achievements = base

            # migrate old stage 3 shape
            if "unlocked_ids" in achievements and "unlocked" not in achievements:
                unlocked_map: dict[str, str] = {}
                old_ids = achievements.get("unlocked_ids", [])
                if isinstance(old_ids, list):
                    for achievement_id in old_ids:
                        if isinstance(achievement_id, str):
                            unlocked_map[achievement_id] = _timestamp()
                achievements["unlocked"] = unlocked_map

            if not isinstance(achievements.get("unlocked"), dict):
                achievements["unlocked"] = {}
            if not isinstance(achievements.get("recent_unlocks"), list):
                achievements["recent_unlocks"] = []
            if not isinstance(achievements.get("popup_queue"), list):
                achievements["popup_queue"] = []
            if not isinstance(achievements.get("progress"), dict):
                achievements["progress"] = {}

            achievements["recent_unlocks"] = [
                entry if isinstance(entry, str) else str(entry.get("achievement_id", ""))
                for entry in achievements["recent_unlocks"]
                if (isinstance(entry, str) and entry) or (isinstance(entry, dict) and entry.get("achievement_id"))
            ][:20]
            achievements["popup_queue"] = [
                entry if isinstance(entry, str) else str(entry.get("achievement_id", ""))
                for entry in achievements["popup_queue"]
                if (isinstance(entry, str) and entry) or (isinstance(entry, dict) and entry.get("achievement_id"))
            ][:20]

            merged["achievements"] = achievements
            profiles[profile_id] = merged

        active_profile_id = self.data.get("app", {}).get("active_profile_id")
        if active_profile_id not in profiles:
            self.data["app"]["active_profile_id"] = next(iter(profiles.keys()))

    def _ensure_leaderboards_shape(self) -> None:
        leaderboards = self.data.get("leaderboards")
        if not isinstance(leaderboards, dict):
            self.data["leaderboards"] = {}
            return

        cleaned: dict[str, list[dict[str, Any]]] = {}
        for game_id, entries in leaderboards.items():
            if not isinstance(game_id, str) or not isinstance(entries, list):
                continue
            valid_entries: list[dict[str, Any]] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                valid_entries.append(
                    {
                        "game_id": str(entry.get("game_id", game_id)),
                        "score": entry.get("score"),
                        "duration_seconds": entry.get("duration_seconds", entry.get("duration")),
                        "metadata": entry.get("metadata", {}) if isinstance(entry.get("metadata", {}), dict) else {},
                        "profile_id": entry.get("profile_id"),
                        "profile_name": entry.get("profile_name"),
                        "created_at": entry.get("created_at"),
                        "rank": entry.get("rank"),
                    }
                )
            cleaned[game_id] = valid_entries
        self.data["leaderboards"] = cleaned

    def _migrate_legacy_data(self, loaded: dict[str, Any]) -> dict[str, Any]:
        migrated = deepcopy(DEFAULT_SAVE_DATA)
        if not isinstance(loaded, dict):
            return migrated

        if "profiles" in loaded:
            migrated.update(loaded)
            app_data = migrated.get("app", {})
            if not isinstance(app_data, dict):
                app_data = deepcopy(DEFAULT_SAVE_DATA["app"])
            settings = app_data.get("settings")
            if not isinstance(settings, dict):
                app_data["settings"] = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
            else:
                merged_settings = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
                merged_settings.update(settings)
                app_data["settings"] = merged_settings
            migrated["app"] = app_data
            migrated["schema_version"] = max(6, int(migrated.get("schema_version", 6)))
            self.data = migrated
            self._ensure_profiles_shape()
            self._ensure_leaderboards_shape()
            return self.data

        old_app = loaded.get("app", {})
        old_games = loaded.get("games", {})
        old_favorites = loaded.get("favorites", [])
        old_recent = loaded.get("recent_games", [])
        old_last_played = loaded.get("last_played")
        old_profile = loaded.get("profile", {})
        old_leaderboards = loaded.get("leaderboards", {})

        profile_name = DEFAULT_PROFILE_NAME
        if isinstance(old_profile, dict):
            profile_name = str(old_profile.get("name") or DEFAULT_PROFILE_NAME)

        profile = _default_profile(name=profile_name)
        profile["last_played_game_id"] = old_last_played if isinstance(old_last_played, str) else None
        profile["recent_game_ids"] = [gid for gid in old_recent if isinstance(gid, str)][:5]
        profile["favorites"] = [gid for gid in old_favorites if isinstance(gid, str)]
        if isinstance(old_games, dict):
            profile["games"] = deepcopy(old_games)
        if isinstance(old_app, dict):
            settings = old_app.get("settings")
            if isinstance(settings, dict):
                merged_settings = deepcopy(DEFAULT_SAVE_DATA["app"]["settings"])
                merged_settings.update(settings)
                migrated["app"]["settings"] = merged_settings
        migrated["profiles"]["default"] = profile
        migrated["app"]["active_profile_id"] = "default"
        if isinstance(old_leaderboards, dict):
            migrated["leaderboards"] = deepcopy(old_leaderboards)

        self.data = migrated
        self._ensure_profiles_shape()
        self._ensure_leaderboards_shape()
        return self.data

    def load(self) -> None:
        if not self.save_file.exists():
            self.save()
            return
        try:
            loaded = json.loads(self.save_file.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("Save data root must be an object.")
            self.data = self._migrate_legacy_data(loaded)
            self.save()
        except (json.JSONDecodeError, OSError, ValueError):
            self.data = deepcopy(DEFAULT_SAVE_DATA)
            self.save()

    def save(self) -> None:
        self.data["schema_version"] = 6
        self.data["app"]["updated_at"] = _timestamp()
        self.save_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

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

    def list_profiles(self) -> list[dict[str, Any]]:
        profiles = self.data.get("profiles", {})
        if not isinstance(profiles, dict):
            return []
        active_profile_id = self.get_active_profile_id()
        summaries: list[dict[str, Any]] = []
        for profile_id, profile in profiles.items():
            if not isinstance(profile, dict):
                continue
            games = profile.get("games", {})
            total_sessions = 0
            unique_games = 0
            if isinstance(games, dict):
                unique_games = len([value for value in games.values() if isinstance(value, dict)])
                total_sessions = sum(int(entry.get("play_count", 0)) for entry in games.values() if isinstance(entry, dict))
            achievement_count = len(self._get_unlocked_map(profile))
            summaries.append({
                "id": profile_id,
                "name": str(profile.get("name", DEFAULT_PROFILE_NAME)),
                "is_active": profile_id == active_profile_id,
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at"),
                "total_sessions": total_sessions,
                "unique_games": unique_games,
                "favorites_count": len(profile.get("favorites", [])) if isinstance(profile.get("favorites"), list) else 0,
                "achievement_count": achievement_count,
            })
        summaries.sort(key=lambda item: (not item["is_active"], item["name"].lower()))
        return summaries

    def get_active_profile_id(self) -> str:
        profiles = self.data.setdefault("profiles", deepcopy(DEFAULT_SAVE_DATA["profiles"]))
        active_profile_id = self.data.setdefault("app", {}).get("active_profile_id")
        if active_profile_id not in profiles:
            active_profile_id = next(iter(profiles.keys()))
            self.data["app"]["active_profile_id"] = active_profile_id
        return active_profile_id

    def get_active_profile(self) -> dict[str, Any]:
        profile_id = self.get_active_profile_id()
        profiles = self.data.setdefault("profiles", deepcopy(DEFAULT_SAVE_DATA["profiles"]))
        profile = profiles.setdefault(profile_id, _default_profile(profile_id=profile_id))
        return profile

    def get_active_profile_name(self) -> str:
        return str(self.get_active_profile().get("name", DEFAULT_PROFILE_NAME))

    def set_active_profile(self, profile_id: str) -> bool:
        profiles = self.data.get("profiles", {})
        if not isinstance(profiles, dict) or profile_id not in profiles:
            return False
        self.data["app"]["active_profile_id"] = profile_id
        self.save()
        return True

    def create_profile(self, name: str) -> str:
        cleaned_name = name.strip()[:24] or "New Player"
        profile_id = uuid.uuid4().hex[:8]
        profiles = self.data.setdefault("profiles", {})
        while profile_id in profiles:
            profile_id = uuid.uuid4().hex[:8]
        profiles[profile_id] = _default_profile(profile_id=profile_id, name=cleaned_name)
        self.data["app"]["active_profile_id"] = profile_id
        self.save()
        return profile_id

    def rename_profile(self, profile_id: str, new_name: str) -> bool:
        profiles = self.data.get("profiles", {})
        if not isinstance(profiles, dict) or profile_id not in profiles:
            return False
        cleaned_name = new_name.strip()[:24]
        if not cleaned_name:
            return False
        profiles[profile_id]["name"] = cleaned_name
        self._touch_profile(profiles[profile_id])
        self.save()
        return True

    def delete_profile(self, profile_id: str) -> bool:
        profiles = self.data.get("profiles", {})
        if not isinstance(profiles, dict) or profile_id not in profiles or len(profiles) <= 1:
            return False
        del profiles[profile_id]
        if self.data.get("app", {}).get("active_profile_id") == profile_id:
            self.data["app"]["active_profile_id"] = next(iter(profiles.keys()))
        self.save()
        return True

    def ensure_game_entry(self, game_id: str) -> dict[str, Any]:
        profile = self.get_active_profile()
        games = profile.setdefault("games", {})
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
        profile = self.get_active_profile()
        profile["last_played_game_id"] = game_id
        recent_ids = profile.setdefault("recent_game_ids", [])
        recent_ids = [existing for existing in recent_ids if existing != game_id]
        recent_ids.insert(0, game_id)
        profile["recent_game_ids"] = recent_ids[:5]
        game_entry = self.ensure_game_entry(game_id)
        game_entry["last_played_at"] = _timestamp()
        self._touch_profile(profile)
        self.save()

    def record_game_session(self, game_id: str, payload: dict[str, Any]) -> None:
        game_entry = self.ensure_game_entry(game_id)
        game_entry["play_count"] += 1
        game_entry["last_played_at"] = _timestamp()
        score = payload.get("score")
        if isinstance(score, int):
            game_entry["last_score"] = score
            best_score = game_entry.get("best_score")
            if best_score is None or score > best_score:
                game_entry["best_score"] = score
        for key, field in (("round", "best_round"), ("wave", "best_wave"), ("lines", "best_lines"), ("hits", "best_hits")):
            value = payload.get(key)
            if isinstance(value, int):
                best = game_entry.get(field)
                if best is None or value > best:
                    game_entry[field] = value
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
        self._touch_profile(self.get_active_profile())
        self._evaluate_and_queue_achievements()
        self.save()

    def get_last_played_game_id(self) -> str | None:
        return self.get_active_profile().get("last_played_game_id")

    def get_recent_game_ids(self) -> list[str]:
        recent_games = self.get_active_profile().get("recent_game_ids", [])
        if isinstance(recent_games, list):
            return [game_id for game_id in recent_games if isinstance(game_id, str)]
        return []

    def get_game_stats(self, game_id: str) -> dict[str, Any]:
        games = self.get_active_profile().get("games", {})
        if isinstance(games, dict):
            return deepcopy(games.get(game_id, {}))
        return {}

    def get_all_game_stats(self) -> dict[str, dict[str, Any]]:
        games = self.get_active_profile().get("games", {})
        return deepcopy(games) if isinstance(games, dict) else {}

    def is_favorite(self, game_id: str) -> bool:
        favorites = self.get_active_profile().get("favorites", [])
        return isinstance(favorites, list) and game_id in favorites

    def toggle_favorite(self, game_id: str) -> bool:
        profile = self.get_active_profile()
        favorites = profile.setdefault("favorites", [])
        if game_id in favorites:
            favorites.remove(game_id)
            is_now_favorite = False
        else:
            favorites.append(game_id)
            favorites.sort()
            is_now_favorite = True
        self._touch_profile(profile)
        self._evaluate_and_queue_achievements()
        self.save()
        return is_now_favorite

    def toggle_favorite_game(self, game_id: str) -> bool:
        return self.toggle_favorite(game_id)

    def get_favorite_game_ids(self) -> list[str]:
        favorites = self.get_active_profile().get("favorites", [])
        if isinstance(favorites, list):
            return [game_id for game_id in favorites if isinstance(game_id, str)]
        return []

    def _get_unlocked_map(self, profile: dict[str, Any]) -> dict[str, str]:
        achievements = profile.get("achievements", {}) if isinstance(profile, dict) else {}
        unlocked = achievements.get("unlocked", {}) if isinstance(achievements, dict) else {}
        return unlocked if isinstance(unlocked, dict) else {}

    def get_profile_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        profiles = self.data.get("profiles", {})
        if not isinstance(profiles, dict):
            return {"id": "default", "name": DEFAULT_PROFILE_NAME, "total_sessions": 0, "unique_games": 0, "favorites_count": 0, "achievement_count": 0, "last_played_game_id": None}
        if profile_id is None:
            profile_id = self.get_active_profile_id()
        profile = profiles.get(profile_id, {})
        games = profile.get("games", {}) if isinstance(profile, dict) else {}
        if not isinstance(games, dict):
            games = {}
        total_sessions = 0
        unique_games = 0
        for stats in games.values():
            if not isinstance(stats, dict):
                continue
            unique_games += 1
            total_sessions += int(stats.get("play_count", 0))
        favorites = profile.get("favorites", []) if isinstance(profile, dict) else []
        if not isinstance(favorites, list):
            favorites = []
        achievement_count = len(self._get_unlocked_map(profile if isinstance(profile, dict) else {}))
        return {
            "id": profile_id,
            "name": str(profile.get("name", DEFAULT_PROFILE_NAME)) if isinstance(profile, dict) else DEFAULT_PROFILE_NAME,
            "total_sessions": total_sessions,
            "unique_games": unique_games,
            "favorites_count": len(favorites),
            "achievement_count": achievement_count,
            "last_played_game_id": profile.get("last_played_game_id") if isinstance(profile, dict) else None,
        }

    def submit_run_result(self, result: Any) -> None:
        if not hasattr(result, "game_id") or not hasattr(result, "to_dict"):
            raise ValueError("submit_run_result expects a RunResult-compatible object.")
        game_id = result.game_id
        leaderboards = self.data.setdefault("leaderboards", {})
        entries = leaderboards.setdefault(game_id, [])
        entry = result.to_dict()
        active_profile = self.get_active_profile()
        entry["profile_id"] = active_profile.get("id")
        entry["profile_name"] = active_profile.get("name")
        entry["created_at"] = _timestamp()
        entries.append(entry)
        def sort_key(item: dict[str, Any]) -> tuple[float, float]:
            score = item.get("score")
            duration_seconds = item.get("duration_seconds", item.get("duration"))
            score_value = float(score) if isinstance(score, (int, float)) else float("-inf")
            duration_value = float(duration_seconds) if isinstance(duration_seconds, (int, float)) else float("inf")
            return (score_value, -duration_value)
        entries.sort(key=sort_key, reverse=True)
        top_entries = entries[:10]
        for index, row in enumerate(top_entries, start=1):
            row["rank"] = index
        leaderboards[game_id] = top_entries
        self.save()

    def get_leaderboard(self, game_id: str) -> list[dict[str, Any]]:
        leaderboards = self.data.get("leaderboards", {})
        entries = leaderboards.get(game_id, []) if isinstance(leaderboards, dict) else []
        return deepcopy(entries) if isinstance(entries, list) else []

    def get_profile_leaderboard_entries(self, game_id: str, profile_id: str | None = None) -> list[dict[str, Any]]:
        entries = self.get_leaderboard(game_id)
        profile_id = profile_id or self.get_active_profile_id()
        return [deepcopy(entry) for entry in entries if isinstance(entry, dict) and entry.get("profile_id") == profile_id]

    def get_active_profile_leaderboard_entry(self, game_id: str) -> dict[str, Any] | None:
        entries = self.get_profile_leaderboard_entries(game_id, self.get_active_profile_id())
        if not entries:
            return None
        entries.sort(key=lambda item: (float(item.get("score")) if isinstance(item.get("score"), (int, float)) else float("-inf"), -(float(item.get("duration_seconds", item.get("duration"))) if isinstance(item.get("duration_seconds", item.get("duration")), (int, float)) else float("inf"))), reverse=True)
        return entries[0]

    def store_last_run_summary(self, summary: dict[str, Any]) -> None:
        if not isinstance(summary, dict):
            return
        game_id = summary.get("game_id")
        if not isinstance(game_id, str) or not game_id:
            return
        profile = self.get_active_profile()
        summaries = profile.setdefault("last_run_summaries", {})
        summaries[game_id] = deepcopy(summary)
        self._touch_profile(profile)
        self.save()

    def get_last_run_summary(self, game_id: str) -> dict[str, Any] | None:
        profile = self.get_active_profile()
        summaries = profile.get("last_run_summaries", {})
        if not isinstance(summaries, dict):
            return None
        summary = summaries.get(game_id)
        return deepcopy(summary) if isinstance(summary, dict) else None

    def clear_last_run_summary(self, game_id: str) -> None:
        profile = self.get_active_profile()
        summaries = profile.get("last_run_summaries", {})
        if isinstance(summaries, dict) and game_id in summaries:
            del summaries[game_id]
            self._touch_profile(profile)
            self.save()

    def record_daily_challenge_result(self, summary: dict[str, Any]) -> None:
        if not isinstance(summary, dict):
            return
        challenge_id = summary.get("challenge_id")
        if not isinstance(challenge_id, str) or not challenge_id:
            return
        profile = self.get_active_profile()
        daily = profile.setdefault("daily_challenges", {"history": {}})
        history = daily.setdefault("history", {})
        current = history.get(challenge_id, {"attempts": 0})
        score = summary.get("score")
        duration = summary.get("duration_seconds")
        attempts = int(current.get("attempts", 0)) + 1
        best_score = current.get("best_score")
        if isinstance(score, (int, float)):
            if best_score is None or score > best_score:
                best_score = score
        best_duration = current.get("best_duration_seconds")
        if isinstance(duration, (int, float)):
            if best_duration is None or duration < best_duration:
                best_duration = duration
        history[challenge_id] = {
            "challenge_id": challenge_id,
            "game_id": summary.get("game_id"),
            "title": summary.get("challenge_title") or summary.get("title"),
            "date": summary.get("challenge_date"),
            "seed": summary.get("seed"),
            "attempts": attempts,
            "best_score": best_score,
            "best_duration_seconds": best_duration,
            "last_score": score,
            "last_duration_seconds": duration,
            "last_played_at": _timestamp(),
        }
        self._touch_profile(profile)
        self.save()

    def get_daily_challenge_record(self, challenge_id: str) -> dict[str, Any] | None:
        profile = self.get_active_profile()
        daily = profile.get("daily_challenges", {})
        history = daily.get("history", {}) if isinstance(daily, dict) else {}
        record = history.get(challenge_id) if isinstance(history, dict) else None
        return deepcopy(record) if isinstance(record, dict) else None

    def get_daily_challenge_history(self, limit: int = 7) -> list[dict[str, Any]]:
        profile = self.get_active_profile()
        daily = profile.get("daily_challenges", {})
        history = daily.get("history", {}) if isinstance(daily, dict) else {}
        if not isinstance(history, dict):
            return []
        rows = [deepcopy(row) for row in history.values() if isinstance(row, dict)]
        rows.sort(key=lambda row: str(row.get("date", "")), reverse=True)
        return rows[:limit]

    def _evaluate_and_queue_achievements(self) -> None:
        profile = self.get_active_profile()
        newly_unlocked, _rows = evaluate_achievements(profile, _timestamp())
        achievements = profile.setdefault("achievements", deepcopy(_default_profile()["achievements"]))
        popup_queue = achievements.setdefault("popup_queue", [])
        recent_unlocks = achievements.setdefault("recent_unlocks", [])
        for achievement_id in newly_unlocked:
            if achievement_id not in recent_unlocks:
                recent_unlocks.insert(0, achievement_id)
            if achievement_id not in popup_queue:
                popup_queue.append(achievement_id)
        achievements["recent_unlocks"] = recent_unlocks[:20]
        achievements["popup_queue"] = popup_queue[:20]
        self._touch_profile(profile)

    def get_unlocked_achievement_ids(self, profile_id: str | None = None) -> list[str]:
        profile = self.get_active_profile() if profile_id is None else self.data.get("profiles", {}).get(profile_id, {})
        return list(self._get_unlocked_map(profile).keys())

    def unlock_achievement(self, achievement_id: str, payload: dict[str, Any] | None = None) -> bool:
        profile = self.get_active_profile()
        achievements = profile.setdefault("achievements", deepcopy(_default_profile()["achievements"]))
        unlocked = achievements.setdefault("unlocked", {})
        if achievement_id in unlocked:
            return False
        unlocked[achievement_id] = _timestamp()
        recent_unlocks = achievements.setdefault("recent_unlocks", [])
        popup_queue = achievements.setdefault("popup_queue", [])
        if achievement_id not in recent_unlocks:
            recent_unlocks.insert(0, achievement_id)
        if achievement_id not in popup_queue:
            popup_queue.append(achievement_id)
        achievements["recent_unlocks"] = recent_unlocks[:20]
        achievements["popup_queue"] = popup_queue[:20]
        self._touch_profile(profile)
        self.save()
        return True

    def get_recent_achievement_unlocks(self, limit: int = 10) -> list[dict[str, Any]]:
        profile = self.get_active_profile()
        achievements = profile.get("achievements", {})
        recent_ids = achievements.get("recent_unlocks", []) if isinstance(achievements, dict) else []
        if not isinstance(recent_ids, list):
            return []
        row_map = get_achievement_row_map(profile)
        return [deepcopy(row_map[achievement_id]) for achievement_id in recent_ids if achievement_id in row_map][:limit]

    def consume_pending_achievement_unlocks(self) -> list[dict[str, Any]]:
        profile = self.get_active_profile()
        achievements = profile.setdefault("achievements", deepcopy(_default_profile()["achievements"]))
        queue = achievements.get("popup_queue", [])
        if not isinstance(queue, list) or not queue:
            return []
        row_map = get_achievement_row_map(profile)
        pending = [deepcopy(row_map[achievement_id]) for achievement_id in queue if achievement_id in row_map]
        achievements["popup_queue"] = []
        self._touch_profile(profile)
        self.save()
        return pending

    def pop_achievement_popup(self) -> dict[str, Any] | None:
        pending = self.consume_pending_achievement_unlocks()
        return pending[0] if pending else None

    def get_pending_achievement_unlocks(self) -> list[dict[str, Any]]:
        profile = self.get_active_profile()
        achievements = profile.get("achievements", {})
        queue = achievements.get("popup_queue", []) if isinstance(achievements, dict) else []
        if not isinstance(queue, list):
            return []
        row_map = get_achievement_row_map(profile)
        return [deepcopy(row_map[achievement_id]) for achievement_id in queue if achievement_id in row_map]

    def queue_achievement_popup(self, popup_entry: dict[str, Any]) -> None:
        achievement_id = popup_entry.get("id") or popup_entry.get("achievement_id") if isinstance(popup_entry, dict) else None
        if not isinstance(achievement_id, str):
            return
        profile = self.get_active_profile()
        achievements = profile.setdefault("achievements", deepcopy(_default_profile()["achievements"]))
        queue = achievements.setdefault("popup_queue", [])
        if achievement_id not in queue:
            queue.append(achievement_id)
        achievements["popup_queue"] = queue[:20]
        self._touch_profile(profile)
        self.save()

    def get_achievement_progress(self) -> dict[str, Any]:
        profile = self.get_active_profile()
        achievements = profile.get("achievements", {})
        progress = achievements.get("progress", {}) if isinstance(achievements, dict) else {}
        return deepcopy(progress) if isinstance(progress, dict) else {}

    def set_achievement_progress(self, key: str, value: Any) -> None:
        profile = self.get_active_profile()
        achievements = profile.setdefault("achievements", deepcopy(_default_profile()["achievements"]))
        progress = achievements.setdefault("progress", {})
        progress[key] = value
        self._touch_profile(profile)
        self.save()

    def get_achievement_rows(self) -> list[dict[str, Any]]:
        return build_achievement_rows(self.get_active_profile())

    def get_game_achievement_rows(self, game_id: str) -> list[dict[str, Any]]:
        rows = self.get_achievement_rows()
        return [deepcopy(row) for row in rows if row.get("game_id") == game_id or str(row.get("id", "")).startswith(f"{game_id}_")]
