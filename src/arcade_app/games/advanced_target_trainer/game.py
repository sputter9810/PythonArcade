from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class AdvancedTargetTrainerGame(GameBase):
    game_id = "advanced_target_trainer"
    title = "Advanced Target Trainer"

    SESSION_LENGTH = 40.0
    TARGET_MIN_UPTIME = 0.45
    TARGET_MAX_UPTIME = 1.25
    TARGET_MIN_DELAY = 0.18
    TARGET_MAX_DELAY = 0.75

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 980, 640)
        self.lane_rects: list[pygame.Rect] = []
        self.targets: list[dict] = []
        self.popups: list[dict] = []

        self.spawn_timer = 0.0
        self.time_left = self.SESSION_LENGTH
        self.game_over = False
        self.paused = False

        self.score = 0
        self.hits = 0
        self.misses = 0
        self.click_misses = 0
        self.combo = 0
        self.best_combo = 0

        self.flash_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.targets = []
        self.popups = []
        self.spawn_timer = 0.55
        self.time_left = self.SESSION_LENGTH
        self.game_over = False
        self.paused = False

        self.score = 0
        self.hits = 0
        self.misses = 0
        self.click_misses = 0
        self.combo = 0
        self.best_combo = 0

        self.flash_timer = 0.0

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(0, 0, 980, 640)
        self.play_rect.centerx = screen.get_width() // 2
        self.play_rect.top = 150

        self.lane_rects = []
        cols = 4
        rows = 2
        gap_x = 22
        gap_y = 28
        pad_x = 28
        pad_y = 30

        available_w = self.play_rect.width - pad_x * 2
        available_h = self.play_rect.height - pad_y * 2
        cell_w = (available_w - gap_x * (cols - 1)) // cols
        cell_h = (available_h - gap_y * (rows - 1)) // rows

        for row in range(rows):
            for col in range(cols):
                x = self.play_rect.left + pad_x + col * (cell_w + gap_x)
                y = self.play_rect.top + pad_y + row * (cell_h + gap_y)
                self.lane_rects.append(pygame.Rect(x, y, cell_w, cell_h))

    def accuracy(self) -> float:
        attempts = self.hits + self.misses + self.click_misses
        if attempts == 0:
            return 100.0
        return (self.hits / attempts) * 100.0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = self.hits
        payload["accuracy"] = round(self.accuracy(), 1)
        payload["round"] = self.best_combo
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -44),
                "life": 0.65,
                "max_life": 0.65,
                "color": color,
                "alpha": 255,
            }
        )

    def update_popups(self, dt: float) -> None:
        updated: list[dict] = []
        for popup in self.popups:
            popup["life"] -= dt
            if popup["life"] <= 0:
                continue
            popup["pos"] += popup["vel"] * dt
            popup["alpha"] = int(255 * (popup["life"] / popup["max_life"]))
            updated.append(popup)
        self.popups = updated

    def current_spawn_delay(self) -> float:
        progress = 1.0 - (self.time_left / self.SESSION_LENGTH)
        value = self.TARGET_MAX_DELAY - progress * 0.42
        return max(self.TARGET_MIN_DELAY, value)

    def current_target_uptime(self) -> float:
        progress = 1.0 - (self.time_left / self.SESSION_LENGTH)
        value = self.TARGET_MAX_UPTIME - progress * 0.55
        return max(self.TARGET_MIN_UPTIME, value)

    def active_lane_indices(self) -> set[int]:
        return {target["lane_index"] for target in self.targets}

    def spawn_target(self) -> None:
        available = [i for i in range(len(self.lane_rects)) if i not in self.active_lane_indices()]
        if not available:
            return

        lane_index = random.choice(available)
        lane_rect = self.lane_rects[lane_index]

        target_radius = min(lane_rect.width, lane_rect.height) // 5
        center = lane_rect.center

        kind = random.choices(
            population=["standard", "fast", "bonus"],
            weights=[6, 3, 1],
            k=1,
        )[0]

        if kind == "fast":
            uptime = self.current_target_uptime() * 0.72
            color = theme.WARNING
            value = 140
        elif kind == "bonus":
            uptime = self.current_target_uptime() * 0.90
            color = theme.ACCENT
            value = 220
        else:
            uptime = self.current_target_uptime()
            color = theme.DANGER
            value = 100

        self.targets.append(
            {
                "lane_index": lane_index,
                "center": center,
                "radius": target_radius,
                "time_left": uptime,
                "max_time": uptime,
                "color": color,
                "value": value,
                "kind": kind,
            }
        )

    def register_hit(self, target: dict) -> None:
        self.hits += 1
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)

        combo_bonus = min(180, self.combo * 12)
        reward = target["value"] + combo_bonus
        self.score += reward
        self.flash_timer = 0.10
        self.add_popup(f"+{reward}", target["center"], theme.ACCENT)

    def register_expired_target(self, target: dict) -> None:
        self.misses += 1
        self.combo = 0
        self.score = max(0, self.score - 45)
        self.add_popup("-45", target["center"], theme.WARNING)

    def register_click_miss(self, pos: tuple[int, int]) -> None:
        self.click_misses += 1
        self.combo = 0
        self.score = max(0, self.score - 25)
        self.add_popup("-25", pos, theme.DANGER)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()
                    continue

                if self.paused:
                    continue

                mouse_pos = pygame.Vector2(event.pos)
                hit_target = None
                for target in reversed(self.targets):
                    if mouse_pos.distance_to(target["center"]) <= target["radius"]:
                        hit_target = target
                        break

                if hit_target is not None:
                    self.register_hit(hit_target)
                    self.targets.remove(hit_target)
                else:
                    self.register_click_miss((int(mouse_pos.x), int(mouse_pos.y)))

    def update_targets(self, dt: float) -> None:
        updated_targets: list[dict] = []
        for target in self.targets:
            target["time_left"] -= dt
            if target["time_left"] <= 0:
                self.register_expired_target(target)
                continue
            updated_targets.append(target)
        self.targets = updated_targets

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.paused:
            return

        if self.game_over:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self.game_over = True
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            spawn_count = 1
            if self.time_left < 20 and random.random() < 0.30:
                spawn_count = 2
            for _ in range(spawn_count):
                self.spawn_target()
            self.spawn_timer = self.current_spawn_delay()

        self.update_targets(dt)

    def draw_lane_grid(self, screen: pygame.Surface) -> None:
        panel_color = theme.SURFACE_ALT if self.flash_timer > 0 else theme.SURFACE
        pygame.draw.rect(screen, panel_color, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for lane_rect in self.lane_rects:
            pygame.draw.rect(screen, theme.BACKGROUND, lane_rect, border_radius=theme.RADIUS_SMALL)
            pygame.draw.rect(screen, theme.SURFACE_ALT, lane_rect, width=1, border_radius=theme.RADIUS_SMALL)

    def draw_targets(self, screen: pygame.Surface) -> None:
        for target in self.targets:
            center = target["center"]
            radius = target["radius"]

            pygame.draw.circle(screen, target["color"], center, radius)
            pygame.draw.circle(screen, theme.TEXT, center, max(8, radius // 2))
            pygame.draw.circle(screen, theme.ACCENT, center, max(3, radius // 5))

            progress = max(0.0, target["time_left"] / target["max_time"])
            bar_width = radius * 2
            bar_rect = pygame.Rect(0, 0, int(bar_width * progress), 8)
            bar_rect.midtop = (center[0], center[1] + radius + 10)

            bg_rect = pygame.Rect(0, 0, bar_width, 8)
            bg_rect.midtop = (center[0], center[1] + radius + 10)
            pygame.draw.rect(screen, theme.SURFACE_ALT, bg_rect, border_radius=999)
            if bar_rect.width > 0:
                pygame.draw.rect(screen, target["color"], bar_rect, border_radius=999)

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_header(
            screen,
            "Advanced Target Trainer",
            "Click targets fast, keep combos alive, and avoid misses. F5 restart, Esc back.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Hits: {self.hits}",
                f"Combo: {self.combo}",
                f"Accuracy: {self.accuracy():0.1f}%",
                f"Time: {self.time_left:0.1f}s",
            ],
        )
        self.ui.draw_sub_stats(
            screen,
            f"Expired Targets: {self.misses}  |  Click Misses: {self.click_misses}  |  Best Combo: {self.best_combo}",
        )
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_game_over(
            screen,
            self.play_rect,
            "Session Complete",
            f"Final Score: {self.score}",
            f"Hits: {self.hits}  |  Accuracy: {self.accuracy():0.1f}%  |  Best Combo: {self.best_combo}",
        )

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)
        self.draw_lane_grid(screen)
        self.draw_targets(screen)
        self.render_hud(screen)

        if self.ui is not None:
            self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.game_over:
            assert self.ui is not None
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.render_game_over_overlay(screen)