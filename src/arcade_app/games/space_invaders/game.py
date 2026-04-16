from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class SpaceInvadersGame(GameBase):
    game_id = "space_invaders"
    title = "Space Invaders"

    POWERUP_RAPID_FIRE = "rapid_fire"
    POWERUP_SHIELD = "shield"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 1100, 640)

        self.player = pygame.Rect(0, 0, 70, 24)
        self.player_speed = 460.0

        self.player_bullets: list[pygame.Rect] = []
        self.enemy_bullets: list[pygame.Rect] = []
        self.invaders: list[pygame.Rect] = []
        self.powerups: list[dict] = []
        self.popups: list[dict] = []

        self.score = 0
        self.lives = 3
        self.wave = 1

        self.invader_direction = 1
        self.invader_speed = 32.0
        self.invader_drop = 18
        self.invader_move_timer = 0.0
        self.invader_move_delay = 0.45

        self.player_shot_cooldown = 0.0
        self.enemy_shot_timer = 0.0

        self.rapid_fire_timer = 0.0
        self.shield_timer = 0.0

        self.game_over = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            165,
            1100,
            640,
        )

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.score = 0
        self.lives = 3
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.powerups.clear()
        self.popups.clear()

        self.player = pygame.Rect(
            self.play_rect.centerx - 35,
            self.play_rect.bottom - 40,
            70,
            24,
        )

        self.player_shot_cooldown = 0.0
        self.enemy_shot_timer = 1.0
        self.invader_direction = 1
        self.rapid_fire_timer = 0.0
        self.shield_timer = 0.0

        self.spawn_wave()

    def spawn_wave(self) -> None:
        self.invaders.clear()

        rows = 5
        cols = 9
        invader_w = 52
        invader_h = 32
        gap_x = 18
        gap_y = 16

        start_x = self.play_rect.left + 120
        start_y = self.play_rect.top + 70

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (invader_w + gap_x)
                y = start_y + row * (invader_h + gap_y)
                self.invaders.append(pygame.Rect(x, y, invader_w, invader_h))

        self.invader_speed = 32.0 + self.wave * 6
        self.invader_move_delay = max(0.12, 0.45 - self.wave * 0.03)

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -34),
                "life": 0.6,
                "max_life": 0.6,
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

    def maybe_spawn_powerup(self, invader: pygame.Rect) -> None:
        if random.random() > 0.12:
            return

        kind = random.choice([self.POWERUP_RAPID_FIRE, self.POWERUP_SHIELD])
        color = theme.ACCENT if kind == self.POWERUP_RAPID_FIRE else theme.WARNING

        self.powerups.append(
            {
                "kind": kind,
                "rect": pygame.Rect(invader.centerx - 12, invader.centery - 12, 24, 24),
                "color": color,
            }
        )

    def fire_player_bullet(self) -> None:
        if self.player_shot_cooldown > 0 or self.game_over or self.paused:
            return

        bullet = pygame.Rect(self.player.centerx - 3, self.player.top - 14, 6, 14)
        self.player_bullets.append(bullet)
        self.player_shot_cooldown = 0.08 if self.rapid_fire_timer > 0 else 0.24

    def fire_enemy_bullet(self) -> None:
        if not self.invaders:
            return

        columns: dict[int, pygame.Rect] = {}
        for invader in self.invaders:
            columns[invader.centerx] = max(columns.get(invader.centerx, invader), invader, key=lambda r: r.y)

        shooter = random.choice(list(columns.values()))
        bullet = pygame.Rect(shooter.centerx - 3, shooter.bottom + 4, 6, 14)
        self.enemy_bullets.append(bullet)

    def collect_powerup(self, powerup: dict) -> None:
        if powerup["kind"] == self.POWERUP_RAPID_FIRE:
            self.rapid_fire_timer = 8.0
            self.add_popup("RAPID FIRE", powerup["rect"].center, theme.ACCENT)
        else:
            self.shield_timer = 8.0
            self.add_popup("SHIELD", powerup["rect"].center, theme.WARNING)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.fire_player_bullet()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()
                else:
                    self.fire_player_bullet()

    def update_invaders(self, dt: float) -> None:
        self.invader_move_timer += dt
        if self.invader_move_timer < self.invader_move_delay:
            return

        self.invader_move_timer = 0.0
        move_x = int(self.invader_direction * self.invader_speed)

        touching_edge = False
        for invader in self.invaders:
            next_left = invader.left + move_x
            next_right = invader.right + move_x
            if next_left <= self.play_rect.left + 20 or next_right >= self.play_rect.right - 20:
                touching_edge = True
                break

        if touching_edge:
            self.invader_direction *= -1
            for invader in self.invaders:
                invader.y += self.invader_drop
        else:
            for invader in self.invaders:
                invader.x += move_x

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

        if self.paused:
            return

        if self.game_over:
            return

        if self.player_shot_cooldown > 0:
            self.player_shot_cooldown -= dt
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
        if self.shield_timer > 0:
            self.shield_timer -= dt

        keys = pygame.key.get_pressed()
        move = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1.0

        self.player.x += int(move * self.player_speed * dt)
        self.player.x = max(self.play_rect.left + 10, min(self.player.x, self.play_rect.right - 10 - self.player.width))

        self.update_invaders(dt)

        for bullet in self.player_bullets:
            bullet.y -= int(520 * dt)
        for bullet in self.enemy_bullets:
            bullet.y += int((240 + self.wave * 10) * dt)
        for powerup in self.powerups:
            powerup["rect"].y += int(130 * dt)

        self.player_bullets = [b for b in self.player_bullets if b.bottom > self.play_rect.top]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.top < self.play_rect.bottom]
        self.powerups = [p for p in self.powerups if p["rect"].top < self.play_rect.bottom]

        remaining_bullets: list[pygame.Rect] = []
        remaining_invaders = self.invaders.copy()

        for bullet in self.player_bullets:
            hit = None
            for invader in remaining_invaders:
                if bullet.colliderect(invader):
                    hit = invader
                    break

            if hit is not None:
                remaining_invaders.remove(hit)
                reward = 50
                self.score += reward
                self.add_popup(f"+{reward}", hit.center, theme.ACCENT)
                self.maybe_spawn_powerup(hit)
            else:
                remaining_bullets.append(bullet)

        self.player_bullets = remaining_bullets
        self.invaders = remaining_invaders

        for powerup in self.powerups[:]:
            if powerup["rect"].colliderect(self.player):
                self.collect_powerup(powerup)
                self.powerups.remove(powerup)

        for bullet in self.enemy_bullets[:]:
            if bullet.colliderect(self.player):
                self.enemy_bullets.remove(bullet)
                if self.shield_timer > 0:
                    self.shield_timer = 0.0
                    self.add_popup("SHIELD BROKE", self.player.center, theme.WARNING)
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                break

        for invader in self.invaders:
            if invader.bottom >= self.player.top:
                self.game_over = True
                break

        self.enemy_shot_timer -= dt
        if self.enemy_shot_timer <= 0:
            self.fire_enemy_bullet()
            self.enemy_shot_timer = max(0.22, 1.1 - self.wave * 0.08)

        if not self.invaders and not self.game_over:
            self.wave += 1
            self.spawn_wave()

    def draw_invader(self, screen: pygame.Surface, invader: pygame.Rect) -> None:
        pygame.draw.rect(screen, theme.ACCENT, invader, border_radius=8)
        eye_y = invader.top + 10
        pygame.draw.circle(screen, theme.BACKGROUND, (invader.left + 14, eye_y), 3)
        pygame.draw.circle(screen, theme.BACKGROUND, (invader.right - 14, eye_y), 3)

    def draw_powerup(self, screen: pygame.Surface, powerup: dict) -> None:
        rect = powerup["rect"]
        pygame.draw.rect(screen, powerup["color"], rect, border_radius=6)
        inner = rect.inflate(-8, -8)
        pygame.draw.rect(screen, theme.BACKGROUND, inner, border_radius=4)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Space Invaders",
            "Move with A/D or Left/Right. Fire with Space or Click. Clear each wave.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Lives: {self.lives}",
                f"Wave: {self.wave}",
                f"Rapid: {'ON' if self.rapid_fire_timer > 0 else 'OFF'}",
                f"Shield: {'ON' if self.shield_timer > 0 else 'OFF'}",
            ],
        )
        self.ui.draw_sub_stats(screen, "Powerups: blue = rapid fire, yellow = shield.")
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for invader in self.invaders:
            self.draw_invader(screen, invader)

        for powerup in self.powerups:
            self.draw_powerup(screen, powerup)

        player_color = theme.WARNING if self.shield_timer > 0 else theme.TEXT
        pygame.draw.rect(screen, player_color, self.player, border_radius=8)

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, theme.ACCENT, bullet, border_radius=4)
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, theme.DANGER, bullet, border_radius=4)

        self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Game Over",
                f"Final Score: {self.score}",
                f"Final Wave: {self.wave}",
            )