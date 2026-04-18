from __future__ import annotations

import json

from arcade_app.core.save_data import SaveDataManager


def test_save_data_migrates_v1_shape(tmp_path) -> None:
    save_dir = tmp_path / "PythonArcade"
    save_dir.mkdir(parents=True)

    legacy_data = {
        "app": {
            "last_played_game_id": "snake",
            "recent_game_ids": ["snake"],
            "settings": {
                "fullscreen": True,
                "sound_enabled": False,
                "music_enabled": True,
            },
        },
        "games": {
            "snake": {
                "play_count": 2,
                "best_score": 14,
            }
        },
    }

    save_file = save_dir / "save_data.json"
    save_file.write_text(json.dumps(legacy_data), encoding="utf-8")

    manager = SaveDataManager(app_name="PythonArcade")
    manager.save_dir = save_dir
    manager.save_file = save_file
    manager.load()

    assert manager.data["schema_version"] == 2
    assert manager.get_launcher_preferences()["sort_mode"] == "title"
    assert manager.get_profile_data()["display_name"] == "Player One"
    assert manager.get_game_stats("snake")["best_score"] == 14


def test_favorites_and_profile_summary(tmp_path) -> None:
    manager = SaveDataManager(app_name="PythonArcadeTest")
    manager.save_dir = tmp_path / "PythonArcadeTest"
    manager.save_dir.mkdir(parents=True, exist_ok=True)
    manager.save_file = manager.save_dir / "save_data.json"
    manager.data = {
        "schema_version": 2,
        "app": {
            "last_played_game_id": None,
            "recent_game_ids": [],
            "updated_at": None,
            "settings": {
                "fullscreen": False,
                "sound_enabled": True,
                "music_enabled": True,
            },
            "launcher": {
                "sort_mode": "title",
                "category_filter": "All",
                "favorites_only": False,
                "search_query": "",
            },
        },
        "profile": {
            "display_name": "Player One",
            "first_played_at": None,
            "last_played_at": None,
            "total_sessions_played": 0,
            "total_score_accumulated": 0,
            "favorite_game_ids": [],
        },
        "games": {},
    }

    manager.toggle_favorite_game("snake")
    manager.record_game_session("snake", {"score": 12})
    summary = manager.get_profile_summary([{"id": "snake", "title": "Snake"}])

    assert manager.is_favorite("snake") is True
    assert summary["total_sessions_played"] == 1
    assert summary["total_games_played"] == 1
    assert summary["top_played_game_title"] == "Snake"
