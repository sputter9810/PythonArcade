from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class WhacAMoleGame(GameBase):
    game_id = "whac_a_mole"
    title = "Whac-A-Mole"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 980, 620)
        self.holes: list[pygame.Rect] = []
        self.moles: list[dict] = []
        self.popups: list[dict] = []

        self.score = 0
        self.time_left = 30.0
        self.hits = 0
        self.misses = 0

        self.game_over = False
        self.paused = False

        self.spawn_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 980) // 2,
            165,
            980,
            620,
        )

        self.holes = []
        cols = 3
        rows = 2
        hole_w = 220
        hole_h = 120
        gap_x = 80
        gap_y = 90

        total_w = cols * hole_w + (cols - 1) * gap_x
        start_x = self.play_rect.centerx - total_w // 2
        start_y = self.play_rect.top + 120

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (hole_w + gap_x)
                y = start_y + row * (hole_h + gap_y)
                self.holes.append(pygame.Rect(x, y, hole_w, hole_h))

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.moles.clear()
        self.popups.clear()

        self.score = 0
        self.time_left = 30.0
        self.hits = 0
        self.misses = 0

        self.game_over = False
        self.paused = False
        self.spawn_timer = 0.45

    def accuracy(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 100.0
        return (self.hits / total) * 100.0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = self.hits
        payload["accuracy"] = round(self.accuracy(), 1)
        return payload

    def add_popup(self, text: str, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.popups.append(
            {
                "text": text,
                "pos": pygame.Vector2(pos[0], pos[1]),
                "vel": pygame.Vector2(0, -38),
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

    def spawn_mole(self) -> None:
        open_indices = [i for i in range(len(self.holes)) if i not in [m["hole_index"] for m in self.moles]]
        if not open_indices:
            return

        hole_index = random.choice(open_indices)
        lifetime = max(0.35, 1.0 - (30.0 - self.time_left) * 0.02)
        self.moles.append(
            {
                "hole_index": hole_index,
                "time_left": lifetime,
            }
        )

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
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over:
                    self.reset_game()
                    continue

                if self.paused:
                    continue

                mouse_pos = event.pos
                hit = None
                for mole in self.moles:
                    hole = self.holes[mole["hole_index"]]
                    mole_rect = pygame.Rect(hole.centerx - 36, hole.y + 12, 72, 72)
                    if mole_rect.collidepoint(mouse_pos):
                        hit = mole
                        break

                if hit is not None:
                    self.moles.remove(hit)
                    self.hits += 1
                    reward = 100
                    self.score += reward
                    hole = self.holes[hit["hole_index"]]
                    self.add_popup(f"+{reward}", (hole.centerx, hole.y), theme.ACCENT)
                else:
                    self.misses += 1
                    self.score = max(0, self.score - 25)
                    self.add_popup("-25", mouse_pos, theme.DANGER)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.update_popups(dt)

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
            self.spawn_mole()
            self.spawn_timer = max(0.18, 0.55 - (30.0 - self.time_left) * 0.01)

        updated_moles: list[dict] = []
        for mole in self.moles:
            mole["time_left"] -= dt
            if mole["time_left"] > 0:
                updated_moles.append(mole)
            else:
                self.misses += 1
        self.moles = updated_moles

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Whac-A-Mole",
            "Click moles quickly before they disappear. Fast reactions keep accuracy high.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Hits: {self.hits}",
                f"Accuracy: {self.accuracy():0.1f}%",
                f"Time: {self.time_left:0.1f}s",
            ],
        )
        self.ui.draw_sub_stats(screen, f"Misses: {self.misses}")
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for hole in self.holes:
            pygame.draw.ellipse(screen, theme.BACKGROUND, hole)
            rim = hole.inflate(10, 10)
            pygame.draw.ellipse(screen, theme.SURFACE_ALT, rim, width=3)

        for mole in self.moles:
            hole = self.holes[mole["hole_index"]]
            body_rect = pygame.Rect(hole.centerx - 36, hole.y + 12, 72, 72)
            pygame.draw.ellipse(screen, theme.WARNING, body_rect)
            pygame.draw.circle(screen, theme.TEXT, (body_rect.centerx - 12, body_rect.y + 20), 4)
            pygame.draw.circle(screen, theme.TEXT, (body_rect.centerx + 12, body_rect.y + 20), 4)

        self.ui.draw_floating_texts(screen, self.popups)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Time Up",
                f"Final Score: {self.score}",
                f"Hits: {self.hits}  |  Accuracy: {self.accuracy():0.1f}%",
            )