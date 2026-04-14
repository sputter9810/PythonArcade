from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class DodgeFallingBlocksGame(GameBase):
    game_id = "dodge_falling_blocks"
    title = "Dodge the Falling Blocks"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 900, 680)

        self.player = pygame.Rect(0, 0, 74, 28)
        self.player_speed = 520.0

        self.blocks: list[dict] = []
        self.particles: list[dict] = []

        self.score = 0
        self.survival_time = 0.0
        self.level = 1
        self.near_misses = 0
        self.game_over = False

        self.spawn_timer = 0.0
        self.flash_timer = 0.0
        self.background_offset = 0.0

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.big_font = pygame.font.SysFont("arial", 52, bold=True)
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.blocks.clear()
        self.particles.clear()

        self.score = 0
        self.survival_time = 0.0
        self.level = 1
        self.near_misses = 0
        self.game_over = False

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

        self.background_offset += 180 * dt
        self.update_particles(dt)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.game_over:
            return

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
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        title = self.title_font.render("Dodge the Falling Blocks", True, theme.TEXT)
        subtitle = self.small_font.render(
            "Move with Arrow Keys or A/D. Survive, dodge cleanly, and avoid the drop. F5 restart, Esc back.",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 38)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 72)))

        stats = [
            f"Score: {self.score}",
            f"Time: {self.survival_time:0.1f}s",
            f"Level: {self.level}",
            f"Near Misses: {self.near_misses}",
        ]

        start_x = screen.get_width() // 2 - 330
        gap = 220
        for index, stat in enumerate(stats):
            surface = self.info_font.render(stat, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=(start_x + index * gap, 112)))

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.big_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        panel = pygame.Rect(0, 0, 560, 240)
        panel.center = self.play_rect.center

        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        screen.blit(overlay, panel.topleft)
        pygame.draw.rect(screen, theme.ACCENT, panel, width=2, border_radius=theme.RADIUS_MEDIUM)

        title = self.big_font.render("Run Ended", True, theme.TEXT)
        score = self.info_font.render(f"Final Score: {self.score}", True, theme.TEXT)
        time_text = self.info_font.render(f"Survival Time: {self.survival_time:0.1f}s", True, theme.TEXT)
        controls = self.small_font.render(
            "Press Space / Enter / Click / F5 to restart   |   Esc to go back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 58)))
        screen.blit(score, score.get_rect(center=(panel.centerx, panel.top + 118)))
        screen.blit(time_text, time_text.get_rect(center=(panel.centerx, panel.top + 152)))
        screen.blit(controls, controls.get_rect(center=(panel.centerx, panel.top + 198)))

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        self.draw_background(screen)
        self.draw_blocks(screen)
        self.draw_player(screen)
        self.draw_particles(screen)
        self.render_hud(screen)

        if self.game_over:
            self.render_game_over_overlay(screen)