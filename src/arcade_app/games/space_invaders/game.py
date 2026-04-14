from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class SpaceInvadersGame(GameBase):
    game_id = "space_invaders"
    title = "Space Invaders"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 620)

        self.player = pygame.Rect(0, 0, 70, 24)
        self.player_speed = 520.0

        self.player_bullets: list[dict] = []
        self.enemy_bullets: list[pygame.Rect] = []
        self.powerups: list[dict] = []

        self.enemies: list[pygame.Rect] = []
        self.enemy_direction = 1
        self.enemy_speed = 40.0
        self.enemy_drop_distance = 18
        self.enemy_shot_timer = 0.0
        self.enemy_shot_delay = 0.9

        self.player_bullet_speed = 620.0
        self.enemy_bullet_speed = 300.0
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.28

        self.active_powerup: str | None = None
        self.powerup_timer = 0.0

        self.score = 0
        self.lives = 3
        self.wave = 1
        self.is_game_over = False
        self.is_won = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            140,
            1100,
            620,
        )

    def reset_player(self) -> None:
        self.player = pygame.Rect(
            self.play_rect.centerx - 35,
            self.play_rect.bottom - 45,
            70,
            24,
        )

    def build_enemy_wave(self) -> None:
        self.enemies.clear()

        rows = 4
        cols = 8
        enemy_width = 54
        enemy_height = 32
        gap_x = 26
        gap_y = 22

        formation_width = cols * enemy_width + (cols - 1) * gap_x
        start_x = self.play_rect.centerx - formation_width // 2
        start_y = self.play_rect.y + 60

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (enemy_width + gap_x)
                y = start_y + row * (enemy_height + gap_y)
                self.enemies.append(pygame.Rect(x, y, enemy_width, enemy_height))

        self.enemy_direction = 1

    def reset_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.is_game_over = False
        self.is_won = False

        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.powerups.clear()
        self.active_powerup = None
        self.powerup_timer = 0.0

        self.shoot_cooldown = 0.0
        self.enemy_shot_timer = 0.0
        self.enemy_speed = 40.0

        self.reset_player()
        self.build_enemy_wave()

    def start_next_wave(self) -> None:
        self.wave += 1
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.powerups.clear()
        self.build_enemy_wave()
        self.enemy_speed += 12.0

    def spawn_powerup(self, x: int, y: int) -> None:
        if random.random() > 0.18:
            return

        powerup_type = random.choice(["rapid", "triple", "laser"])
        rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.powerups.append({"type": powerup_type, "rect": rect, "speed": 160.0})

    def fire_player_bullet(self) -> None:
        if self.active_powerup == "triple":
            for offset in (-20, 0, 20):
                bullet = {
                    "rect": pygame.Rect(self.player.centerx - 3 + offset, self.player.top - 16, 6, 16),
                    "speed": self.player_bullet_speed,
                    "piercing": False,
                }
                self.player_bullets.append(bullet)
            return

        if self.active_powerup == "laser":
            bullet = {
                "rect": pygame.Rect(self.player.centerx - 5, self.player.top - 34, 10, 34),
                "speed": self.player_bullet_speed + 220.0,
                "piercing": True,
            }
            self.player_bullets.append(bullet)
            return

        bullet = {
            "rect": pygame.Rect(self.player.centerx - 3, self.player.top - 16, 6, 16),
            "speed": self.player_bullet_speed,
            "piercing": False,
        }
        self.player_bullets.append(bullet)

    def fire_enemy_bullet(self) -> None:
        if not self.enemies:
            return

        shooters_by_col: dict[int, pygame.Rect] = {}
        for enemy in self.enemies:
            col_key = enemy.centerx
            if col_key not in shooters_by_col or enemy.y > shooters_by_col[col_key].y:
                shooters_by_col[col_key] = enemy

        shooter = random.choice(list(shooters_by_col.values()))
        bullet = pygame.Rect(shooter.centerx - 3, shooter.bottom + 6, 6, 16)
        self.enemy_bullets.append(bullet)

    def apply_powerup(self, powerup_type: str) -> None:
        self.active_powerup = powerup_type
        self.powerup_timer = 8.0

        if powerup_type == "rapid":
            self.shoot_delay = 0.12
        else:
            self.shoot_delay = 0.28

    def clear_powerup(self) -> None:
        self.active_powerup = None
        self.powerup_timer = 0.0
        self.shoot_delay = 0.28

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))
            elif event.key == pygame.K_F5:
                self.reset_game()
            elif event.key == pygame.K_SPACE:
                if not self.is_game_over and not self.is_won and self.shoot_cooldown <= 0:
                    self.fire_player_bullet()
                    self.shoot_cooldown = self.shoot_delay

    def update_player(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        move = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1.0

        self.player.x += int(move * self.player_speed * dt)

        if self.player.left < self.play_rect.left:
            self.player.left = self.play_rect.left
        if self.player.right > self.play_rect.right:
            self.player.right = self.play_rect.right

    def update_player_bullets(self, dt: float) -> None:
        for bullet in self.player_bullets[:]:
            bullet["rect"].y -= int(bullet["speed"] * dt)

            if bullet["rect"].bottom < self.play_rect.top:
                self.player_bullets.remove(bullet)
                continue

            hit_enemies = [enemy for enemy in self.enemies if bullet["rect"].colliderect(enemy)]
            if not hit_enemies:
                continue

            for hit_enemy in hit_enemies:
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                    self.score += 100
                    self.spawn_powerup(hit_enemy.centerx, hit_enemy.centery)

            if not bullet["piercing"] and bullet in self.player_bullets:
                self.player_bullets.remove(bullet)

    def update_enemy_bullets(self, dt: float) -> None:
        for bullet in self.enemy_bullets[:]:
            bullet.y += int(self.enemy_bullet_speed * dt)

            if bullet.top > self.play_rect.bottom:
                self.enemy_bullets.remove(bullet)
                continue

            if bullet.colliderect(self.player):
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                self.lives -= 1

                if self.lives <= 0:
                    self.is_game_over = True
                else:
                    self.reset_player()
                    self.player_bullets.clear()
                    self.enemy_bullets.clear()
                return

    def update_powerups(self, dt: float) -> None:
        for powerup in self.powerups[:]:
            powerup["rect"].y += int(powerup["speed"] * dt)

            if powerup["rect"].top > self.play_rect.bottom:
                self.powerups.remove(powerup)
                continue

            if powerup["rect"].colliderect(self.player):
                self.apply_powerup(powerup["type"])
                self.powerups.remove(powerup)

        if self.active_powerup is not None:
            self.powerup_timer -= dt
            if self.powerup_timer <= 0:
                self.clear_powerup()

    def update_enemies(self, dt: float) -> None:
        if not self.enemies:
            self.start_next_wave()
            return

        move_x = int(self.enemy_speed * self.enemy_direction * dt)
        reached_edge = False

        for enemy in self.enemies:
            enemy.x += move_x
            if enemy.right >= self.play_rect.right - 10 or enemy.left <= self.play_rect.left + 10:
                reached_edge = True

        if reached_edge:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy.y += self.enemy_drop_distance

        for enemy in self.enemies:
            if enemy.bottom >= self.player.top:
                self.is_game_over = True
                return

    def update_enemy_shooting(self, dt: float) -> None:
        self.enemy_shot_timer += dt
        if self.enemy_shot_timer >= self.enemy_shot_delay:
            self.enemy_shot_timer = 0.0
            self.fire_enemy_bullet()

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if self.is_game_over or self.is_won:
            return

        self.update_player(dt)
        self.update_player_bullets(dt)
        self.update_enemy_bullets(dt)
        self.update_powerups(dt)
        self.update_enemies(dt)
        self.update_enemy_shooting(dt)

        if self.wave >= 5 and not self.enemies:
            self.is_won = True

    def draw_player(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, theme.SUCCESS, self.player, border_radius=8)
        turret = pygame.Rect(self.player.centerx - 7, self.player.top - 10, 14, 12)
        pygame.draw.rect(screen, theme.SUCCESS, turret, border_radius=4)

    def draw_enemy(self, screen: pygame.Surface, enemy: pygame.Rect) -> None:
        pygame.draw.rect(screen, theme.DANGER, enemy, border_radius=8)

        eye1 = pygame.Rect(enemy.x + 12, enemy.y + 10, 8, 8)
        eye2 = pygame.Rect(enemy.right - 20, enemy.y + 10, 8, 8)
        pygame.draw.rect(screen, theme.TEXT, eye1, border_radius=2)
        pygame.draw.rect(screen, theme.TEXT, eye2, border_radius=2)

    def draw_powerup(self, screen: pygame.Surface, powerup: dict) -> None:
        rect = powerup["rect"]
        ptype = powerup["type"]

        color = {
            "rapid": theme.WARNING,
            "triple": theme.ACCENT,
            "laser": theme.SUCCESS,
        }[ptype]

        pygame.draw.rect(screen, color, rect, border_radius=6)

        assert self.small_font is not None
        label_map = {"rapid": "R", "triple": "T", "laser": "L"}
        label = self.small_font.render(label_map[ptype], True, theme.TEXT)
        screen.blit(label, label.get_rect(center=rect.center))

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Space Invaders", True, theme.TEXT)

        if self.is_won:
            status_text = "You defeated the invasion!"
        elif self.is_game_over:
            status_text = "Game Over"
        else:
            status_text = "Defend the base"

        status = self.info_font.render(status_text, True, theme.TEXT)
        score = self.info_font.render(f"Score: {self.score}", True, theme.TEXT)
        lives = self.info_font.render(f"Lives: {self.lives}", True, theme.TEXT)
        wave = self.info_font.render(f"Wave: {self.wave}", True, theme.TEXT)

        if self.active_powerup is None:
            powerup_text = "Powerup: None"
        else:
            powerup_text = f"Powerup: {self.active_powerup.title()} ({self.powerup_timer:0.1f}s)"
        powerup_surface = self.small_font.render(powerup_text, True, theme.MUTED_TEXT)

        controls = self.info_font.render(
            "Move: Arrow Keys / A,D  |  Space: Shoot  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 75)))
        screen.blit(score, score.get_rect(center=(screen.get_width() // 2 - 180, 110)))
        screen.blit(lives, lives.get_rect(center=(screen.get_width() // 2, 110)))
        screen.blit(wave, wave.get_rect(center=(screen.get_width() // 2 + 180, 110)))
        screen.blit(powerup_surface, powerup_surface.get_rect(center=(screen.get_width() // 2, 134)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)

        for enemy in self.enemies:
            self.draw_enemy(screen, enemy)

        for bullet in self.player_bullets:
            color = theme.SUCCESS if bullet["piercing"] else theme.ACCENT
            pygame.draw.rect(screen, color, bullet["rect"], border_radius=3)

        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, theme.WARNING, bullet, border_radius=3)

        for powerup in self.powerups:
            self.draw_powerup(screen, powerup)

        self.draw_player(screen)