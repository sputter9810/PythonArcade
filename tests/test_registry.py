from arcade_app.registry import GAME_REGISTRY


def test_registry_has_16_games() -> None:
    assert len(GAME_REGISTRY) == 16


def test_registry_ids_unique() -> None:
    ids = [game["id"] for game in GAME_REGISTRY]
    assert len(ids) == len(set(ids))
