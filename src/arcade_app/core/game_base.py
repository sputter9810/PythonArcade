from __future__ import annotations

from arcade_app.core.scene_base import SceneBase


class GameBase(SceneBase):
    """Base class for playable game scenes.

    This class provides:
    - a shared scene type for all games
    - a stable place for persistence helpers
    - common metadata conventions
    """

    game_id: str = "base_game"
    title: str = "Base Game"

    def get_persistence_payload(self) -> dict:
        """Return session stats that should be persisted.

        Games can override this for custom data. If not overridden,
        this method attempts to gather common attributes automatically.
        """
        payload: dict = {}

        if hasattr(self, "score"):
            score = getattr(self, "score")
            if isinstance(score, int):
                payload["score"] = score

        if hasattr(self, "round_number"):
            round_number = getattr(self, "round_number")
            if isinstance(round_number, int):
                payload["round"] = round_number

        if hasattr(self, "wave"):
            wave = getattr(self, "wave")
            if isinstance(wave, int):
                payload["wave"] = wave

        if hasattr(self, "lines_cleared"):
            lines_cleared = getattr(self, "lines_cleared")
            if isinstance(lines_cleared, int):
                payload["lines"] = lines_cleared

        return payload