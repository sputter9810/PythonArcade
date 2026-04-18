from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.platform.challenges import build_daily_challenge, build_launch_context
from arcade_app.registry import create_game_scene
from arcade_app.ui import theme


class DailyChallengeScene(SceneBase):
    def __init__(self, app, preferred_game_id: str | None = None, return_scene: str = "menu") -> None:
        super().__init__(app)
        self.preferred_game_id = preferred_game_id
        self.return_scene = return_scene
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 42, bold=True)
        self.body_font = pygame.font.SysFont("arial", 24)
        self.meta_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 16)

    def challenge(self):
        return build_daily_challenge(preferred_game_id=self.preferred_game_id)

    def launch(self) -> None:
        challenge = self.challenge()
        if not challenge:
            return
        scene = create_game_scene(challenge["game_id"], self.app, launch_context=build_launch_context(challenge))
        self.app.save_data.set_last_played(challenge["game_id"])
        self.app.scene_manager.go_to(scene)

    def go_back(self) -> None:
        if self.return_scene == "library":
            from arcade_app.scenes.game_select_scene import GameSelectScene
            self.app.scene_manager.go_to(GameSelectScene(self.app, initial_game_id=self.preferred_game_id))
        else:
            from arcade_app.scenes.main_menu_scene import MainMenuScene
            self.app.scene_manager.go_to(MainMenuScene(self.app))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go_back()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_c):
                self.launch()

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None
        assert self.small_font is not None

        screen.fill(theme.BACKGROUND)
        challenge = self.challenge()
        panel = pygame.Rect(180, 120, screen.get_width() - 360, screen.get_height() - 240)
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel, width=2, border_radius=theme.RADIUS_LARGE)

        title = self.title_font.render("Daily Challenge", True, theme.TEXT)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, panel.y + 46)))

        if not challenge:
            empty = self.body_font.render("No seeded daily challenge is available right now.", True, theme.MUTED_TEXT)
            screen.blit(empty, empty.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
            return

        record = self.app.save_data.get_daily_challenge_record(challenge["id"])
        y = panel.y + 110
        rows = [
            challenge["title"],
            challenge["description"],
            f"Game: {challenge['game_title']}  |  Seed: {challenge['seed']}",
            f"Date: {challenge['date']}  |  Mode: Seeded Daily Run",
        ]
        for index, row in enumerate(rows):
            font = self.body_font if index < 2 else self.meta_font
            color = theme.ACCENT if index == 0 else theme.MUTED_TEXT if index > 0 else theme.TEXT
            surface = font.render(row, True, color if index > 0 else theme.TEXT)
            screen.blit(surface, surface.get_rect(topleft=(panel.x + 28, y)))
            y += 40 if index == 0 else 30

        y += 18
        history_title = self.body_font.render("Your Daily Progress", True, theme.TEXT)
        screen.blit(history_title, history_title.get_rect(topleft=(panel.x + 28, y)))
        y += 42

        if record:
            best_score = record.get("best_score")
            best_duration = record.get("best_duration_seconds")
            attempts = record.get("attempts", 0)
            lines = [f"Attempts Today: {attempts}"]
            if best_score is not None:
                lines.append(f"Best Score: {best_score}")
            if best_duration is not None:
                lines.append(f"Best Duration: {float(best_duration):.2f}s")
            for row in lines:
                surface = self.meta_font.render(row, True, theme.WARNING)
                screen.blit(surface, surface.get_rect(topleft=(panel.x + 28, y)))
                y += 28
        else:
            empty = self.meta_font.render("No attempt recorded for this challenge yet.", True, theme.MUTED_TEXT)
            screen.blit(empty, empty.get_rect(topleft=(panel.x + 28, y)))
            y += 28

        footer = self.small_font.render("Enter / Space / C: Launch daily challenge  |  Esc: Back", True, theme.MUTED_TEXT)
        screen.blit(footer, footer.get_rect(center=(screen.get_width() // 2, panel.bottom - 32)))
