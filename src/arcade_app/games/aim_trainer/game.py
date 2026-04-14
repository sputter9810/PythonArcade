from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class AimTrainerGame(GameBase):
    game_id = "aim_trainer"
    title = "Aim Trainer"

    SESSION_LENGTH = 30.0
    TARGET_BASE_RADIUS = 34
    TARGET_MIN_RADIUS = 22
    TARGET_MAX_RADIUS = 42
    TARGET_LIFETIME_START = 1.1
    TARGET_LIFETIME_MIN = 0.5

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None

        self.playfield_rect = pygame.Rect(0, 0, 920, 520)
        self.target_center = pygame.Vector2(0, 0)
        self.target_radius = self.TARGET_BASE_RADIUS
        self.target_elapsed = 0.0
        self.target_lifetime = self.TARGET_LIFETIME_START

        self.score = 0
        self.hits = 0
        self.misses = 0
        self.targets_missed = 0
        self.shots_taken = 0
        self.time_left = self.SESSION_LENGTH
        self.is_game_over = False
        self.session_started = False

        self.total_reaction_time = 0.0
        self.best_reaction_time: float | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.big_font = pygame.font.SysFont("arial", 52, bold=True)
        self.reset_game()

    def reset_game(self) -> None:
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.targets_missed = 0
        self.shots_taken = 0
        self.time_left = self.SESSION_LENGTH
        self.is_game_over = False
        self.session_started = True
        self.total_reaction_time = 0.0
        self.best_reaction_time = None
        self.target_elapsed = 0.0
        self.target_lifetime = self.TARGET_LIFETIME_START
        self.target_radius = self.TARGET_BASE_RADIUS
        self.spawn_new_target()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        width = min(920, screen.get_width() - 120)
        height = min(520, screen.get_height() - 260)
        self.playfield_rect = pygame.Rect(0, 0, width, height)
        self.playfield_rect.centerx = screen.get_width() // 2
        self.playfield_rect.top = 150

    def spawn_new_target(self) -> None:
        screen = pygame.display.get_surface()
        if screen is None:
            return

        self.rebuild_layout(screen)

        margin = 54
        min_x = self.playfield_rect.left + margin
        max_x = self.playfield_rect.right - margin
        min_y = self.playfield_rect.top + margin
        max_y = self.playfield_rect.bottom - margin

        self.target_center = pygame.Vector2(
            random.randint(min_x, max_x),
            random.randint(min_y, max_y),
        )
        self.target_elapsed = 0.0

        difficulty_progress = self.hits / 24 if self.hits > 0 else 0.0
        shrink = min(12, int(difficulty_progress * 12))
        self.target_radius = max(self.TARGET_MIN_RADIUS, self.TARGET_BASE_RADIUS - shrink)
        self.target_lifetime = max(
            self.TARGET_LIFETIME_MIN,
            self.TARGET_LIFETIME_START - min(0.6, self.hits * 0.025),
        )

    def accuracy(self) -> float:
        if self.shots_taken == 0:
            return 100.0
        return (self.hits / self.shots_taken) * 100.0

    def average_reaction_ms(self) -> int:
        if self.hits == 0:
            return 0
        return int((self.total_reaction_time / self.hits) * 1000)

    def best_reaction_ms(self) -> int:
        if self.best_reaction_time is None:
            return 0
        return int(self.best_reaction_time * 1000)

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def handle_hit(self) -> None:
        reaction_time = self.target_elapsed
        self.hits += 1
        self.shots_taken += 1
        self.total_reaction_time += reaction_time

        if self.best_reaction_time is None or reaction_time < self.best_reaction_time:
            self.best_reaction_time = reaction_time

        speed_bonus = max(0, int((self.target_lifetime - reaction_time) * 140))
        self.score += 100 + speed_bonus
        self.spawn_new_target()

    def handle_miss(self) -> None:
        self.misses += 1
        self.shots_taken += 1
        self.score = max(0, self.score - 35)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_SPACE and self.is_game_over:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_game_over:
                    continue

                self.shots_taken += 1
                mouse_pos = pygame.Vector2(event.pos)
                distance = mouse_pos.distance_to(self.target_center)

                if distance <= self.target_radius:
                    self.shots_taken -= 1
                    self.handle_hit()
                else:
                    self.shots_taken -= 1
                    self.handle_miss()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.is_game_over or not self.session_started:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self.is_game_over = True
            return

        self.target_elapsed += dt
        if self.target_elapsed >= self.target_lifetime:
            self.targets_missed += 1
            self.score = max(0, self.score - 20)
            self.spawn_new_target()

    def draw_target(self, screen: pygame.Surface) -> None:
        pulse = 1.0 + 0.08 * math.sin(self.target_elapsed * 9.0)
        outer_radius = int(self.target_radius * pulse)
        middle_radius = max(12, int(self.target_radius * 0.68))
        inner_radius = max(6, int(self.target_radius * 0.32))

        pygame.draw.circle(screen, theme.WARNING, self.target_center, outer_radius)
        pygame.draw.circle(screen, theme.TEXT, self.target_center, middle_radius)
        pygame.draw.circle(screen, theme.ACCENT, self.target_center, inner_radius)

        timer_progress = min(1.0, self.target_elapsed / self.target_lifetime)
        timer_width = int((self.playfield_rect.width - 32) * (1.0 - timer_progress))
        timer_rect = pygame.Rect(
            self.playfield_rect.left + 16,
            self.playfield_rect.top + 14,
            max(0, timer_width),
            8,
        )
        if timer_rect.width > 0:
            pygame.draw.rect(screen, theme.ACCENT, timer_rect, border_radius=999)

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.big_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        overlay = pygame.Surface((self.playfield_rect.width, self.playfield_rect.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 210))
        screen.blit(overlay, self.playfield_rect.topleft)

        title = self.big_font.render("Session Complete", True, theme.TEXT)
        score = self.info_font.render(f"Final Score: {self.score}", True, theme.TEXT)
        accuracy = self.info_font.render(f"Accuracy: {self.accuracy():.1f}%", True, theme.TEXT)
        avg_reaction = self.info_font.render(
            f"Average Reaction: {self.average_reaction_ms()} ms",
            True,
            theme.TEXT,
        )
        controls = self.small_font.render(
            "Space / F5: Restart  |  Esc: Back to menu",
            True,
            theme.MUTED_TEXT,
        )

        center_x = self.playfield_rect.centerx
        center_y = self.playfield_rect.centery
        screen.blit(title, title.get_rect(center=(center_x, center_y - 70)))
        screen.blit(score, score.get_rect(center=(center_x, center_y - 10)))
        screen.blit(accuracy, accuracy.get_rect(center=(center_x, center_y + 26)))
        screen.blit(avg_reaction, avg_reaction.get_rect(center=(center_x, center_y + 62)))
        screen.blit(controls, controls.get_rect(center=(center_x, center_y + 118)))

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Aim Trainer", True, theme.TEXT)
        subtitle = self.small_font.render(
            "Click targets quickly and cleanly. Faster hits score more.",
            True,
            theme.MUTED_TEXT,
        )
        controls = self.small_font.render(
            "Mouse: Shoot  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 34)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 72)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.playfield_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(
            screen,
            theme.SURFACE_ALT,
            self.playfield_rect,
            width=2,
            border_radius=theme.RADIUS_MEDIUM,
        )

        stat_y = 112
        stat_gap = 165
        stats = [
            f"Score: {self.score}",
            f"Hits: {self.hits}",
            f"Accuracy: {self.accuracy():.1f}%",
            f"Avg RT: {self.average_reaction_ms()} ms",
            f"Time: {self.time_left:0.1f}s",
        ]

        start_x = screen.get_width() // 2 - (stat_gap * 2)
        for index, stat in enumerate(stats):
            stat_surface = self.info_font.render(stat, True, theme.TEXT)
            screen.blit(stat_surface, stat_surface.get_rect(center=(start_x + stat_gap * index, stat_y)))

        detail_text = (
            f"Miss Clicks: {self.misses}  |  Missed Targets: {self.targets_missed}  |  Best RT: {self.best_reaction_ms()} ms"
        )
        detail_surface = self.small_font.render(detail_text, True, theme.MUTED_TEXT)
        screen.blit(detail_surface, detail_surface.get_rect(center=(screen.get_width() // 2, 138)))

        if not self.is_game_over:
            self.draw_target(screen)
        else:
            self.render_game_over_overlay(screen)