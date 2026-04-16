from arcade_app.registry import GAME_REGISTRY


def test_registry_has_32_games() -> None:
    assert len(GAME_REGISTRY) == 32


def test_registry_ids_unique() -> None:
    ids = [game["id"] for game in GAME_REGISTRY]
    assert len(ids) == len(set(ids))


def test_registry_titles_sorted_alphabetically() -> None:
    titles = [game["title"] for game in GAME_REGISTRY]
    assert titles == sorted(titles, key=str.lower)