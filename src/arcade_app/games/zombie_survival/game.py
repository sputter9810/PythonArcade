from __future__ import annotations

import math
import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class ZombieSurvivalGame(GameBase):
    game_id = "zombie_survival"
    title = "Zombie Survival"

    PICKUP_HEAL = "heal"
    PICKUP_BOMB = "bomb"

    UPGRADE_FIRE_RATE = "fire_rate"
    UPGRADE_MOVE_SPEED = "move_speed"
    UPGRADE_PROJECTILE = "projectile"
    UPGRADE_BULLET_SIZE = "bullet_size"
    UPGRADE_MAX_HEALTH = "max_health"
    UPGRADE_AURA = "aura"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1080, 640)

        self.player_pos = pygame.Vector2(0, 0)
        self.player_radius = 18
        self.base_move_speed = 240.0
        self.move_speed_bonus = 0.0

        self.max_health = 3
        self.health = 3
        self.contact_cooldown = 0.0

        self.bullets: list[dict] = []
        self.zombies: list[dict] = []
        self.pickups: list[dict] = []
        self.xp_gems: list[dict] = []
        self.popups: list[dict] = []

        self.score = 0
        self.time_alive = 0.0
        self.stage = 1
        self.kills = 0

        self.spawn_timer = 0.0
        self.fire_timer = 0.0

        self.level = 1
        self.xp = 0
        self.xp_to_next = 8

        self.fire_rate_level = 0
        self.projectile_level = 0
        self.bullet_size_level = 0
        self.aura_level = 0

        self.upgrade_menu_active = False
        self.upgrade_choices: list[str] = []
        self.upgrade_buttons: list[pygame.Rect] = []

        self.paused = False
        self.completed = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.mode_font = pygame.font.SysFont("arial", 20, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1080) // 2, 165, 1080, 640)

        self.upgrade_buttons = [
            pygame.Rect(self.play_rect.centerx - 360, self.play_rect.centery - 40, 220, 120),
            pygame.Rect(self.play_rect.centerx - 110, self.play_rect.centery - 40, 220, 120),
            pygame.Rect(self.play_rect.centerx + 140, self.play_rect.centery - 40, 220, 120),
        ]

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.player_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)
        self.contact_cooldown = 0.0

        self.bullets.clear()
        self.zombies.clear()
        self.pickups.clear()
        self.xp_gems.clear()
        self.popups.clear()

        self.score = 0
        self.time_alive = 0.0
        self.stage = 1
        self.kills = 0

        self.spawn_timer = 0.5
        self.fire_timer = 0.0

        self.level = 1
        self.xp = 0
        self.xp_to_next = 8

        self.max_health = 3
        self.health = 3
        self.base_move_speed = 240.0
        self.move_speed_bonus = 0.0

        self.fire_rate_level = 0
        self.projectile_level = 0
        self.bullet_size_level = 0
        self.aura_level = 0

        self.upgrade_menu_active = False
        self.upgrade_choices = []

        self.paused = False
        self.completed = False

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = self.score
        payload["round"] = self.stage
        payload["hits"] = self.kills
        payload["accuracy"] = round((self.time_alive / max(1, self.kills)) * 10, 1)
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -34),
                "life": 0.7,
                "max_life": 0.7,
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

    def current_move_speed(self) -> float:
        return self.base_move_speed + self.move_speed_bonus

    def current_fire_delay(self) -> float:
        return max(0.12, 0.55 - self.fire_rate_level * 0.06)

    def current_bullet_radius(self) -> int:
        return 4 + self.bullet_size_level

    def current_projectile_count(self) -> int:
        return 1 + min(2, self.projectile_level)

    def current_aura_radius(self) -> float:
        return 0.0 if self.aura_level <= 0 else 48 + self.aura_level * 12

    def current_aura_tick_damage(self) -> float:
        return 0.0 if self.aura_level <= 0 else 0.8 + self.aura_level * 0.45

    def spawn_zombie(self) -> None:
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.top - 40)
        elif edge == "bottom":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.bottom + 40)
        elif edge == "left":
            pos = pygame.Vector2(self.play_rect.left - 40, random.randint(self.play_rect.top, self.play_rect.bottom))
        else:
            pos = pygame.Vector2(self.play_rect.right + 40, random.randint(self.play_rect.top, self.play_rect.bottom))

        elite_chance = min(0.05 + self.time_alive / 180.0, 0.22)
        elite = random.random() < elite_chance

        if elite:
            self.zombies.append(
                {
                    "pos": pos,
                    "radius": random.randint(24, 30),
                    "speed": random.uniform(65, 90) + self.stage * 2,
                    "hp": 4 + self.stage // 2,
                    "max_hp": 4 + self.stage // 2,
                    "elite": True,
                    "touch_damage": 1,
                    "xp": 3,
                }
            )
        else:
            self.zombies.append(
                {
                    "pos": pos,
                    "radius": random.randint(15, 22),
                    "speed": random.uniform(52, 82) + self.stage * 1.8,
                    "hp": 1 + self.stage // 5,
                    "max_hp": 1 + self.stage // 5,
                    "elite": False,
                    "touch_damage": 1,
                    "xp": 1,
                }
            )

    def spawn_xp_gem(self, pos: pygame.Vector2, amount: int) -> None:
        self.xp_gems.append(
            {
                "pos": pygame.Vector2(pos.x, pos.y),
                "radius": 8 if amount == 1 else 11,
                "amount": amount,
            }
        )

    def maybe_spawn_pickup(self, pos: pygame.Vector2, elite: bool) -> None:
        chance = 0.08 if not elite else 0.25
        if random.random() > chance:
            return

        kind = random.choice([self.PICKUP_HEAL, self.PICKUP_BOMB])
        color = theme.SUCCESS if kind == self.PICKUP_HEAL else theme.WARNING
        self.pickups.append(
            {
                "kind": kind,
                "pos": pygame.Vector2(pos.x, pos.y),
                "radius": 12,
                "color": color,
            }
        )

    def find_nearest_zombie(self) -> dict | None:
        if not self.zombies:
            return None
        return min(self.zombies, key=lambda z: z["pos"].distance_to(self.player_pos))

    def auto_fire(self) -> None:
        if self.fire_timer > 0 or self.completed or self.paused or self.upgrade_menu_active:
            return

        target = self.find_nearest_zombie()
        if target is None:
            return

        direction = target["pos"] - self.player_pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()

        projectile_count = self.current_projectile_count()
        spread = 0.28 if projectile_count > 1 else 0.0

        if projectile_count == 1:
            angles = [math.atan2(direction.y, direction.x)]
        elif projectile_count == 2:
            base = math.atan2(direction.y, direction.x)
            angles = [base - spread / 2, base + spread / 2]
        else:
            base = math.atan2(direction.y, direction.x)
            angles = [base - spread, base, base + spread]

        for angle in angles:
            vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * 520
            self.bullets.append(
                {
                    "pos": pygame.Vector2(self.player_pos.x, self.player_pos.y),
                    "vel": vel,
                    "life": 1.15,
                    "radius": self.current_bullet_radius(),
                    "damage": 1,
                }
            )

        self.fire_timer = self.current_fire_delay()

    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.28) + 2
            self.open_upgrade_menu()

    def open_upgrade_menu(self) -> None:
        pool = [
            self.UPGRADE_FIRE_RATE,
            self.UPGRADE_MOVE_SPEED,
            self.UPGRADE_PROJECTILE,
            self.UPGRADE_BULLET_SIZE,
            self.UPGRADE_MAX_HEALTH,
            self.UPGRADE_AURA,
        ]
        self.upgrade_choices = random.sample(pool, 3)
        self.upgrade_menu_active = True

    def apply_upgrade(self, upgrade: str) -> None:
        if upgrade == self.UPGRADE_FIRE_RATE:
            self.fire_rate_level += 1
            self.add_popup("FIRE RATE UP", (int(self.player_pos.x), int(self.player_pos.y)), theme.ACCENT)
        elif upgrade == self.UPGRADE_MOVE_SPEED:
            self.move_speed_bonus += 22.0
            self.add_popup("MOVE SPEED UP", (int(self.player_pos.x), int(self.player_pos.y)), theme.ACCENT)
        elif upgrade == self.UPGRADE_PROJECTILE:
            self.projectile_level += 1
            self.add_popup("EXTRA PROJECTILE", (int(self.player_pos.x), int(self.player_pos.y)), theme.WARNING)
        elif upgrade == self.UPGRADE_BULLET_SIZE:
            self.bullet_size_level += 1
            self.add_popup("BULLET SIZE UP", (int(self.player_pos.x), int(self.player_pos.y)), theme.WARNING)
        elif upgrade == self.UPGRADE_MAX_HEALTH:
            self.max_health += 1
            self.health = min(self.max_health, self.health + 1)
            self.add_popup("MAX HEALTH UP", (int(self.player_pos.x), int(self.player_pos.y)), theme.SUCCESS)
        elif upgrade == self.UPGRADE_AURA:
            self.aura_level += 1
            self.add_popup("AURA UP", (int(self.player_pos.x), int(self.player_pos.y)), theme.SUCCESS)

        self.upgrade_menu_active = False
        self.upgrade_choices = []

    def collect_pickup(self, pickup: dict) -> None:
        if pickup["kind"] == self.PICKUP_HEAL:
            self.health = min(self.max_health, self.health + 1)
            self.add_popup("+1 HP", (int(pickup["pos"].x), int(pickup["pos"].y)), theme.SUCCESS)
        else:
            killed = 0
            for zombie in self.zombies:
                zombie["hp"] = 0
                killed += 1
            if killed > 0:
                self.add_popup("BOMB", (int(pickup["pos"].x), int(pickup["pos"].y)), theme.WARNING)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.completed and not self.upgrade_menu_active:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.completed:
                    self.reset_game()
                    continue

                if self.upgrade_menu_active:
                    for i, rect in enumerate(self.upgrade_buttons):
                        if i < len(self.upgrade_choices) and rect.collidepoint(event.pos):
                            self.apply_upgrade(self.upgrade_choices[i])
                            return

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

        if self.paused or self.completed:
            return

        if self.upgrade_menu_active:
            return

        self.time_alive += dt
        self.score = self.kills * 100 + int(self.time_alive * 10)
        self.stage = 1 + int(self.time_alive // 20)

        if self.contact_cooldown > 0:
            self.contact_cooldown -= dt
        if self.fire_timer > 0:
            self.fire_timer -= dt

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()

        self.player_pos += move * self.current_move_speed() * dt
        self.player_pos.x = max(self.play_rect.left + self.player_radius, min(self.player_pos.x, self.play_rect.right - self.player_radius))
        self.player_pos.y = max(self.play_rect.top + self.player_radius, min(self.player_pos.y, self.play_rect.bottom - self.player_radius))

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            spawn_count = 1 + min(3, self.stage // 2)
            for _ in range(spawn_count):
                self.spawn_zombie()
            self.spawn_timer = max(0.16, 0.65 - self.time_alive * 0.008)

        self.auto_fire()

        for bullet in self.bullets:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt
        self.bullets = [
            b for b in self.bullets
            if b["life"] > 0 and self.play_rect.collidepoint(b["pos"].x, b["pos"].y)
        ]

        for zombie in self.zombies:
            direction = self.player_pos - zombie["pos"]
            if direction.length_squared() > 0:
                zombie["pos"] += direction.normalize() * zombie["speed"] * dt

        aura_radius = self.current_aura_radius()
        aura_damage = self.current_aura_tick_damage()

        for zombie in self.zombies:
            if aura_radius > 0 and zombie["pos"].distance_to(self.player_pos) <= aura_radius + zombie["radius"]:
                zombie["hp"] -= aura_damage * dt

        remaining_bullets: list[dict] = []
        for bullet in self.bullets:
            hit = None
            for zombie in self.zombies:
                if bullet["pos"].distance_to(zombie["pos"]) <= zombie["radius"] + bullet["radius"]:
                    hit = zombie
                    break

            if hit is not None:
                hit["hp"] -= bullet["damage"]
            else:
                remaining_bullets.append(bullet)
        self.bullets = remaining_bullets

        survivors: list[dict] = []
        for zombie in self.zombies:
            if zombie["hp"] <= 0:
                self.kills += 1
                reward = 180 if zombie["elite"] else 100
                self.score += reward
                self.add_popup(f"+{reward}", (int(zombie["pos"].x), int(zombie["pos"].y)), theme.ACCENT)
                self.spawn_xp_gem(zombie["pos"], zombie["xp"])
                self.maybe_spawn_pickup(zombie["pos"], zombie["elite"])
            else:
                survivors.append(zombie)
        self.zombies = survivors

        for gem in self.xp_gems[:]:
            if gem["pos"].distance_to(self.player_pos) <= self.player_radius + gem["radius"]:
                self.gain_xp(gem["amount"])
                self.xp_gems.remove(gem)

        for pickup in self.pickups[:]:
            if pickup["pos"].distance_to(self.player_pos) <= self.player_radius + pickup["radius"]:
                self.collect_pickup(pickup)
                self.pickups.remove(pickup)

        if self.contact_cooldown <= 0:
            for zombie in self.zombies:
                if zombie["pos"].distance_to(self.player_pos) <= zombie["radius"] + self.player_radius:
                    self.health -= zombie["touch_damage"]
                    self.contact_cooldown = 0.7
                    self.add_popup("-1 HP", (int(self.player_pos.x), int(self.player_pos.y)), theme.DANGER)
                    if self.health <= 0:
                        self.completed = True
                    break

    def draw_player(self, screen: pygame.Surface) -> None:
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse - self.player_pos
        angle = 0.0 if direction.length_squared() == 0 else math.atan2(direction.y, direction.x)

        nose = self.player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * 22
        left = self.player_pos + pygame.Vector2(math.cos(angle + 2.4), math.sin(angle + 2.4)) * 16
        right = self.player_pos + pygame.Vector2(math.cos(angle - 2.4), math.sin(angle - 2.4)) * 16

        pygame.draw.polygon(
            screen,
            theme.TEXT,
            [(int(nose.x), int(nose.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))],
        )

    def upgrade_name(self, upgrade: str) -> str:
        names = {
            self.UPGRADE_FIRE_RATE: "Fire Rate",
            self.UPGRADE_MOVE_SPEED: "Move Speed",
            self.UPGRADE_PROJECTILE: "Extra Projectile",
            self.UPGRADE_BULLET_SIZE: "Bullet Size",
            self.UPGRADE_MAX_HEALTH: "Max Health",
            self.UPGRADE_AURA: "Damage Aura",
        }
        return names.get(upgrade, upgrade)

    def upgrade_desc(self, upgrade: str) -> str:
        descriptions = {
            self.UPGRADE_FIRE_RATE: "Shoot more often.",
            self.UPGRADE_MOVE_SPEED: "Move faster around the arena.",
            self.UPGRADE_PROJECTILE: "Fire extra shots per burst.",
            self.UPGRADE_BULLET_SIZE: "Increase hit size.",
            self.UPGRADE_MAX_HEALTH: "Raise max HP and heal 1.",
            self.UPGRADE_AURA: "Damage nearby zombies over time.",
        }
        return descriptions.get(upgrade, "")

    def draw_upgrade_menu(self, screen: pygame.Surface) -> None:
        assert self.mode_font is not None

        overlay = pygame.Surface((self.play_rect.width, self.play_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, self.play_rect.topleft)

        title = self.mode_font.render("Choose an Upgrade", True, theme.TEXT)
        screen.blit(title, title.get_rect(center=(self.play_rect.centerx, self.play_rect.centery - 90)))

        for i, rect in enumerate(self.upgrade_buttons):
            if i >= len(self.upgrade_choices):
                continue
            upgrade = self.upgrade_choices[i]

            pygame.draw.rect(screen, theme.SURFACE, rect, border_radius=16)
            pygame.draw.rect(screen, theme.ACCENT, rect, width=2, border_radius=16)

            name_surface = self.mode_font.render(self.upgrade_name(upgrade), True, theme.TEXT)
            desc_surface = pygame.font.SysFont("arial", 16).render(self.upgrade_desc(upgrade), True, theme.MUTED_TEXT)

            screen.blit(name_surface, name_surface.get_rect(center=(rect.centerx, rect.y + 36)))
            screen.blit(desc_surface, desc_surface.get_rect(center=(rect.centerx, rect.y + 76)))

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        xp_text = f"XP: {self.xp}/{self.xp_to_next}"
        self.ui.draw_header(
            screen,
            "Zombie Survival",
            "Auto-fire survivor-lite. Kite the horde, collect XP, and build your run.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"HP: {self.health}/{self.max_health}",
                f"Kills: {self.kills}",
                f"Level: {self.level}",
                xp_text,
            ],
        )
        sub = "Survive, level up, and shape your build." if not self.completed else "Survival run ended."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "WASD / Arrows: Move  |  Auto-Fire  |  P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        aura_radius = self.current_aura_radius()
        if aura_radius > 0:
            pygame.draw.circle(
                screen,
                (80, 200, 140),
                (int(self.player_pos.x), int(self.player_pos.y)),
                int(aura_radius),
                width=2,
            )

        for zombie in self.zombies:
            color = theme.WARNING if zombie["elite"] else theme.DANGER
            pygame.draw.circle(screen, color, (int(zombie["pos"].x), int(zombie["pos"].y)), zombie["radius"])

            if zombie["elite"]:
                bar_width = zombie["radius"] * 2
                bar_rect = pygame.Rect(int(zombie["pos"].x - zombie["radius"]), int(zombie["pos"].y - zombie["radius"] - 10), bar_width, 5)
                fill_width = int(bar_width * (zombie["hp"] / zombie["max_hp"]))
                pygame.draw.rect(screen, theme.SURFACE_ALT, bar_rect, border_radius=3)
                pygame.draw.rect(screen, theme.SUCCESS, (bar_rect.x, bar_rect.y, fill_width, bar_rect.height), border_radius=3)

        for gem in self.xp_gems:
            pygame.draw.circle(screen, theme.ACCENT, (int(gem["pos"].x), int(gem["pos"].y)), gem["radius"])

        for pickup in self.pickups:
            pygame.draw.circle(screen, pickup["color"], (int(pickup["pos"].x), int(pickup["pos"].y)), pickup["radius"])
            pygame.draw.circle(screen, theme.BACKGROUND, (int(pickup["pos"].x), int(pickup["pos"].y)), 5)

        bullet_color = theme.WARNING if self.projectile_level > 0 else theme.ACCENT
        for bullet in self.bullets:
            pygame.draw.circle(screen, bullet_color, (int(bullet["pos"].x), int(bullet["pos"].y)), bullet["radius"])

        self.draw_player(screen)
        self.ui.draw_floating_texts(screen, self.popups)

        if self.upgrade_menu_active:
            self.draw_upgrade_menu(screen)
        elif self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Survival Over",
                f"Score: {self.score}",
                f"Kills: {self.kills}  |  Time: {self.time_alive:0.1f}s  |  Level: {self.level}",
            )