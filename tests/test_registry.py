from arcade_app.registry import GAME_REGISTRY, get_game_categories


def test_registry_has_32_games() -> None:
    assert len(GAME_REGISTRY) == 32


def test_registry_ids_unique() -> None:
    ids = [game["id"] for game in GAME_REGISTRY]
    assert len(ids) == len(set(ids))


def test_registry_titles_sorted_alphabetically() -> None:
    titles = [game["title"] for game in GAME_REGISTRY]
    assert titles == sorted(titles, key=str.lower)


def test_registry_entries_include_stage_1_metadata() -> None:
    for game in GAME_REGISTRY:
        assert isinstance(game.get("tags"), list)
        assert len(game["tags"]) >= 2
        assert isinstance(game.get("search_terms"), list)
        assert game.get("status_label") in {"Ready to Play", "Coming Soon"}
        assert isinstance(game.get("detail_bullets"), list)
        assert len(game["detail_bullets"]) >= 3


def test_registry_categories_include_all_filter() -> None:
    categories = get_game_categories()
    assert categories[0] == "All"
    assert "Arcade" in categories
