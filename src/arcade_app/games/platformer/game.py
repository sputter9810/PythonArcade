from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class PlatformerGame(GameBase):
    game_id = "platformer"
    title = "Platformer"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1200, 620)

        self.player = pygame.Rect(0, 0, 42, 52)
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)

        self.move_speed = 300.0
        self.jump_strength = -640.0
        self.gravity = 1050.0
        self.max_fall_speed = 850.0

        self.on_ground = False

        # Responsiveness helpers
        self.jump_buffer_time = 0.12
        self.jump_buffer_timer = 0.0

        self.coyote_time = 0.10
        self.coyote_timer = 0.0

        self.platforms: list[pygame.Rect] = []
        self.coins: list[pygame.Rect] = []
        self.exit_door = pygame.Rect(0, 0, 50, 70)

        self.score = 0
        self.total_coins = 0
        self.is_won = False
        self.is_game_over = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1200) // 2,
            140,
            1200,
            620,
        )

    def build_level(self) -> None:
        floor_y = self.play_rect.bottom - 40

        self.platforms = [
            pygame.Rect(self.play_rect.left, floor_y, self.play_rect.width, 40),
            pygame.Rect(self.play_rect.left + 120, floor_y - 110, 180, 22),
            pygame.Rect(self.play_rect.left + 380, floor_y - 190, 170, 22),
            pygame.Rect(self.play_rect.left + 650, floor_y - 130, 180, 22),
            pygame.Rect(self.play_rect.left + 930, floor_y - 240, 170, 22),
            pygame.Rect(self.play_rect.left + 760, floor_y - 310, 130, 22),
            pygame.Rect(self.play_rect.left + 480, floor_y - 360, 140, 22),
            pygame.Rect(self.play_rect.left + 210, floor_y - 300, 120, 22),
        ]

        self.coins = [
            pygame.Rect(self.play_rect.left + 180, floor_y - 150, 18, 18),
            pygame.Rect(self.play_rect.left + 450, floor_y - 230, 18, 18),
            pygame.Rect(self.play_rect.left + 720, floor_y - 170, 18, 18),
            pygame.Rect(self.play_rect.left + 980, floor_y - 280, 18, 18),
            pygame.Rect(self.play_rect.left + 810, floor_y - 350, 18, 18),
            pygame.Rect(self.play_rect.left + 540, floor_y - 400, 18, 18),
            pygame.Rect(self.play_rect.left + 250, floor_y - 340, 18, 18),
        ]
        self.total_coins = len(self.coins)

        self.exit_door = pygame.Rect(
            self.play_rect.right - 90,
            floor_y - 70,
            50,
            70,
        )

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.build_level()

        self.player = pygame.Rect(
            self.play_rect.left + 40,
            self.play_rect.bottom - 120,
            42,
            52,
        )
        self.player_pos = pygame.Vector2(float(self.player.x), float(self.player.y))
        self.player_vel = pygame.Vector2(0, 0)

        self.on_ground = False
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0

        self.score = 0
        self.is_won = False
        self.is_game_over = False

    def request_jump(self) -> None:
        self.jump_buffer_timer = self.jump_buffer_time

    def perform_jump_if_possible(self) -> None:
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0 and not self.is_won and not self.is_game_over:
            self.player_vel.y = self.jump_strength
            self.on_ground = False
            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))
            elif event.key == pygame.K_F5:
                self.reset_game()
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.request_jump()

    def update_horizontal(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = 0.0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move += 1.0

        self.player_vel.x = move * self.move_speed
        self.player_pos.x += self.player_vel.x * dt
        self.player.x = round(self.player_pos.x)

        for platform in self.platforms:
            if self.player.colliderect(platform):
                if self.player_vel.x > 0:
                    self.player.right = platform.left
                elif self.player_vel.x < 0:
                    self.player.left = platform.right
                self.player_pos.x = float(self.player.x)

        if self.player.left < self.play_rect.left:
            self.player.left = self.play_rect.left
            self.player_pos.x = float(self.player.x)
        if self.player.right > self.play_rect.right:
            self.player.right = self.play_rect.right
            self.player_pos.x = float(self.player.x)

    def update_vertical(self, dt: float) -> None:
        was_on_ground = self.on_ground

        self.player_vel.y += self.gravity * dt
        if self.player_vel.y > self.max_fall_speed:
            self.player_vel.y = self.max_fall_speed

        self.player_pos.y += self.player_vel.y * dt
        self.player.y = round(self.player_pos.y)

        self.on_ground = False

        for platform in self.platforms:
            if self.player.colliderect(platform):
                if self.player_vel.y > 0:
                    self.player.bottom = platform.top
                    self.player_vel.y = 0
                    self.on_ground = True
                elif self.player_vel.y < 0:
                    self.player.top = platform.bottom
                    self.player_vel.y = 0
                self.player_pos.y = float(self.player.y)

        if self.on_ground:
            self.coyote_timer = self.coyote_time
        elif was_on_ground and not self.on_ground:
            self.coyote_timer = self.coyote_time

        if self.player.top > self.play_rect.bottom:
            self.is_game_over = True

    def collect_coins(self) -> None:
        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.coins.remove(coin)
                self.score += 100

    def check_win(self) -> None:
        if self.player.colliderect(self.exit_door) and not self.coins:
            self.is_won = True

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.is_won or self.is_game_over:
            return

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        if self.coyote_timer > 0:
            self.coyote_timer -= dt

        self.perform_jump_if_possible()
        self.update_horizontal(dt)
        self.update_vertical(dt)
        self.perform_jump_if_possible()

        self.collect_coins()
        self.check_win()

    def draw_platforms(self, screen: pygame.Surface) -> None:
        for platform in self.platforms:
            pygame.draw.rect(screen, theme.SURFACE_ALT, platform, border_radius=8)

    def draw_coins(self, screen: pygame.Surface) -> None:
        for coin in self.coins:
            pygame.draw.ellipse(screen, theme.WARNING, coin)

    def draw_exit(self, screen: pygame.Surface) -> None:
        door_color = theme.SUCCESS if not self.coins else theme.SURFACE_ALT
        pygame.draw.rect(screen, door_color, self.exit_door, border_radius=8)

        inner = self.exit_door.inflate(-18, -12)
        pygame.draw.rect(screen, theme.BACKGROUND, inner, border_radius=6)

    def draw_player(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, theme.ACCENT, self.player, border_radius=8)

        eye_y = self.player.y + 14
        pygame.draw.circle(screen, theme.TEXT, (self.player.x + 14, eye_y), 3)
        pygame.draw.circle(screen, theme.TEXT, (self.player.x + 28, eye_y), 3)

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Platformer", True, theme.TEXT)

        if self.is_won:
            status_text = "Level Complete!"
        elif self.is_game_over:
            status_text = "You fell! Game Over"
        else:
            status_text = "Collect all coins, then reach the exit"

        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        coins_left = self.info_font.render(
            f"Coins Left: {len(self.coins)}/{self.total_coins}",
            True,
            theme.TEXT,
        )
        controls = self.info_font.render(
            "Move: A/D or Left/Right  |  Jump: W/Up/Space  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        exit_hint = "Exit unlocked" if not self.coins else "Collect all coins to unlock exit"
        exit_hint_surface = self.small_font.render(exit_hint, True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 150, 110)))
        screen.blit(coins_left, coins_left.get_rect(center=(screen.get_width() // 2 + 150, 110)))
        screen.blit(exit_hint_surface, exit_hint_surface.get_rect(center=(screen.get_width() // 2, 134)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        ground = pygame.Rect(self.play_rect.left, self.play_rect.bottom - 40, self.play_rect.width, 40)
        pygame.draw.rect(screen, theme.SURFACE_ALT, ground)

        self.draw_platforms(screen)
        self.draw_coins(screen)
        self.draw_exit(screen)
        self.draw_player(screen)

        if self.is_won:
            win_text = self.title_font.render("Victory!", True, theme.TEXT)
            replay = self.info_font.render("Press F5 to play again", True, theme.MUTED_TEXT)
            screen.blit(win_text, win_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 18)))
            screen.blit(replay, replay.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 22)))

        if self.is_game_over:
            lose_text = self.title_font.render("Try Again", True, theme.TEXT)
            replay = self.info_font.render("Press F5 to restart", True, theme.MUTED_TEXT)
            screen.blit(lose_text, lose_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 18)))
            screen.blit(replay, replay.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 22)))