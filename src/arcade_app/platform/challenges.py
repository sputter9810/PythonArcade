from __future__ import annotations

import hashlib
from datetime import date, datetime
from typing import Any

from arcade_app.registry import GAME_REGISTRY, get_game_by_id

SUPPORTED_DAILY_CHALLENGE_GAMES = {
    "advanced_target_trainer",
    "aim_trainer",
    "asteroids",
    "breakout",
    "bullet_hell_lite",
    "dodge_falling_blocks",
    "maze",
    "memory_match",
    "minesweeper",
    "reaction_timer",
    "snake",
    "space_invaders",
    "sudoku",
    "tetris",
    "time_attack_challenge",
    "top_down_shooter",
    "whac_a_mole",
    "zombie_survival",
}


def _normalise_date(value: date | datetime | str | None = None) -> date:
    if value is None:
        return datetime.now().date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    return datetime.now().date()


def get_daily_challenge_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for game in GAME_REGISTRY:
        if not game.get("implemented", False):
            continue
        if game["id"] not in SUPPORTED_DAILY_CHALLENGE_GAMES:
            continue
        candidates.append(game)
    return sorted(candidates, key=lambda game: str(game["title"]).lower())


def _seed_for(game_id: str, date_key: str) -> int:
    digest = hashlib.sha256(f"{date_key}:{game_id}:arcade-daily".encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _descriptor_for(game: dict[str, Any]) -> str:
    category = str(game.get("category", "")).lower()
    if category == "puzzle":
        return "Solve the seeded board as cleanly as you can."
    if category in {"arcade", "action"}:
        return "Chase a higher score on today's seeded run."
    if category == "skill":
        return "Test consistency against today's seeded challenge."
    return "Take on today's featured seeded run."


def build_daily_challenge(value: date | datetime | str | None = None, preferred_game_id: str | None = None) -> dict[str, Any] | None:
    challenge_date = _normalise_date(value)
    date_key = challenge_date.isoformat()

    if preferred_game_id:
        game = get_game_by_id(preferred_game_id)
        if game is None or game["id"] not in SUPPORTED_DAILY_CHALLENGE_GAMES or not game.get("implemented", False):
            return None
    else:
        candidates = get_daily_challenge_candidates()
        if not candidates:
            return None
        index = challenge_date.toordinal() % len(candidates)
        game = candidates[index]

    seed = _seed_for(game["id"], date_key)
    challenge_id = f"daily:{date_key}:{game['id']}"
    return {
        "id": challenge_id,
        "mode": "daily",
        "date": date_key,
        "game_id": game["id"],
        "game_title": game["title"],
        "seed": seed,
        "title": f"Daily Challenge — {game['title']}",
        "description": _descriptor_for(game),
        "status_label": game.get("status_label", "Ready to Play"),
        "tags": game.get("tags", []),
    }


def build_launch_context(challenge: dict[str, Any]) -> dict[str, Any]:
    return {
        "challenge_id": challenge["id"],
        "challenge_mode": challenge.get("mode", "daily"),
        "challenge_title": challenge.get("title", "Daily Challenge"),
        "challenge_date": challenge.get("date"),
        "seed": challenge.get("seed"),
        "seeded_run": True,
    }
