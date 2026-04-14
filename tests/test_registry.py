from arcade_app.registry import GAME_REGISTRY


def test_registry_has_21_games() -> None:
    assert len(GAME_REGISTRY) == 21


def test_registry_ids_unique() -> None:
    ids = [game["id"] for game in GAME_REGISTRY]
    assert len(ids) == len(set(ids))