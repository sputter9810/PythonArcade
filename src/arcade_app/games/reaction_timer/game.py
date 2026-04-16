from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class ReactionTimerGame(GameBase):
    game_id = "reaction_timer"
    title = "Reaction Timer"

    TOTAL_ROUNDS = 5

    STATE_IDLE = "idle"
    STATE_WAITING = "waiting"
    STATE_READY = "ready"
    STATE_RESULT = "result"
    STATE_SESSION_COMPLETE = "session_complete"
    STATE_FALSE_START = "false_start"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 960, 620)

        self.state = self.STATE_IDLE
        self.round_index = 0
        self.wait_timer = 0.0
        self.ready_timer = 0.0
        self.result_timer = 0.0

        self.last_reaction_ms = 0
        self.best_reaction_ms_value: int | None = None
        self.false_starts = 0
        self.results: list[int] = []

        self.pulse_timer = 0.0
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.state = self.STATE_IDLE
        self.round_index = 0
        self.wait_timer = 0.0
        self.ready_timer = 0.0
        self.result_timer = 0.0

        self.last_reaction_ms = 0
        self.best_reaction_ms_value = None
        self.false_starts = 0
        self.results = []

        self.pulse_timer = 0.0
        self.paused = False

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(0, 0, 960, 620)
        self.play_rect.centerx = screen.get_width() // 2
        self.play_rect.top = 150

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def start_round(self) -> None:
        self.state = self.STATE_WAITING
        self.wait_timer = random.uniform(1.4, 3.4)
        self.ready_timer = 0.0
        self.result_timer = 0.0

    def advance_after_round(self) -> None:
        if self.round_index >= self.TOTAL_ROUNDS:
            self.state = self.STATE_SESSION_COMPLETE
        else:
            self.state = self.STATE_IDLE

    def average_reaction_ms(self) -> int:
        if not self.results:
            return 0
        return int(sum(self.results) / len(self.results))

    def best_reaction_ms(self) -> int:
        if self.best_reaction_ms_value is None:
            return 0
        return self.best_reaction_ms_value

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()

        if self.best_reaction_ms_value is not None:
            payload["reaction_ms"] = self.best_reaction_ms_value

        payload["round"] = max(self.round_index, len(self.results))
        payload["accuracy"] = 0.0 if self.TOTAL_ROUNDS == 0 else round((len(self.results) / self.TOTAL_ROUNDS) * 100.0, 1)
        payload["score"] = max(0, 5000 - self.average_reaction_ms()) if self.results else 0

        return payload

    def react_now(self) -> None:
        if self.paused:
            return

        if self.state == self.STATE_IDLE:
            self.start_round()
            return

        if self.state == self.STATE_WAITING:
            self.false_starts += 1
            self.last_reaction_ms = 0
            self.state = self.STATE_FALSE_START
            self.result_timer = 0.8
            return

        if self.state == self.STATE_READY:
            reaction_ms = int(self.ready_timer * 1000)
            self.last_reaction_ms = reaction_ms
            self.results.append(reaction_ms)

            if self.best_reaction_ms_value is None or reaction_ms < self.best_reaction_ms_value:
                self.best_reaction_ms_value = reaction_ms

            self.round_index += 1
            self.state = self.STATE_RESULT
            self.result_timer = 1.0
            return

        if self.state == self.STATE_RESULT:
            self.advance_after_round()
            return

        if self.state == self.STATE_FALSE_START:
            self.state = self.STATE_IDLE
            return

        if self.state == self.STATE_SESSION_COMPLETE:
            self.reset_game()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and self.state != self.STATE_SESSION_COMPLETE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.react_now()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.react_now()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused:
            return

        self.pulse_timer += dt

        if self.state == self.STATE_WAITING:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.state = self.STATE_READY
                self.ready_timer = 0.0

        elif self.state == self.STATE_READY:
            self.ready_timer += dt

        elif self.state in (self.STATE_RESULT, self.STATE_FALSE_START):
            self.result_timer -= dt
            if self.result_timer <= 0:
                if self.state == self.STATE_RESULT:
                    self.advance_after_round()
                else:
                    self.state = self.STATE_IDLE

    def panel_color(self) -> tuple[int, int, int]:
        if self.state == self.STATE_READY:
            return (38, 118, 70)
        if self.state == self.STATE_FALSE_START:
            return (120, 46, 46)
        if self.state == self.STATE_RESULT:
            return (54, 62, 96)
        return theme.SURFACE

    def status_title_and_subtitle(self) -> tuple[str, str]:
        if self.state == self.STATE_IDLE:
            if self.round_index == 0 and not self.results and self.false_starts == 0:
                return ("Reaction Timer", "Press Space, Enter, or Click to begin.")
            return ("Next Round", "Press Space, Enter, or Click when you're ready.")
        if self.state == self.STATE_WAITING:
            return ("Wait...", "Do not press anything until the panel turns green.")
        if self.state == self.STATE_READY:
            return ("CLICK!", "React now.")
        if self.state == self.STATE_RESULT:
            return (f"{self.last_reaction_ms} ms", "Nice. Get ready for the next round.")
        if self.state == self.STATE_FALSE_START:
            return ("Too Early", "That was a false start.")
        return ("Session Complete", "Press Space, Enter, or Click to restart.")

    def draw_signal_panel(self, screen: pygame.Surface) -> None:
        panel_rect = self.play_rect.inflate(-120, -180)
        panel_rect.centery += 10

        pygame.draw.rect(screen, self.panel_color(), panel_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        if self.state == self.STATE_WAITING:
            pulse = 0.5 + 0.5 * ((pygame.time.get_ticks() // 250) % 2)
            circle_color = theme.WARNING if pulse > 0.5 else theme.MUTED_TEXT
            pygame.draw.circle(screen, circle_color, panel_rect.center, 34)

        elif self.state == self.STATE_READY:
            pygame.draw.circle(screen, theme.TEXT, panel_rect.center, 14)

        elif self.state == self.STATE_FALSE_START:
            pygame.draw.line(
                screen,
                theme.TEXT,
                (panel_rect.centerx - 30, panel_rect.centery - 30),
                (panel_rect.centerx + 30, panel_rect.centery + 30),
                8,
            )
            pygame.draw.line(
                screen,
                theme.TEXT,
                (panel_rect.centerx + 30, panel_rect.centery - 30),
                (panel_rect.centerx - 30, panel_rect.centery + 30),
                8,
            )

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.ui.big_font is not None
        assert self.ui.info_font is not None
        assert self.ui.small_font is not None

        self.ui.draw_header(
            screen,
            "Reaction Timer",
            "Press Space / Enter / Click to react. F5 restart, Esc back.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Round: {min(self.round_index + (1 if self.state in (self.STATE_WAITING, self.STATE_READY) else 0), self.TOTAL_ROUNDS)}/{self.TOTAL_ROUNDS}",
                f"Best: {self.best_reaction_ms()} ms" if self.results else "Best: --",
                f"Average: {self.average_reaction_ms()} ms" if self.results else "Average: --",
                f"False Starts: {self.false_starts}",
            ],
        )
        self.ui.draw_sub_stats(
            screen,
            "Wait for green, react instantly, and avoid false starts.",
        )
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        heading, subheading = self.status_title_and_subtitle()

        heading_surface = self.ui.big_font.render(heading, True, theme.TEXT)
        subheading_surface = self.ui.info_font.render(subheading, True, theme.TEXT)

        center_y = self.play_rect.centery + 40
        screen.blit(heading_surface, heading_surface.get_rect(center=(self.play_rect.centerx, center_y - 30)))
        screen.blit(subheading_surface, subheading_surface.get_rect(center=(self.play_rect.centerx, center_y + 30)))

        if self.state == self.STATE_SESSION_COMPLETE:
            summary = [
                f"Best Reaction: {self.best_reaction_ms()} ms",
                f"Average Reaction: {self.average_reaction_ms()} ms",
                f"Successful Rounds: {len(self.results)}/{self.TOTAL_ROUNDS}",
            ]
            for i, line in enumerate(summary):
                summary_surface = self.ui.small_font.render(line, True, theme.MUTED_TEXT)
                screen.blit(summary_surface, summary_surface.get_rect(center=(self.play_rect.centerx, center_y + 84 + i * 28)))

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_game_over(
            screen,
            self.play_rect,
            "Session Complete",
            f"Best Reaction: {self.best_reaction_ms()} ms",
            f"Average: {self.average_reaction_ms()} ms  |  False Starts: {self.false_starts}",
        )

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        self.draw_signal_panel(screen)
        self.render_hud(screen)

        if self.paused and self.state != self.STATE_SESSION_COMPLETE:
            assert self.ui is not None
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.state == self.STATE_SESSION_COMPLETE:
            self.render_game_over_overlay(screen)