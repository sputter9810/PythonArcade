from __future__ import annotations

import time
from typing import Any

from arcade_app.core.run_result import RunResult
from arcade_app.core.scene_base import SceneBase


class GameBase(SceneBase):
    """Base class for playable game scenes."""

    game_id: str = "base_game"
    title: str = "Base Game"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.session_started_at = time.perf_counter()
        self.launch_context: dict[str, Any] = {}

    def enter(self) -> None:
        self.session_started_at = time.perf_counter()

    def get_persistence_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}

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

        if hasattr(self, "difficulty"):
            difficulty = getattr(self, "difficulty")
            if isinstance(difficulty, str) and difficulty.strip():
                payload["difficulty"] = difficulty.strip()

        launch_context = getattr(self, "launch_context", {})
        if isinstance(launch_context, dict):
            if launch_context.get("challenge_id"):
                payload["challenge_id"] = launch_context["challenge_id"]
                payload["challenge_mode"] = launch_context.get("challenge_mode", "daily")
                payload["challenge_title"] = launch_context.get("challenge_title")
                payload["challenge_date"] = launch_context.get("challenge_date")
            if launch_context.get("seed") is not None:
                payload["seed"] = launch_context.get("seed")
                payload["seeded_run"] = True

        return payload

    def build_run_result(self) -> RunResult:
        payload = self.get_persistence_payload()
        score = payload.get("score") if isinstance(payload.get("score"), int) else None
        metadata = dict(payload)
        metadata.pop("score", None)
        duration_seconds = round(max(0.0, time.perf_counter() - self.session_started_at), 2)
        return RunResult(
            game_id=self.game_id,
            score=score,
            duration_seconds=duration_seconds,
            metadata=metadata,
        )

    def should_show_run_summary(self) -> bool:
        payload = self.get_persistence_payload()
        if payload:
            return True
        duration_seconds = max(0.0, time.perf_counter() - self.session_started_at)
        return duration_seconds >= 8.0
