from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.core.scene_base import SceneBase


class SceneManager:
    def __init__(self, app) -> None:
        self.app = app
        self.current_scene: SceneBase | None = None

    def go_to(self, scene: SceneBase) -> None:
        if self.current_scene is not None:
            if isinstance(self.current_scene, GameBase):
                payload = self.current_scene.get_persistence_payload()
                self.app.save_data.record_game_session(
                    self.current_scene.game_id,
                    payload,
                )
            self.current_scene.exit()

        self.current_scene = scene
        self.current_scene.enter()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_events(events)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if self.current_scene is not None:
            self.current_scene.render(screen)