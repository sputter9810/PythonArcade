from __future__ import annotations

from copy import deepcopy
from typing import Any

from arcade_app.registry import GAME_REGISTRY


GLOBAL_ACHIEVEMENT_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "first_steps",
        "name": "First Steps",
        "description": "Finish your first arcade session.",
        "category": "Progression",
        "target": 1,
        "metric_label": "sessions",
        "kind": "total_sessions",
    },
    {
        "id": "regular_player",
        "name": "Regular Player",
        "description": "Finish 10 arcade sessions.",
        "category": "Progression",
        "target": 10,
        "metric_label": "sessions",
        "kind": "total_sessions",
    },
    {
        "id": "arcade_veteran",
        "name": "Arcade Veteran",
        "description": "Finish 25 arcade sessions.",
        "category": "Progression",
        "target": 25,
        "metric_label": "sessions",
        "kind": "total_sessions",
    },
    {
        "id": "explorer",
        "name": "Explorer",
        "description": "Play 5 different games.",
        "category": "Collection",
        "target": 5,
        "metric_label": "games",
        "kind": "unique_games",
    },
    {
        "id": "collector",
        "name": "Collector",
        "description": "Mark 3 games as favourites.",
        "category": "Collection",
        "target": 3,
        "metric_label": "favourites",
        "kind": "favorites",
    },
    {
        "id": "score_hunter",
        "name": "Score Hunter",
        "description": "Reach a score of 1,000 in any score-based game.",
        "category": "Skill",
        "target": 1000,
        "metric_label": "score",
        "kind": "best_score",
    },
    {
        "id": "sharpshooter",
        "name": "Sharpshooter",
        "description": "Record 90% accuracy or better in a tracked game.",
        "category": "Skill",
        "target": 90,
        "metric_label": "%",
        "kind": "best_accuracy",
    },
    {
        "id": "lightning_reflexes",
        "name": "Lightning Reflexes",
        "description": "Record a reaction time of 250 ms or faster.",
        "category": "Skill",
        "target": 250,
        "metric_label": "ms",
        "kind": "best_reaction_ms_lower",
    },
]


def get_achievement_definitions() -> list[dict[str, Any]]:
    return deepcopy(GLOBAL_ACHIEVEMENT_DEFINITIONS + _build_per_game_definitions())


def _build_per_game_definitions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for game in GAME_REGISTRY:
        if not game.get("implemented", False):
            continue

        game_id = str(game["id"])
        title = str(game["title"])

        rows.extend(
            [
                {
                    "id": f"{game_id}_rookie",
                    "name": f"{title} Rookie",
                    "description": f"Play {title} once.",
                    "category": f"Game: {title}",
                    "target": 1,
                    "metric_label": "sessions",
                    "kind": "per_game_play_count",
                    "game_id": game_id,
                },
                {
                    "id": f"{game_id}_regular",
                    "name": f"{title} Regular",
                    "description": f"Play {title} 5 times.",
                    "category": f"Game: {title}",
                    "target": 5,
                    "metric_label": "sessions",
                    "kind": "per_game_play_count",
                    "game_id": game_id,
                },
                {
                    "id": f"{game_id}_veteran",
                    "name": f"{title} Veteran",
                    "description": f"Play {title} 10 times.",
                    "category": f"Game: {title}",
                    "target": 10,
                    "metric_label": "sessions",
                    "kind": "per_game_play_count",
                    "game_id": game_id,
                },
            ]
        )
    return rows


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _best_metric(profile: dict[str, Any], metric_key: str, prefer_lower: bool = False) -> int | None:
    games = profile.get("games", {}) if isinstance(profile, dict) else {}
    if not isinstance(games, dict):
        return None

    values: list[int] = []
    for entry in games.values():
        if not isinstance(entry, dict):
            continue
        value = entry.get(metric_key)
        if isinstance(value, (int, float)):
            values.append(int(value))

    if not values:
        return None
    return min(values) if prefer_lower else max(values)


def _progress_for_definition(definition: dict[str, Any], profile: dict[str, Any]) -> int:
    games = profile.get("games", {}) if isinstance(profile, dict) else {}
    favorites = profile.get("favorites", []) if isinstance(profile, dict) else []
    kind = definition.get("kind")

    if kind == "total_sessions":
        if not isinstance(games, dict):
            return 0
        return sum(_safe_int(entry.get("play_count", 0)) for entry in games.values() if isinstance(entry, dict))

    if kind == "unique_games":
        if not isinstance(games, dict):
            return 0
        return len([entry for entry in games.values() if isinstance(entry, dict) and _safe_int(entry.get("play_count", 0)) > 0])

    if kind == "favorites":
        return len(favorites) if isinstance(favorites, list) else 0

    if kind == "best_score":
        return _best_metric(profile, "best_score") or 0

    if kind == "best_accuracy":
        return _best_metric(profile, "best_accuracy") or 0

    if kind == "best_reaction_ms_lower":
        best = _best_metric(profile, "best_reaction_ms", prefer_lower=True)
        return best if best is not None else 9999

    if kind == "per_game_play_count":
        game_id = definition.get("game_id")
        if isinstance(games, dict) and isinstance(game_id, str):
            entry = games.get(game_id, {})
            if isinstance(entry, dict):
                return _safe_int(entry.get("play_count", 0))
        return 0

    return 0


def _is_unlocked(definition: dict[str, Any], progress: int) -> bool:
    if definition.get("kind") == "best_reaction_ms_lower":
        return progress <= int(definition["target"])
    return progress >= int(definition["target"])


def _progress_text(progress: int, target: int, metric_label: str) -> str:
    if metric_label in {"%", "ms"}:
        return f"{progress}/{target}{metric_label}"
    return f"{progress}/{target} {metric_label}".strip()


def evaluate_achievements(profile: dict[str, Any], now_timestamp: str) -> tuple[list[str], list[dict[str, Any]]]:
    achievements = profile.setdefault("achievements", {"unlocked": {}, "recent_unlocks": []})
    unlocked = achievements.setdefault("unlocked", {})
    recent_unlocks = achievements.setdefault("recent_unlocks", [])

    definitions = get_achievement_definitions()
    newly_unlocked: list[str] = []
    rows: list[dict[str, Any]] = []

    for definition in definitions:
        progress = _progress_for_definition(definition, profile)
        target = int(definition["target"])
        achieved = definition["id"] in unlocked or _is_unlocked(definition, progress)

        if achieved and definition["id"] not in unlocked:
            unlocked[definition["id"]] = now_timestamp
            recent_unlocks.insert(0, definition["id"])
            newly_unlocked.append(definition["id"])

        rows.append(
            {
                **definition,
                "progress": progress,
                "unlocked": definition["id"] in unlocked,
                "unlocked_at": unlocked.get(definition["id"]),
                "progress_text": _progress_text(progress, target, str(definition.get("metric_label", ""))),
            }
        )

    achievements["recent_unlocks"] = recent_unlocks[:12]
    return newly_unlocked, rows


def build_achievement_rows(profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unlocked = profile.get("achievements", {}).get("unlocked", {}) if isinstance(profile, dict) else {}
    definitions = get_achievement_definitions()

    for definition in definitions:
        progress = _progress_for_definition(definition, profile)
        target = int(definition["target"])
        is_done = definition["id"] in unlocked or _is_unlocked(definition, progress)
        rows.append(
            {
                **definition,
                "progress": progress,
                "unlocked": is_done,
                "unlocked_at": unlocked.get(definition["id"]),
                "progress_text": _progress_text(progress, target, str(definition.get("metric_label", ""))),
            }
        )
    return rows


def get_achievement_row_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in build_achievement_rows(profile)}
