from __future__ import annotations

from typing import Any


class RunResult:
    """Standardised run summary for Stage 2A systems.

    Compatible with both:
    - duration
    - duration_seconds

    so older and newer callers can coexist safely.
    """

    def __init__(
        self,
        game_id: str,
        score: int | float | None = None,
        duration: float | None = None,
        duration_seconds: float | None = None,
        metadata: dict[str, Any] | None = None,
        **extra: Any,
    ) -> None:
        self.game_id = game_id
        self.score = score

        # Support either field name.
        if duration_seconds is not None:
            self.duration_seconds = float(duration_seconds)
        elif duration is not None:
            self.duration_seconds = float(duration)
        else:
            self.duration_seconds = None

        self.metadata: dict[str, Any] = metadata.copy() if isinstance(metadata, dict) else {}

        # Preserve any extra fields without breaking callers.
        for key, value in extra.items():
            setattr(self, key, value)

    @property
    def duration(self) -> float | None:
        return self.duration_seconds

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "game_id": self.game_id,
            "score": self.score,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }

        # Include any extra dynamic fields that were attached.
        standard_keys = {"game_id", "score", "duration_seconds", "metadata"}
        for key, value in self.__dict__.items():
            if key not in standard_keys:
                payload[key] = value

        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunResult":
        if not isinstance(data, dict):
            raise ValueError("RunResult.from_dict expects a dictionary.")

        copied = dict(data)
        game_id = copied.pop("game_id")
        score = copied.pop("score", None)
        duration_seconds = copied.pop("duration_seconds", copied.pop("duration", None))
        metadata = copied.pop("metadata", {})

        return cls(
            game_id=game_id,
            score=score,
            duration_seconds=duration_seconds,
            metadata=metadata,
            **copied,
        )