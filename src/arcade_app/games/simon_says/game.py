from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class SimonSaysGame(GameBase):
    game_id = "simon_says"
    title = "Simon Says"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 520, 520)
        self.pad_rects: list[pygame.Rect] = []

        self.base_colors = [
            (180, 70, 70),   # red
            (80, 170, 90),   # green
            (80, 120, 210),  # blue
            (220, 190, 80),  # yellow
        ]
        self.bright_colors = [
            (240, 120, 120),
            (130, 230, 140),
            (130, 170, 255),
            (255, 235, 130),
        ]

        self.sequence: list[int] = []
        self.player_index = 0
        self.round_number = 0

        self.playback_index = 0
        self.playback_timer = 0.0
        self.playback_on_duration = 0.45
        self.playback_off_duration = 0.20
        self.active_pad: int | None = None
        self.playback_showing = False

        self.player_flash_timer = 0.0
        self.player_flash_duration = 0.18

        self.state = "idle"  # idle, playback, input, success, game_over
        self.state_timer = 0.0

        self.score = 0

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)
        self.reset_game()

    def reset_game(self) -> None:
        self.sequence = []
        self.player_index = 0
        self.round_number = 0
        self.playback_index = 0
        self.playback_timer = 0.0
        self.active_pad = None
        self.playback_showing = False
        self.player_flash_timer = 0.0
        self.state_timer = 0.0
        self.score = 0
        self.start_next_round()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - 520) // 2,
            180,
            520,
            520,
        )

        gap = 18
        pad_size = (self.board_rect.width - gap) // 2

        x = self.board_rect.x
        y = self.board_rect.y

        self.pad_rects = [
            pygame.Rect(x, y, pad_size, pad_size),
            pygame.Rect(x + pad_size + gap, y, pad_size, pad_size),
            pygame.Rect(x, y + pad_size + gap, pad_size, pad_size),
            pygame.Rect(x + pad_size + gap, y + pad_size + gap, pad_size, pad_size),
        ]

    def start_next_round(self) -> None:
        self.sequence.append(random.randint(0, 3))
        self.round_number += 1
        self.player_index = 0
        self.playback_index = 0
        self.playback_timer = 0.0
        self.active_pad = None
        self.playback_showing = False
        self.state = "playback"

    def get_status_text(self) -> str:
        if self.state == "playback":
            return "Watch the sequence"
        if self.state == "input":
            return "Repeat the sequence"
        if self.state == "success":
            return "Correct!"
        if self.state == "game_over":
            return "Wrong pad - Game Over"
        return "Get ready"

    def handle_player_choice(self, pad_index: int) -> None:
        if self.state != "input":
            return

        self.active_pad = pad_index
        self.player_flash_timer = self.player_flash_duration

        expected = self.sequence[self.player_index]
        if pad_index != expected:
            self.state = "game_over"
            self.active_pad = pad_index
            return

        self.player_index += 1
        self.score += 10

        if self.player_index >= len(self.sequence):
            self.state = "success"
            self.state_timer = 0.6

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_1:
                    self.handle_player_choice(0)
                elif event.key == pygame.K_2:
                    self.handle_player_choice(1)
                elif event.key == pygame.K_3:
                    self.handle_player_choice(2)
                elif event.key == pygame.K_4:
                    self.handle_player_choice(3)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state != "input":
                    continue

                for i, rect in enumerate(self.pad_rects):
                    if rect.collidepoint(event.pos):
                        self.handle_player_choice(i)
                        break

    def update_playback(self, dt: float) -> None:
        if self.playback_index >= len(self.sequence):
            self.state = "input"
            self.active_pad = None
            self.playback_showing = False
            self.player_index = 0
            return

        self.playback_timer += dt

        if not self.playback_showing:
            if self.playback_timer >= self.playback_off_duration:
                self.playback_timer = 0.0
                self.playback_showing = True
                self.active_pad = self.sequence[self.playback_index]
        else:
            if self.playback_timer >= self.playback_on_duration:
                self.playback_timer = 0.0
                self.playback_showing = False
                self.active_pad = None
                self.playback_index += 1

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.player_flash_timer > 0:
            self.player_flash_timer -= dt
            if self.player_flash_timer <= 0 and self.state == "input":
                self.active_pad = None

        if self.state == "playback":
            self.update_playback(dt)
        elif self.state == "success":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.start_next_round()

    def draw_pad(self, screen: pygame.Surface, rect: pygame.Rect, index: int) -> None:
        is_active = self.active_pad == index
        color = self.bright_colors[index] if is_active else self.base_colors[index]

        pygame.draw.rect(screen, color, rect, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE, rect, width=4, border_radius=theme.RADIUS_LARGE)

        assert self.small_font is not None
        label = self.small_font.render(str(index + 1), True, theme.TEXT)
        screen.blit(label, label.get_rect(center=rect.center))

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Simon Says", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        round_text = self.info_font.render(f"Round: {self.round_number}", True, theme.TEXT)
        score_text = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        controls = self.info_font.render(
            "Mouse or Keys 1-4  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(round_text, round_text.get_rect(center=(screen.get_width() // 2 - 110, 115)))
        screen.blit(score_text, score_text.get_rect(center=(screen.get_width() // 2 + 110, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_LARGE)

        for i, rect in enumerate(self.pad_rects):
            self.draw_pad(screen, rect, i)