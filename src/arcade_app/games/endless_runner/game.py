from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class EndlessRunnerGame(GameBase):
    game_id = "endless_runner"
    title = "Endless Runner"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1200, 620)
        self.ground_y = 0

        self.player = pygame.Rect(0, 0, 52, 68)
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)

        self.player_width = 52
        self.player_height = 68
        self.player_duck_height = 40

        self.gravity = 1850.0
        self.jump_strength = -760.0
        self.max_fall_speed = 1200.0

        self.on_ground = True
        self.jump_buffer_timer = 0.0
        self.jump_buffer_window = 0.12
        self.coyote_timer = 0.0
        self.coyote_window = 0.10

        self.score = 0
        self.distance = 0.0
        self.best_chain = 0
        self.obstacles_cleared = 0

        self.game_over = False
        self.base_speed = 420.0
        self.scroll_speed = self.base_speed
        self.spawn_timer = 0.0

        self.obstacles: list[dict] = []
        self.clouds: list[dict] = []
        self.track_marks: list[float] = []

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

        self.score = 0
        self.distance = 0.0
        self.best_chain = 0
        self.obstacles_cleared = 0
        self.game_over = False
        self.scroll_speed = self.base_speed
        self.spawn_timer = 0.9
        self.obstacles.clear()

        self.player.width = self.player_width
        self.player.height = self.player_height
        self.player_pos.x = self.play_rect.left + 120
        self.player_pos.y = self.ground_y - self.player.height
        self.player.topleft = (round(self.player_pos.x), round(self.player_pos.y))
        self.player_vel.xy = (0.0, 0.0)

        self.on_ground = True
        self.jump_buffer_timer = 0.0
        self.coyote_timer = self.coyote_window

        self.clouds = [
            {"x": self.play_rect.left + 140, "y": self.play_rect.top + 70, "speed": 24, "size": 54},
            {"x": self.play_rect.left + 460, "y": self.play_rect.top + 120, "speed": 18, "size": 66},
            {"x": self.play_rect.left + 860, "y": self.play_rect.top + 90, "speed": 22, "size": 48},
        ]
        self.track_marks = [self.play_rect.left + i * 130 for i in range(12)]

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1200) // 2,
            140,
            1200,
            620,
        )
        self.ground_y = self.play_rect.bottom - 90

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def request_jump(self) -> None:
        self.jump_buffer_timer = self.jump_buffer_window

    def current_ducking(self) -> bool:
        keys = pygame.key.get_pressed()
        return keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

    def perform_jump_if_possible(self) -> None:
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.player_vel.y = self.jump_strength
            self.on_ground = False
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0

    def update_player_shape(self) -> None:
        ducking = self.current_ducking() and self.on_ground and not self.game_over
        previous_bottom = self.player.bottom

        self.player.width = self.player_width
        self.player.height = self.player_duck_height if ducking else self.player_height
        self.player.x = round(self.player_pos.x)
        self.player.bottom = previous_bottom
        self.player_pos.y = float(self.player.y)

    def spawn_obstacle(self) -> None:
        kind = random.choices(
            population=["crate", "spike", "drone"],
            weights=[5, 4, 3 if self.score >= 250 else 0],
            k=1,
        )[0]

        x = self.play_rect.right + random.randint(40, 160)

        if kind == "crate":
            rect = pygame.Rect(x, self.ground_y - 54, 44, 54)
            color = theme.WARNING
        elif kind == "spike":
            rect = pygame.Rect(x, self.ground_y - 32, 56, 32)
            color = theme.DANGER
        else:
            rect = pygame.Rect(x, self.ground_y - 92, 66, 30)
            color = theme.ACCENT

        self.obstacles.append(
            {
                "kind": kind,
                "rect": rect,
                "color": color,
                "passed": False,
            }
        )

    def update_clouds(self, dt: float) -> None:
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"] * dt
            if cloud["x"] < self.play_rect.left - 140:
                cloud["x"] = self.play_rect.right + random.randint(40, 180)
                cloud["y"] = self.play_rect.top + random.randint(55, 145)
                cloud["size"] = random.randint(42, 72)

    def update_track_marks(self, dt: float) -> None:
        for i in range(len(self.track_marks)):
            self.track_marks[i] -= self.scroll_speed * dt
            if self.track_marks[i] < self.play_rect.left - 60:
                self.track_marks[i] = self.play_rect.right + random.randint(20, 60)

    def update_player(self, dt: float) -> None:
        previous_grounded = self.on_ground

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        if self.coyote_timer > 0:
            self.coyote_timer -= dt

        self.perform_jump_if_possible()

        self.player_vel.y += self.gravity * dt
        if self.player_vel.y > self.max_fall_speed:
            self.player_vel.y = self.max_fall_speed

        self.player_pos.y += self.player_vel.y * dt
        self.player.y = round(self.player_pos.y)

        self.on_ground = False
        if self.player.bottom >= self.ground_y:
            self.player.bottom = self.ground_y
            self.player_pos.y = float(self.player.y)
            self.player_vel.y = 0.0
            self.on_ground = True

        if self.on_ground:
            self.coyote_timer = self.coyote_window
        elif previous_grounded:
            self.coyote_timer = self.coyote_window

        self.update_player_shape()
        self.perform_jump_if_possible()

    def update_obstacles(self, dt: float) -> None:
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_obstacle()
            min_delay = max(0.48, 0.95 - min(0.35, self.score / 2800))
            max_delay = max(min_delay + 0.08, 1.25 - min(0.40, self.score / 2600))
            self.spawn_timer = random.uniform(min_delay, max_delay)

        for obstacle in self.obstacles:
            obstacle["rect"].x -= round(self.scroll_speed * dt)

            if not obstacle["passed"] and obstacle["rect"].right < self.player.left:
                obstacle["passed"] = True
                self.obstacles_cleared += 1
                self.score += 35

        self.obstacles = [obstacle for obstacle in self.obstacles if obstacle["rect"].right > self.play_rect.left - 120]

    def check_collisions(self) -> None:
        for obstacle in self.obstacles:
            if self.player.colliderect(obstacle["rect"]):
                self.game_over = True
                return

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_clouds(dt)
        self.update_track_marks(dt)

        if self.game_over:
            return

        self.scroll_speed = self.base_speed + min(240.0, self.distance * 0.045)
        self.distance += self.scroll_speed * dt
        self.score = max(self.score, int(self.distance / 18) + self.obstacles_cleared * 20)

        self.update_player(dt)
        self.update_obstacles(dt)
        self.check_collisions()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.request_jump()
                elif event.key == pygame.K_F5:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()
                else:
                    self.request_jump()

    def draw_background(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)

        sky_rect = pygame.Rect(self.play_rect.left, self.play_rect.top, self.play_rect.width, self.play_rect.height)
        pygame.draw.rect(screen, (24, 28, 38), sky_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, sky_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        hill_points_back = [
            (self.play_rect.left, self.ground_y),
            (self.play_rect.left + 180, self.ground_y - 90),
            (self.play_rect.left + 420, self.ground_y - 40),
            (self.play_rect.left + 650, self.ground_y - 120),
            (self.play_rect.left + 940, self.ground_y - 55),
            (self.play_rect.right, self.ground_y),
        ]
        hill_points_front = [
            (self.play_rect.left, self.ground_y),
            (self.play_rect.left + 120, self.ground_y - 40),
            (self.play_rect.left + 360, self.ground_y - 18),
            (self.play_rect.left + 540, self.ground_y - 70),
            (self.play_rect.left + 760, self.ground_y - 30),
            (self.play_rect.left + 1020, self.ground_y - 56),
            (self.play_rect.right, self.ground_y),
        ]

        pygame.draw.polygon(screen, (36, 42, 58), hill_points_back)
        pygame.draw.polygon(screen, (46, 54, 74), hill_points_front)

        for cloud in self.clouds:
            x = int(cloud["x"])
            y = int(cloud["y"])
            size = int(cloud["size"])
            cloud_color = (72, 80, 104)
            pygame.draw.circle(screen, cloud_color, (x, y), size // 2)
            pygame.draw.circle(screen, cloud_color, (x + size // 3, y - 6), size // 2)
            pygame.draw.circle(screen, cloud_color, (x + size // 2, y + 4), size // 2)

        ground_rect = pygame.Rect(self.play_rect.left, self.ground_y, self.play_rect.width, self.play_rect.bottom - self.ground_y)
        pygame.draw.rect(screen, (58, 72, 52), ground_rect, border_radius=0)

        for mark_x in self.track_marks:
            mark_rect = pygame.Rect(int(mark_x), self.ground_y + 36, 64, 8)
            pygame.draw.rect(screen, (90, 104, 82), mark_rect, border_radius=999)

    def draw_player(self, screen: pygame.Surface) -> None:
        body_color = theme.ACCENT if not self.game_over else theme.DANGER
        pygame.draw.rect(screen, body_color, self.player, border_radius=10)

        eye_y = self.player.y + 16
        pygame.draw.circle(screen, theme.TEXT, (self.player.x + 16, eye_y), 3)
        pygame.draw.circle(screen, theme.TEXT, (self.player.x + 32, eye_y), 3)

        if self.player.height > 50:
            pygame.draw.line(
                screen,
                theme.TEXT,
                (self.player.x + 12, self.player.bottom - 4),
                (self.player.x + 12, self.player.bottom + 12),
                3,
            )
            pygame.draw.line(
                screen,
                theme.TEXT,
                (self.player.right - 12, self.player.bottom - 4),
                (self.player.right - 12, self.player.bottom + 12),
                3,
            )

    def draw_obstacles(self, screen: pygame.Surface) -> None:
        for obstacle in self.obstacles:
            rect = obstacle["rect"]
            if obstacle["kind"] == "spike":
                points = [
                    (rect.left, rect.bottom),
                    (rect.left + rect.width // 3, rect.top),
                    (rect.centerx, rect.bottom),
                    (rect.left + 2 * rect.width // 3, rect.top),
                    (rect.right, rect.bottom),
                ]
                pygame.draw.polygon(screen, obstacle["color"], points)
            elif obstacle["kind"] == "drone":
                pygame.draw.rect(screen, obstacle["color"], rect, border_radius=8)
                pygame.draw.rect(screen, theme.TEXT, rect.inflate(-18, -12), border_radius=6)
            else:
                pygame.draw.rect(screen, obstacle["color"], rect, border_radius=8)
                band = pygame.Rect(rect.x, rect.y + 12, rect.width, 10)
                pygame.draw.rect(screen, theme.BACKGROUND, band, border_radius=6)

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        title = self.title_font.render("Endless Runner", True, theme.TEXT)
        subtitle = self.small_font.render(
            "Jump with Space / W / Up. Duck with S / Down / Ctrl. F5 to restart, Esc to leave.",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 38)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 72)))

        stat_y = 110
        stats = [
            f"Score: {self.score}",
            f"Distance: {int(self.distance)}",
            f"Cleared: {self.obstacles_cleared}",
            f"Speed: {int(self.scroll_speed)}",
        ]
        spacing = 220
        start_x = screen.get_width() // 2 - spacing * (len(stats) - 1) // 2
        for index, text in enumerate(stats):
            surface = self.info_font.render(text, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=(start_x + index * spacing, stat_y)))

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.big_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        panel = pygame.Rect(0, 0, 540, 230)
        panel.center = self.play_rect.center
        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        screen.blit(overlay, panel.topleft)
        pygame.draw.rect(screen, theme.ACCENT, panel, width=2, border_radius=theme.RADIUS_MEDIUM)

        title = self.big_font.render("Run Over", True, theme.TEXT)
        score = self.info_font.render(f"Final Score: {self.score}", True, theme.TEXT)
        cleared = self.info_font.render(f"Obstacles Cleared: {self.obstacles_cleared}", True, theme.TEXT)
        controls = self.small_font.render(
            "Press Space / Click / F5 to restart   |   Esc to go back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 56)))
        screen.blit(score, score.get_rect(center=(panel.centerx, panel.top + 114)))
        screen.blit(cleared, cleared.get_rect(center=(panel.centerx, panel.top + 148)))
        screen.blit(controls, controls.get_rect(center=(panel.centerx, panel.top + 192)))

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        self.draw_background(screen)
        self.render_hud(screen)
        self.draw_obstacles(screen)
        self.draw_player(screen)

        if self.game_over:
            self.render_game_over_overlay(screen)