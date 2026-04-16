from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class DodgeFallingBlocksGame(GameBase):
    game_id = "dodge_falling_blocks"
    title = "Dodge the Falling Blocks"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 900, 680)

        self.player = pygame.Rect(0, 0, 74, 28)
        self.player_speed = 520.0

        self.blocks: list[dict] = []
        self.particles: list[dict] = []
        self.popups: list[dict] = []

        self.score = 0
        self.survival_time = 0.0
        self.level = 1
        self.near_misses = 0
        self.game_over = False
        self.paused = False

        self.spawn_timer = 0.0
        self.flash_timer = 0.0
        self.background_offset = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.blocks.clear()
        self.particles.clear()
        self.popups.clear()

        self.score = 0
        self.survival_time = 0.0
        self.level = 1
        self.near_misses = 0
        self.game_over = False
        self.paused = False

        self.spawn_timer = 0.45
        self.flash_timer = 0.0
        self.background_offset = 0.0

        self.player.size = (74, 28)
        self.player.midbottom = (self.play_rect.centerx, self.play_rect.bottom - 26)

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(0, 0, 900, 680)
        self.play_rect.centerx = screen.get_width() // 2
        self.play_rect.top = 150

        bottom_margin = 26
        if self.player.height > 0:
            self.player.bottom = self.play_rect.bottom - bottom_margin
            self.player.x = max(self.play_rect.left, min(self.player.x, self.play_rect.right - self.player.width))

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -42),
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
        return max(0.16, 0.48 - min(0.28, self.survival_time * 0.012))

    def current_fall_speed(self) -> float:
        return 260.0 + min(460.0, self.survival_time * 18.0)

    def spawn_block(self) -> None:
        width = random.randint(36, 96)
        height = random.randint(24, 70)

        x = random.randint(self.play_rect.left, self.play_rect.right - width)
        y = self.play_rect.top - height - random.randint(10, 120)

        speed = self.current_fall_speed() * random.uniform(0.88, 1.18)
        color = random.choice([theme.ACCENT, theme.WARNING, theme.DANGER])

        self.blocks.append(
            {
                "rect": pygame.Rect(x, y, width, height),
                "speed": speed,
                "color": color,
                "counted": False,
                "near_miss_awarded": False,
            }
        )

    def add_collision_particles(self) -> None:
        center = self.player.center
        for _ in range(18):
            angle_x = random.uniform(-220, 220)
            angle_y = random.uniform(-260, -60)
            self.particles.append(
                {
                    "pos": pygame.Vector2(center[0], center[1]),
                    "vel": pygame.Vector2(angle_x, angle_y),
                    "life": random.uniform(0.35, 0.7),
                    "radius": random.randint(3, 6),
                }
            )

    def update_particles(self, dt: float) -> None:
        updated: list[dict] = []
        for particle in self.particles:
            particle["life"] -= dt
            if particle["life"] <= 0:
                continue

            particle["vel"].y += 480 * dt
            particle["pos"] += particle["vel"] * dt
            updated.append(particle)

        self.particles = updated

    def handle_player_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1

        self.player.x += round(move * self.player_speed * dt)
        self.player.x = max(self.play_rect.left, min(self.player.x, self.play_rect.right - self.player.width))

    def update_blocks(self, dt: float) -> None:
        self.spawn_timer -= dt
        while self.spawn_timer <= 0:
            self.spawn_block()
            self.spawn_timer += self.current_spawn_delay()

        updated_blocks: list[dict] = []
        player_center_y = self.player.centery

        for block in self.blocks:
            rect = block["rect"]
            rect.y += round(block["speed"] * dt)

            if not block["near_miss_awarded"] and rect.bottom >= player_center_y:
                horizontal_gap = min(
                    abs(rect.right - self.player.left),
                    abs(self.player.right - rect.left),
                )
                overlapping_x = rect.right >= self.player.left and rect.left <= self.player.right

                if not overlapping_x and horizontal_gap <= 22:
                    block["near_miss_awarded"] = True
                    self.near_misses += 1
                    self.score += 25
                    self.add_popup("+25", (rect.centerx, rect.bottom + 12), theme.ACCENT)

            if rect.colliderect(self.player):
                self.game_over = True
                self.flash_timer = 0.35
                self.add_collision_particles()
                return

            if rect.top > self.play_rect.bottom:
                if not block["counted"]:
                    block["counted"] = True
                    self.score += 10
                continue

            updated_blocks.append(block)

        self.blocks = updated_blocks

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_particles(dt)
        self.update_popups(dt)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.paused:
            return

        if self.game_over:
            return

        self.background_offset += 180 * dt
        self.survival_time += dt
        self.level = 1 + int(self.survival_time // 10)
        self.score = max(self.score, int(self.survival_time * 18) + self.near_misses * 25)

        self.handle_player_input(dt)
        self.update_blocks(dt)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()

    def draw_background(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)

        panel_color = theme.SURFACE
        if self.flash_timer > 0:
            panel_color = (70, 42, 42)

        pygame.draw.rect(screen, panel_color, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        stripe_spacing = 54
        stripe_height = 22
        total_stripes = self.play_rect.height // stripe_spacing + 3

        for i in range(total_stripes):
            y = self.play_rect.top + int((i * stripe_spacing + self.background_offset) % (self.play_rect.height + stripe_spacing)) - stripe_spacing
            stripe_rect = pygame.Rect(self.play_rect.left + 12, y, self.play_rect.width - 24, stripe_height)
            pygame.draw.rect(screen, theme.BACKGROUND, stripe_rect, border_radius=999)

    def draw_blocks(self, screen: pygame.Surface) -> None:
        for block in self.blocks:
            rect = block["rect"]
            pygame.draw.rect(screen, block["color"], rect, border_radius=10)

            inner = rect.inflate(-12, -10)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.rect(screen, theme.BACKGROUND, inner, border_radius=8)

    def draw_player(self, screen: pygame.Surface) -> None:
        shadow = self.player.move(0, 8)
        pygame.draw.rect(screen, theme.SURFACE_ALT, shadow, border_radius=14)

        pygame.draw.rect(screen, theme.TEXT, self.player, border_radius=14)

        cockpit = pygame.Rect(
            self.player.x + 16,
            self.player.y + 6,
            self.player.width - 32,
            self.player.height - 12,
        )
        pygame.draw.rect(screen, theme.ACCENT, cockpit, border_radius=10)

    def draw_particles(self, screen: pygame.Surface) -> None:
        for particle in self.particles:
            pos = particle["pos"]
            pygame.draw.circle(
                screen,
                theme.WARNING,
                (int(pos.x), int(pos.y)),
                particle["radius"],
            )

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_header(
            screen,
            "Dodge the Falling Blocks",
            "Move with Arrow Keys or A/D. Survive cleanly and avoid the drop. F5 restart, Esc back.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Time: {self.survival_time:0.1f}s",
                f"Level: {self.level}",
                f"Near Misses: {self.near_misses}",
            ],
        )
        self.ui.draw_sub_stats(
            screen,
            "Thread tight gaps for bonus near misses, but one collision ends the run.",
        )
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_game_over(
            screen,
            self.play_rect,
            "Run Ended",
            f"Final Score: {self.score}",
            f"Survival Time: {self.survival_time:0.1f}s  |  Near Misses: {self.near_misses}",
        )

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        self.draw_background(screen)
        self.draw_blocks(screen)
        self.draw_player(screen)
        self.draw_particles(screen)
        self.render_hud(screen)

        if self.ui is not None:
            self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.game_over:
            assert self.ui is not None
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.render_game_over_overlay(screen)