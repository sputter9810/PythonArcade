from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class WhacAMoleGame(GameBase):
    game_id = "whac_a_mole"
    title = "Whac-A-Mole"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.mole_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 720, 540)
        self.holes: list[pygame.Rect] = []

        self.score = 0
        self.time_left = 30.0
        self.is_game_over = False

        self.active_hole_index: int | None = None
        self.mole_timer = 0.0
        self.mole_interval = 0.75

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.mole_font = pygame.font.SysFont("arial", 34, bold=True)
        self.reset_game()

    def reset_game(self) -> None:
        self.score = 0
        self.time_left = 30.0
        self.is_game_over = False
        self.active_hole_index = None
        self.mole_timer = 0.0

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - 720) // 2,
            170,
            720,
            540,
        )

        self.holes = []
        rows = 3
        cols = 3
        hole_w = 150
        hole_h = 95
        gap_x = 60
        gap_y = 55

        total_w = cols * hole_w + (cols - 1) * gap_x
        total_h = rows * hole_h + (rows - 1) * gap_y

        start_x = self.board_rect.centerx - total_w // 2
        start_y = self.board_rect.centery - total_h // 2

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (hole_w + gap_x)
                y = start_y + row * (hole_h + gap_y)
                self.holes.append(pygame.Rect(x, y, hole_w, hole_h))

    def choose_new_hole(self) -> None:
        if self.holes:
            self.active_hole_index = random.randint(0, len(self.holes) - 1)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_game_over or self.active_hole_index is None:
                    continue

                if self.holes[self.active_hole_index].collidepoint(event.pos):
                    self.score += 1
                    self.active_hole_index = None
                    self.mole_timer = 0.0

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.is_game_over:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.is_game_over = True
            return

        self.mole_timer += dt
        if self.mole_timer >= self.mole_interval:
            self.mole_timer = 0.0
            self.choose_new_hole()

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.mole_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Whac-A-Mole", True, theme.TEXT)
        status_text = "Time's up!" if self.is_game_over else "Click the mole as fast as you can"
        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        timer = self.info_font.render(f"Time: {self.time_left:0.1f}s", True, theme.TEXT)
        controls = self.info_font.render(
            "Mouse: Click mole  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 120, 115)))
        screen.blit(timer, timer.get_rect(center=(screen.get_width() // 2 + 120, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        for i, hole in enumerate(self.holes):
            pygame.draw.ellipse(screen, theme.SURFACE_ALT, hole)

            if i == self.active_hole_index and not self.is_game_over:
                mole_rect = hole.inflate(-40, -20)
                pygame.draw.ellipse(screen, theme.WARNING, mole_rect)
                face = self.mole_font.render("M", True, theme.TEXT)
                screen.blit(face, face.get_rect(center=mole_rect.center))