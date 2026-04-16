from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class PlatformerGame(GameBase):
    game_id = "platformer"
    title = "Platformer"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1200, 640)

        self.player = pygame.Rect(0, 0, 38, 54)
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)

        self.move_speed = 240.0
        self.gravity = 1550.0
        self.jump_strength = -620.0
        self.max_fall_speed = 1200.0

        self.on_ground = False
        self.coyote_timer = 0.0
        self.coyote_window = 0.12
        self.jump_buffer_timer = 0.0
        self.jump_buffer_window = 0.12

        self.platforms: list[pygame.Rect] = []
        self.coins: list[pygame.Rect] = []
        self.exit_rect = pygame.Rect(0, 0, 52, 74)

        self.score = 0
        self.coins_collected = 0
        self.total_coins = 0

        self.game_over = False
        self.paused = False
        self.completed = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1200) // 2,
            165,
            1200,
            640,
        )

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.score = 0
        self.coins_collected = 0
        self.game_over = False
        self.paused = False
        self.completed = False

        self.build_level()

        self.player = pygame.Rect(self.play_rect.left + 60, self.play_rect.bottom - 110, 38, 54)
        self.player_pos = pygame.Vector2(self.player.x, self.player.y)
        self.player_vel = pygame.Vector2(0, 0)

        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = self.coins_collected
        payload["accuracy"] = 100.0 if self.total_coins == 0 else round((self.coins_collected / self.total_coins) * 100.0, 1)
        return payload

    def build_level(self) -> None:
        ground = pygame.Rect(self.play_rect.left, self.play_rect.bottom - 30, self.play_rect.width, 30)

        self.platforms = [
            ground,
            pygame.Rect(self.play_rect.left + 120, self.play_rect.bottom - 130, 180, 18),
            pygame.Rect(self.play_rect.left + 380, self.play_rect.bottom - 220, 180, 18),
            pygame.Rect(self.play_rect.left + 660, self.play_rect.bottom - 300, 180, 18),
            pygame.Rect(self.play_rect.left + 920, self.play_rect.bottom - 190, 180, 18),
            pygame.Rect(self.play_rect.left + 870, self.play_rect.bottom - 390, 170, 18),
        ]

        self.coins = [
            pygame.Rect(self.play_rect.left + 185, self.play_rect.bottom - 170, 18, 18),
            pygame.Rect(self.play_rect.left + 455, self.play_rect.bottom - 260, 18, 18),
            pygame.Rect(self.play_rect.left + 730, self.play_rect.bottom - 340, 18, 18),
            pygame.Rect(self.play_rect.left + 980, self.play_rect.bottom - 230, 18, 18),
            pygame.Rect(self.play_rect.left + 945, self.play_rect.bottom - 430, 18, 18),
        ]
        self.total_coins = len(self.coins)

        self.exit_rect = pygame.Rect(self.play_rect.right - 90, self.play_rect.bottom - 104, 52, 74)

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def request_jump(self) -> None:
        self.jump_buffer_timer = self.jump_buffer_window

    def can_jump(self) -> bool:
        return self.on_ground or self.coyote_timer > 0

    def perform_jump_if_possible(self) -> None:
        if self.jump_buffer_timer > 0 and self.can_jump():
            self.player_vel.y = self.jump_strength
            self.on_ground = False
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.completed and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.completed or self.game_over:
                        self.reset_game()
                    else:
                        self.request_jump()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.completed or self.game_over:
            return

        keys = pygame.key.get_pressed()

        move_dir = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_dir -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_dir += 1.0

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        if self.coyote_timer > 0:
            self.coyote_timer -= dt

        self.perform_jump_if_possible()

        previous_rect = self.player.copy()

        self.player_vel.x = move_dir * self.move_speed
        self.player_pos.x += self.player_vel.x * dt
        self.player.x = round(self.player_pos.x)

        for platform in self.platforms:
            if self.player.colliderect(platform):
                if self.player_vel.x > 0:
                    self.player.right = platform.left
                elif self.player_vel.x < 0:
                    self.player.left = platform.right
                self.player_pos.x = float(self.player.x)

        self.player_vel.y += self.gravity * dt
        if self.player_vel.y > self.max_fall_speed:
            self.player_vel.y = self.max_fall_speed

        self.player_pos.y += self.player_vel.y * dt
        self.player.y = round(self.player_pos.y)

        was_on_ground = self.on_ground
        self.on_ground = False

        for platform in self.platforms:
            if self.player.colliderect(platform):
                if previous_rect.bottom <= platform.top and self.player_vel.y >= 0:
                    self.player.bottom = platform.top
                    self.player_pos.y = float(self.player.y)
                    self.player_vel.y = 0.0
                    self.on_ground = True
                elif previous_rect.top >= platform.bottom and self.player_vel.y < 0:
                    self.player.top = platform.bottom
                    self.player_pos.y = float(self.player.y)
                    self.player_vel.y = 0.0

        if self.on_ground:
            self.coyote_timer = self.coyote_window
        elif was_on_ground:
            self.coyote_timer = self.coyote_window

        if self.player.top > self.play_rect.bottom + 120:
            self.game_over = True
            return

        remaining_coins: list[pygame.Rect] = []
        for coin in self.coins:
            if self.player.colliderect(coin):
                self.coins_collected += 1
                self.score += 100
            else:
                remaining_coins.append(coin)
        self.coins = remaining_coins

        if self.player.colliderect(self.exit_rect) and not self.coins:
            self.completed = True
            self.score += 250

    def draw_background(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        hill_back = [
            (self.play_rect.left, self.play_rect.bottom - 30),
            (self.play_rect.left + 160, self.play_rect.bottom - 130),
            (self.play_rect.left + 410, self.play_rect.bottom - 80),
            (self.play_rect.left + 620, self.play_rect.bottom - 180),
            (self.play_rect.left + 860, self.play_rect.bottom - 90),
            (self.play_rect.right, self.play_rect.bottom - 30),
        ]
        pygame.draw.polygon(screen, (48, 62, 78), hill_back)

    def draw_world(self, screen: pygame.Surface) -> None:
        for platform in self.platforms:
            pygame.draw.rect(screen, (88, 102, 126), platform, border_radius=8)

        for coin in self.coins:
            pygame.draw.circle(screen, theme.WARNING, coin.center, 9)
            pygame.draw.circle(screen, theme.TEXT, coin.center, 4)

        pygame.draw.rect(screen, theme.ACCENT, self.exit_rect, border_radius=10)
        pygame.draw.rect(screen, theme.TEXT, self.exit_rect.inflate(-22, -18), border_radius=6)

        pygame.draw.rect(screen, theme.TEXT, self.player, border_radius=8)
        eye_y = self.player.y + 16
        pygame.draw.circle(screen, theme.BACKGROUND, (self.player.x + 12, eye_y), 3)
        pygame.draw.circle(screen, theme.BACKGROUND, (self.player.right - 12, eye_y), 3)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        self.draw_background(screen)

        self.ui.draw_header(
            screen,
            "Platformer",
            "Move with Arrow Keys or WASD. Jump with Space / W / Up. Collect every coin, then reach the exit.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Coins: {self.coins_collected}/{self.total_coins}",
            ],
        )

        if self.completed:
            sub = "Every coin collected. Exit reached."
        elif self.game_over:
            sub = "You fell off the course."
        else:
            sub = "Use clean landings and keep your jump timing controlled."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        self.draw_world(screen)

        if self.paused and not self.completed and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Level Complete",
                f"Final Score: {self.score}",
                f"Coins Collected: {self.coins_collected}/{self.total_coins}",
            )
        elif self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Game Over",
                f"Final Score: {self.score}",
                f"Coins Collected: {self.coins_collected}/{self.total_coins}",
            )