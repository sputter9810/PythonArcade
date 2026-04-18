from __future__ import annotations

from typing import Any

SORT_MODES = ("title", "most_played", "recently_played", "favorites_first")


def _normalise_text(value: Any) -> str:
    return str(value or "").strip().lower()


def build_search_text(game: dict[str, Any]) -> str:
    fields: list[str] = [
        str(game.get("title", "")),
        str(game.get("description", "")),
        str(game.get("category", "")),
    ]
    fields.extend(str(mode) for mode in game.get("modes", []))
    fields.extend(str(tag) for tag in game.get("tags", []))
    fields.extend(str(tag) for tag in game.get("search_terms", []))
    return " ".join(fields).lower()


def filter_and_sort_games(
    games: list[dict[str, Any]],
    save_data,
    *,
    search_query: str = "",
    category_filter: str = "All",
    favorites_only: bool = False,
    sort_mode: str = "title",
) -> list[dict[str, Any]]:
    favorite_ids = set(save_data.get_favorite_game_ids())
    lowered_query = _normalise_text(search_query)
    lowered_category = _normalise_text(category_filter)

    filtered: list[dict[str, Any]] = []
    for game in games:
        if lowered_category not in ("", "all") and _normalise_text(game.get("category")) != lowered_category:
            continue

        if favorites_only and game.get("id") not in favorite_ids:
            continue

        if lowered_query and lowered_query not in build_search_text(game):
            continue

        filtered.append(game)

    game_stats = save_data.get_all_game_stats()

    def stat_value(game_id: str, key: str, fallback: Any) -> Any:
        stats = game_stats.get(game_id, {})
        if isinstance(stats, dict):
            value = stats.get(key)
            if value is not None:
                return value
        return fallback

    if sort_mode == "most_played":
        return sorted(
            filtered,
            key=lambda game: (
                -int(stat_value(game["id"], "play_count", 0)),
                str(game.get("title", "")).lower(),
            ),
        )

    if sort_mode == "recently_played":
        return sorted(
            filtered,
            key=lambda game: (
                str(stat_value(game["id"], "last_played_at", "")),
                str(game.get("title", "")).lower(),
            ),
            reverse=True,
        )

    if sort_mode == "favorites_first":
        return sorted(
            filtered,
            key=lambda game: (
                0 if game.get("id") in favorite_ids else 1,
                str(game.get("title", "")).lower(),
            ),
        )

    return sorted(filtered, key=lambda game: str(game.get("title", "")).lower())


def build_profile_snapshot(save_data, registry: list[dict[str, Any]]) -> dict[str, Any]:
    summary = save_data.get_profile_summary(registry)
    top_game = summary.get("top_played_game_title") or "None yet"
    top_count = summary.get("top_play_count", 0)

    return {
        "headline": f"{summary.get('display_name', 'Player One')} Profile",
        "rows": [
            f"Sessions played: {summary.get('total_sessions_played', 0)}",
            f"Unique games played: {summary.get('total_games_played', 0)}",
            f"Favorites: {summary.get('total_favorites', 0)}",
            f"Top played: {top_game}" + (f" ({top_count})" if top_count else ""),
        ],
    }


def format_last_played_label(last_played_at: Any) -> str:
    if not isinstance(last_played_at, str) or not last_played_at:
        return "Never played"

    label = last_played_at.replace("T", " ").split(".")[0]
    return f"Last played: {label} UTC"


def format_metric_rows(stats: dict[str, Any]) -> list[str]:
    rows: list[str] = []

    play_count = stats.get("play_count")
    rows.append(f"Play count: {play_count}" if isinstance(play_count, int) else "Play count: 0")

    mappings = [
        ("best_score", "Best score"),
        ("last_score", "Last score"),
        ("best_round", "Best round"),
        ("best_wave", "Best wave"),
        ("best_lines", "Best lines"),
        ("best_hits", "Best hits"),
        ("best_accuracy", "Best accuracy"),
        ("best_reaction_ms", "Best reaction"),
    ]

    for key, label in mappings:
        value = stats.get(key)
        if value is None:
            continue
        if key == "best_accuracy":
            rows.append(f"{label}: {float(value):.1f}%")
        elif key == "best_reaction_ms":
            rows.append(f"{label}: {value} ms")
        else:
            rows.append(f"{label}: {value}")

    rows.append(format_last_played_label(stats.get("last_played_at")))
    return rows


def format_stats_inline(stats: dict[str, Any]) -> str:
    parts: list[str] = []

    mappings = [
        ("play_count", "Plays"),
        ("best_score", "Best Score"),
        ("best_round", "Best Round"),
        ("best_wave", "Best Wave"),
        ("best_lines", "Best Lines"),
        ("best_hits", "Best Hits"),
    ]

    for key, label in mappings:
        value = stats.get(key)
        if isinstance(value, int):
            parts.append(f"{label}: {value}")

    accuracy = stats.get("best_accuracy")
    if isinstance(accuracy, (int, float)):
        parts.append(f"Best Accuracy: {float(accuracy):.1f}%")

    reaction = stats.get("best_reaction_ms")
    if isinstance(reaction, int):
        parts.append(f"Best RT: {reaction} ms")

    return "  |  ".join(parts) if parts else "No saved stats yet"
