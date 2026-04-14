from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class TimeAttackChallengeGame(GameBase):
    game_id = "time_attack_challenge"
    title = "Time Attack Challenge"

    SESSION_LENGTH = 45.0
    PLAYER_SPEED = 340.0
    PLAYER_RADIUS = 18

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.big_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 980, 640)

        self.player_pos = pygame.Vector2(0, 0)
        self.pickups: list[dict] = []
        self.hazards: list[dict] = []
        self.particles: list[dict] = []

        self.time_left = self.SESSION_LENGTH
        self.score = 0
        self.pickups_collected = 0
        self.hits_taken = 0
        self.combo = 0
        self.best_combo = 0

        self.game_over = False

        self.pickup_spawn_timer = 0.0
        self.hazard_spawn_timer = 0.0
        self.combo_timer = 0.0
        self.flash_timer = 0.0

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

        self.player_pos = pygame.Vector2(self.play_rect.centerx, self.play_rect.centery)

        self.pickups = []
        self.hazards = []
        self.particles = []

        self.time_left = self.SESSION_LENGTH
        self.score = 0
        self.pickups_collected = 0
        self.hits_taken = 0
        self.combo = 0
        self.best_combo = 0

        self.game_over = False

        self.pickup_spawn_timer = 0.0
        self.hazard_spawn_timer = 1.2
        self.combo_timer = 0.0
        self.flash_timer = 0.0

        for _ in range(4):
            self.spawn_pickup()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(0, 0, 980, 640)
        self.play_rect.centerx = screen.get_width() // 2
        self.play_rect.top = 150

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = self.pickups_collected
        payload["accuracy"] = round(self.collection_accuracy(), 1)
        payload["round"] = self.best_combo
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def collection_accuracy(self) -> float:
        total = self.pickups_collected + self.hits_taken
        if total == 0:
            return 100.0
        return (self.pickups_collected / total) * 100.0

    def random_arena_position(self, margin: int = 34) -> pygame.Vector2:
        return pygame.Vector2(
            random.randint(self.play_rect.left + margin, self.play_rect.right - margin),
            random.randint(self.play_rect.top + margin, self.play_rect.bottom - margin),
        )

    def spawn_pickup(self) -> None:
        pos = self.random_arena_position()
        self.pickups.append(
            {
                "pos": pos,
                "radius": random.randint(10, 15),
                "value": random.choice([80, 100, 120]),
                "pulse": random.uniform(0, 3.14),
            }
        )

    def spawn_hazard(self) -> None:
        edge = random.choice(["top", "bottom", "left", "right"])
        size = random.randint(18, 34)
        speed = 150 + (self.SESSION_LENGTH - self.time_left) * 4.8

        if edge == "top":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.top - size)
            vel = pygame.Vector2(random.uniform(-40, 40), random.uniform(1.0, 1.5) * speed)
        elif edge == "bottom":
            pos = pygame.Vector2(random.randint(self.play_rect.left, self.play_rect.right), self.play_rect.bottom + size)
            vel = pygame.Vector2(random.uniform(-40, 40), -random.uniform(1.0, 1.5) * speed)
        elif edge == "left":
            pos = pygame.Vector2(self.play_rect.left - size, random.randint(self.play_rect.top, self.play_rect.bottom))
            vel = pygame.Vector2(random.uniform(1.0, 1.5) * speed, random.uniform(-40, 40))
        else:
            pos = pygame.Vector2(self.play_rect.right + size, random.randint(self.play_rect.top, self.play_rect.bottom))
            vel = pygame.Vector2(-random.uniform(1.0, 1.5) * speed, random.uniform(-40, 40))

        self.hazards.append(
            {
                "pos": pos,
                "vel": vel,
                "radius": size,
                "hit_cooldown": 0.0,
            }
        )

    def add_particles(self, pos: pygame.Vector2, color: tuple[int, int, int], count: int) -> None:
        for _ in range(count):
            vel = pygame.Vector2(random.uniform(-180, 180), random.uniform(-180, 180))
            self.particles.append(
                {
                    "pos": pygame.Vector2(pos.x, pos.y),
                    "vel": vel,
                    "life": random.uniform(0.25, 0.55),
                    "radius": random.randint(2, 5),
                    "color": color,
                }
            )

    def update_player(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize()

        self.player_pos += move * self.PLAYER_SPEED * dt
        self.player_pos.x = max(self.play_rect.left + self.PLAYER_RADIUS, min(self.player_pos.x, self.play_rect.right - self.PLAYER_RADIUS))
        self.player_pos.y = max(self.play_rect.top + self.PLAYER_RADIUS, min(self.player_pos.y, self.play_rect.bottom - self.PLAYER_RADIUS))

    def update_pickups(self, dt: float) -> None:
        updated_pickups: list[dict] = []
        player_radius = self.PLAYER_RADIUS

        for pickup in self.pickups:
            pickup["pulse"] += dt * 4.0
            distance = self.player_pos.distance_to(pickup["pos"])
            if distance <= player_radius + pickup["radius"]:
                self.pickups_collected += 1
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                self.combo_timer = 2.0

                combo_bonus = min(200, self.combo * 14)
                self.score += pickup["value"] + combo_bonus
                self.add_particles(pickup["pos"], theme.ACCENT, 12)
            else:
                updated_pickups.append(pickup)

        self.pickups = updated_pickups

        while len(self.pickups) < 4:
            self.spawn_pickup()

    def update_hazards(self, dt: float) -> None:
        updated_hazards: list[dict] = []

        for hazard in self.hazards:
            hazard["pos"] += hazard["vel"] * dt
            if hazard["hit_cooldown"] > 0:
                hazard["hit_cooldown"] -= dt

            distance = self.player_pos.distance_to(hazard["pos"])
            if distance <= self.PLAYER_RADIUS + hazard["radius"] and hazard["hit_cooldown"] <= 0:
                hazard["hit_cooldown"] = 0.45
                self.hits_taken += 1
                self.combo = 0
                self.combo_timer = 0.0
                self.score = max(0, self.score - 140)
                self.flash_timer = 0.18
                self.add_particles(hazard["pos"], theme.DANGER, 14)

            still_visible = (
                self.play_rect.left - 80 <= hazard["pos"].x <= self.play_rect.right + 80
                and self.play_rect.top - 80 <= hazard["pos"].y <= self.play_rect.bottom + 80
            )
            if still_visible:
                updated_hazards.append(hazard)

        self.hazards = updated_hazards

    def update_particles(self, dt: float) -> None:
        updated_particles: list[dict] = []
        for particle in self.particles:
            particle["life"] -= dt
            if particle["life"] <= 0:
                continue
            particle["pos"] += particle["vel"] * dt
            particle["vel"] *= 0.94
            updated_particles.append(particle)
        self.particles = updated_particles

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_particles(dt)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.game_over:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self.game_over = True
            return

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        self.pickup_spawn_timer -= dt
        if self.pickup_spawn_timer <= 0:
            self.spawn_pickup()
            self.pickup_spawn_timer = random.uniform(0.9, 1.5)

        self.hazard_spawn_timer -= dt
        if self.hazard_spawn_timer <= 0:
            self.spawn_hazard()
            difficulty_progress = 1.0 - (self.time_left / self.SESSION_LENGTH)
            self.hazard_spawn_timer = max(0.28, 1.1 - difficulty_progress * 0.72)

        self.update_player(dt)
        self.update_pickups(dt)
        self.update_hazards(dt)

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

        panel_color = theme.SURFACE_ALT if self.flash_timer > 0 else theme.SURFACE
        pygame.draw.rect(screen, panel_color, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        grid_gap = 48
        for x in range(self.play_rect.left + 20, self.play_rect.right, grid_gap):
            pygame.draw.line(screen, theme.BACKGROUND, (x, self.play_rect.top + 10), (x, self.play_rect.bottom - 10), 1)
        for y in range(self.play_rect.top + 10, self.play_rect.bottom, grid_gap):
            pygame.draw.line(screen, theme.BACKGROUND, (self.play_rect.left + 10, y), (self.play_rect.right - 10, y), 1)

    def draw_pickups(self, screen: pygame.Surface) -> None:
        for pickup in self.pickups:
            pulse_scale = 1.0 + 0.10 * __import__("math").sin(pickup["pulse"])
            radius = int(pickup["radius"] * pulse_scale)
            pygame.draw.circle(screen, theme.ACCENT, (int(pickup["pos"].x), int(pickup["pos"].y)), radius)
            pygame.draw.circle(screen, theme.TEXT, (int(pickup["pos"].x), int(pickup["pos"].y)), max(4, radius // 3))

    def draw_hazards(self, screen: pygame.Surface) -> None:
        for hazard in self.hazards:
            pos = (int(hazard["pos"].x), int(hazard["pos"].y))
            pygame.draw.circle(screen, theme.DANGER, pos, hazard["radius"])
            pygame.draw.circle(screen, theme.WARNING, pos, max(5, hazard["radius"] // 3))

    def draw_player(self, screen: pygame.Surface) -> None:
        pos = (int(self.player_pos.x), int(self.player_pos.y))
        pygame.draw.circle(screen, theme.TEXT, pos, self.PLAYER_RADIUS + 5)
        pygame.draw.circle(screen, theme.ACCENT, pos, self.PLAYER_RADIUS)
        pygame.draw.circle(screen, theme.BACKGROUND, pos, 6)

    def draw_particles(self, screen: pygame.Surface) -> None:
        for particle in self.particles:
            pygame.draw.circle(
                screen,
                particle["color"],
                (int(particle["pos"].x), int(particle["pos"].y)),
                particle["radius"],
            )

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        title = self.title_font.render("Time Attack Challenge", True, theme.TEXT)
        subtitle = self.small_font.render(
            "Move with Arrow Keys or WASD. Grab green pickups, avoid red hazards. F5 restart, Esc back.",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 40)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 74)))

        stats = [
            f"Score: {self.score}",
            f"Pickups: {self.pickups_collected}",
            f"Combo: {self.combo}",
            f"Accuracy: {self.collection_accuracy():0.1f}%",
            f"Time: {self.time_left:0.1f}s",
        ]
        start_x = screen.get_width() // 2 - 360
        gap = 180
        for index, stat in enumerate(stats):
            surface = self.info_font.render(stat, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=(start_x + index * gap, 112)))

        detail = self.small_font.render(
            f"Hits Taken: {self.hits_taken}  |  Best Combo: {self.best_combo}",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(detail, detail.get_rect(center=(screen.get_width() // 2, 138)))

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.big_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        panel = pygame.Rect(0, 0, 600, 240)
        panel.center = self.play_rect.center

        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        screen.blit(overlay, panel.topleft)
        pygame.draw.rect(screen, theme.ACCENT, panel, width=2, border_radius=theme.RADIUS_MEDIUM)

        title = self.big_font.render("Time Up", True, theme.TEXT)
        score = self.info_font.render(f"Final Score: {self.score}", True, theme.TEXT)
        summary = self.info_font.render(
            f"Pickups: {self.pickups_collected}  |  Accuracy: {self.collection_accuracy():0.1f}%  |  Best Combo: {self.best_combo}",
            True,
            theme.TEXT,
        )
        controls = self.small_font.render(
            "Press Space / Enter / Click / F5 to restart   |   Esc to go back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 58)))
        screen.blit(score, score.get_rect(center=(panel.centerx, panel.top + 118)))
        screen.blit(summary, summary.get_rect(center=(panel.centerx, panel.top + 154)))
        screen.blit(controls, controls.get_rect(center=(panel.centerx, panel.top + 198)))

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        self.draw_background(screen)
        self.draw_pickups(screen)
        self.draw_hazards(screen)
        self.draw_player(screen)
        self.draw_particles(screen)
        self.render_hud(screen)

        if self.game_over:
            self.render_game_over_overlay(screen)