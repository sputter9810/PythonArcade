from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class SimonSaysGame(GameBase):
    game_id = "simon_says"
    title = "Simon Says"

    COLORS = [
        {"name": "Green", "base": (80, 170, 100), "bright": (130, 230, 150)},
        {"name": "Red", "base": (190, 80, 80), "bright": (250, 130, 130)},
        {"name": "Blue", "base": (80, 120, 200), "bright": (140, 180, 255)},
        {"name": "Yellow", "base": (200, 180, 70), "bright": (255, 235, 120)},
    ]

    STATE_BUFFER = "buffer"
    STATE_SHOW_ON = "show_on"
    STATE_SHOW_OFF = "show_off"
    STATE_INPUT = "input"
    STATE_OVER = "over"

    ROUND_START_BUFFER = 0.75
    FLASH_ON_TIME = 0.55
    FLASH_OFF_TIME = 0.22
    INPUT_FLASH_TIME = 0.18

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.label_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 920, 620)
        self.buttons: list[pygame.Rect] = []

        self.sequence: list[int] = []
        self.input_index = 0
        self.round_reached = 0

        self.state = self.STATE_BUFFER
        self.state_timer = 0.0
        self.show_index = 0
        self.flash_button: int | None = None
        self.status_text = "Get ready..."

        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.label_font = pygame.font.SysFont("arial", 24, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 920) // 2, 165, 920, 620)
        panel_size = 210
        gap = 24
        total = panel_size * 2 + gap
        start_x = self.play_rect.centerx - total // 2
        start_y = self.play_rect.centery - total // 2 + 30

        self.buttons = [
            pygame.Rect(start_x, start_y, panel_size, panel_size),
            pygame.Rect(start_x + panel_size + gap, start_y, panel_size, panel_size),
            pygame.Rect(start_x, start_y + panel_size + gap, panel_size, panel_size),
            pygame.Rect(start_x + panel_size + gap, start_y + panel_size + gap, panel_size, panel_size),
        ]

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.sequence = [random.randint(0, 3)]
        self.input_index = 0
        self.round_reached = 1

        self.state = self.STATE_BUFFER
        self.state_timer = self.ROUND_START_BUFFER
        self.show_index = 0
        self.flash_button = None
        self.status_text = "Get ready..."

        self.paused = False

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["round"] = self.round_reached
        payload["score"] = self.round_reached * 100
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def begin_demo_buffer(self, message: str = "Watch the pattern...") -> None:
        self.state = self.STATE_BUFFER
        self.state_timer = self.ROUND_START_BUFFER
        self.show_index = 0
        self.flash_button = None
        self.status_text = message

    def begin_next_round(self) -> None:
        self.sequence.append(random.randint(0, 3))
        self.round_reached = len(self.sequence)
        self.input_index = 0
        self.begin_demo_buffer("Next round...")

    def start_demo(self) -> None:
        self.state = self.STATE_SHOW_ON
        self.show_index = 0
        self.flash_button = self.sequence[self.show_index]
        self.state_timer = self.FLASH_ON_TIME
        self.status_text = "Watch closely..."

    def press_button(self, index: int) -> None:
        if self.paused or self.state != self.STATE_INPUT:
            return

        self.flash_button = index
        self.state_timer = self.INPUT_FLASH_TIME

        expected = self.sequence[self.input_index]
        if index != expected:
            self.state = self.STATE_OVER
            self.status_text = "Wrong input."
            return

        self.input_index += 1
        if self.input_index >= len(self.sequence):
            self.begin_next_round()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        key_map = {
            pygame.K_q: 0,
            pygame.K_w: 1,
            pygame.K_a: 2,
            pygame.K_s: 3,
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
        }

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and self.state != self.STATE_OVER:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.state == self.STATE_OVER and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif event.key in key_map:
                    self.press_button(key_map[event.key])

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == self.STATE_OVER:
                    self.reset_game()
                    continue
                if self.paused:
                    continue
                for i, rect in enumerate(self.buttons):
                    if rect.collidepoint(event.pos):
                        self.press_button(i)
                        break

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.state == self.STATE_OVER:
            return

        if self.state_timer > 0:
            self.state_timer -= dt

        if self.state == self.STATE_BUFFER:
            if self.state_timer <= 0:
                self.start_demo()

        elif self.state == self.STATE_SHOW_ON:
            if self.state_timer <= 0:
                self.flash_button = None
                self.state = self.STATE_SHOW_OFF
                self.state_timer = self.FLASH_OFF_TIME

        elif self.state == self.STATE_SHOW_OFF:
            if self.state_timer <= 0:
                self.show_index += 1
                if self.show_index >= len(self.sequence):
                    self.state = self.STATE_INPUT
                    self.input_index = 0
                    self.flash_button = None
                    self.status_text = "Your turn."
                else:
                    self.flash_button = self.sequence[self.show_index]
                    self.state = self.STATE_SHOW_ON
                    self.state_timer = self.FLASH_ON_TIME

        elif self.state == self.STATE_INPUT:
            if self.flash_button is not None and self.state_timer <= 0:
                self.flash_button = None

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.label_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Simon Says",
            "Repeat the pattern. Use Q/W/A/S, 1-4, or click the panels.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Round: {self.round_reached}",
                f"Progress: {self.input_index}/{len(self.sequence) if self.state == self.STATE_INPUT else len(self.sequence)}",
            ],
        )

        if self.state == self.STATE_BUFFER:
            sub = self.status_text
        elif self.state in (self.STATE_SHOW_ON, self.STATE_SHOW_OFF):
            sub = "Watch the demonstration carefully."
        elif self.state == self.STATE_INPUT:
            sub = "Repeat the full sequence in order."
        else:
            sub = "Sequence broken."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for i, rect in enumerate(self.buttons):
            color = self.COLORS[i]["bright"] if self.flash_button == i else self.COLORS[i]["base"]
            pygame.draw.rect(screen, color, rect, border_radius=18)
            pygame.draw.rect(screen, theme.TEXT, rect, width=2, border_radius=18)

            label = self.label_font.render(self.COLORS[i]["name"], True, theme.BACKGROUND)
            screen.blit(label, label.get_rect(center=rect.center))

        if self.paused and self.state != self.STATE_OVER:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.state == self.STATE_OVER:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Sequence Broken",
                f"Best Round: {self.round_reached}",
                "Press Space / Click / F5 to restart.",
            )