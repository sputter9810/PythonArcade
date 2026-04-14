from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from arcade_app.app import ArcadeApp


class SceneBase(ABC):
    def __init__(self, app: "ArcadeApp") -> None:
        self.app = app

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, dt: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        raise NotImplementedError
