from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class FroggerCloneGame(GameBase):
    game_id = "frogger_clone"
    title = "Frogger Clone"

    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui: GameUI | None = None

        self.play_rect = pygame.Rect(0, 0, 960, 704)
        self.cell_size = 64
        self.cols = 11
        self.rows = 11
        self.board_rect = pygame.Rect(0, 0, self.cols * self.cell_size, self.rows * self.cell_size)

        self.player_col = 0
        self.player_row = 0
        self.player_offset_x = 0.0
        self.player_move_cooldown = 0.0
        self.move_delay = 0.12

        self.level = 1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False

        self.home_slots: list[int] = []
        self.filled_homes: set[int] = set()

        self.road_lanes: list[dict] = []
        self.river_lanes: list[dict] = []

    def enter(self) -> None:
        self.ui = GameUI()
        self.reset_game()

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.level = 1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.setup_level(reset_score=False)

    def setup_level(self, reset_score: bool = False) -> None:
        if reset_score:
            self.score = 0

        self.player_col = self.cols // 2
        self.player_row = self.rows - 1
        self.player_offset_x = 0.0
        self.player_move_cooldown = 0.0

        self.home_slots = [1, 3, 5, 7, 9]
        self.filled_homes.clear()

        speed_bonus = (self.level - 1) * 18

        self.road_lanes = [
            {
                "row": 7,
                "direction": 1,
                "speed": 130 + speed_bonus,
                "vehicles": [
                    {"x": -40, "w": 92},
                    {"x": 250, "w": 92},
                    {"x": 540, "w": 92},
                ],
                "color": theme.DANGER,
            },
            {
                "row": 8,
                "direction": -1,
                "speed": 165 + speed_bonus,
                "vehicles": [
                    {"x": 120, "w": 74},
                    {"x": 360, "w": 74},
                    {"x": 680, "w": 74},
                    {"x": 900, "w": 74},
                ],
                "color": theme.WARNING,
            },
            {
                "row": 9,
                "direction": 1,
                "speed": 190 + speed_bonus,
                "vehicles": [
                    {"x": -60, "w": 118},
                    {"x": 340, "w": 118},
                    {"x": 760, "w": 118},
                ],
                "color": theme.ACCENT,
            },
        ]

        self.river_lanes = [
            {
                "row": 2,
                "direction": -1,
                "speed": 95 + speed_bonus,
                "logs": [
                    {"x": 80, "w": 160},
                    {"x": 430, "w": 160},
                    {"x": 780, "w": 160},
                ],
            },
            {
                "row": 3,
                "direction": 1,
                "speed": 120 + speed_bonus,
                "logs": [
                    {"x": -20, "w": 126},
                    {"x": 260, "w": 126},
                    {"x": 580, "w": 126},
                ],
            },
            {
                "row": 4,
                "direction": -1,
                "speed": 135 + speed_bonus,
                "logs": [
                    {"x": 110, "w": 192},
                    {"x": 510, "w": 192},
                ],
            },
            {
                "row": 5,
                "direction": 1,
                "speed": 110 + speed_bonus,
                "logs": [
                    {"x": 40, "w": 148},
                    {"x": 360, "w": 148},
                    {"x": 720, "w": 148},
                ],
            },
        ]

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect(
            (screen.get_width() - 1100) // 2,
            140,
            1100,
            740,
        )
        self.board_rect = pygame.Rect(0, 0, self.cols * self.cell_size, self.rows * self.cell_size)
        self.board_rect.centerx = self.play_rect.centerx
        self.board_rect.top = self.play_rect.top + 22

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["round"] = self.level
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene

        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def reset_player(self) -> None:
        self.player_col = self.cols // 2
        self.player_row = self.rows - 1
        self.player_offset_x = 0.0
        self.player_move_cooldown = 0.0

    def lose_life(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self.reset_player()

    def handle_goal_row(self) -> None:
        if self.player_row != 0:
            return

        if self.player_col in self.home_slots and self.player_col not in self.filled_homes:
            self.filled_homes.add(self.player_col)
            self.score += 250
            if len(self.filled_homes) == len(self.home_slots):
                self.level += 1
                self.score += 500
                self.setup_level()
            else:
                self.reset_player()
        else:
            self.lose_life()

    def attempt_move(self, dc: int, dr: int) -> None:
        if self.game_over or self.paused or self.player_move_cooldown > 0:
            return

        new_col = max(0, min(self.cols - 1, self.player_col + dc))
        new_row = max(0, min(self.rows - 1, self.player_row + dr))

        if new_col == self.player_col and new_row == self.player_row:
            return

        if new_row < self.player_row:
            self.score += 10

        self.player_col = new_col
        self.player_row = new_row
        self.player_offset_x = 0.0
        self.player_move_cooldown = self.move_delay
        self.handle_goal_row()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_game()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.attempt_move(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.attempt_move(1, 0)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.attempt_move(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.attempt_move(0, 1)

    def lane_y(self, row: int) -> int:
        return self.board_rect.top + row * self.cell_size

    def wrap_movers(self, movers: list[dict], direction: int) -> None:
        lane_left = self.board_rect.left - 220
        lane_right = self.board_rect.right + 220

        for mover in movers:
            if direction > 0 and mover["x"] > lane_right:
                mover["x"] = lane_left - mover["w"]
            elif direction < 0 and mover["x"] + mover["w"] < lane_left:
                mover["x"] = lane_right

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused:
            return

        if self.player_move_cooldown > 0:
            self.player_move_cooldown -= dt

        if self.game_over:
            return

        for lane in self.road_lanes:
            for vehicle in lane["vehicles"]:
                vehicle["x"] += lane["direction"] * lane["speed"] * dt
            self.wrap_movers(lane["vehicles"], lane["direction"])

        for lane in self.river_lanes:
            for log in lane["logs"]:
                log["x"] += lane["direction"] * lane["speed"] * dt
            self.wrap_movers(lane["logs"], lane["direction"])

        player_rect = self.get_player_rect()

        for lane in self.road_lanes:
            if self.player_row == lane["row"]:
                for vehicle in lane["vehicles"]:
                    vehicle_rect = pygame.Rect(
                        int(vehicle["x"]),
                        self.lane_y(lane["row"]) + 10,
                        vehicle["w"],
                        self.cell_size - 20,
                    )
                    if player_rect.colliderect(vehicle_rect):
                        self.lose_life()
                        return

        river_rows = {lane["row"] for lane in self.river_lanes}
        if self.player_row in river_rows:
            carried = False
            for lane in self.river_lanes:
                if self.player_row != lane["row"]:
                    continue

                for log in lane["logs"]:
                    log_rect = pygame.Rect(
                        int(log["x"]),
                        self.lane_y(lane["row"]) + 14,
                        log["w"],
                        self.cell_size - 28,
                    )
                    if player_rect.colliderect(log_rect):
                        self.player_offset_x += lane["direction"] * lane["speed"] * dt
                        if abs(self.player_offset_x) >= self.cell_size:
                            cell_shift = int(self.player_offset_x / self.cell_size)
                            self.player_col += cell_shift
                            self.player_offset_x -= cell_shift * self.cell_size
                        carried = True
                        break

                if carried:
                    break

            if not carried:
                self.lose_life()
                return

            if self.player_col < 0 or self.player_col >= self.cols:
                self.lose_life()
                return

    def get_player_rect(self) -> pygame.Rect:
        x = self.board_rect.left + self.player_col * self.cell_size + 10 + int(self.player_offset_x)
        y = self.board_rect.top + self.player_row * self.cell_size + 10
        return pygame.Rect(x, y, self.cell_size - 20, self.cell_size - 20)

    def draw_board(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for row in range(self.rows):
            row_rect = pygame.Rect(
                self.board_rect.left,
                self.board_rect.top + row * self.cell_size,
                self.board_rect.width,
                self.cell_size,
            )

            if row == 0:
                color = (36, 62, 48)
            elif row in (1, 6, 10):
                color = (50, 82, 54)
            elif row in (2, 3, 4, 5):
                color = (40, 76, 108)
            else:
                color = (70, 70, 78)

            pygame.draw.rect(screen, color, row_rect)

        for col in range(self.cols + 1):
            x = self.board_rect.left + col * self.cell_size
            pygame.draw.line(screen, theme.SURFACE_ALT, (x, self.board_rect.top), (x, self.board_rect.bottom), 1)

        for row in range(self.rows + 1):
            y = self.board_rect.top + row * self.cell_size
            pygame.draw.line(screen, theme.SURFACE_ALT, (self.board_rect.left, y), (self.board_rect.right, y), 1)

        for home_col in self.home_slots:
            slot_rect = pygame.Rect(
                self.board_rect.left + home_col * self.cell_size + 8,
                self.board_rect.top + 8,
                self.cell_size - 16,
                self.cell_size - 16,
            )
            slot_color = theme.ACCENT if home_col in self.filled_homes else (20, 34, 28)
            pygame.draw.rect(screen, slot_color, slot_rect, border_radius=12)
            if home_col in self.filled_homes:
                pygame.draw.circle(screen, theme.TEXT, slot_rect.center, 12)

    def draw_road_movers(self, screen: pygame.Surface) -> None:
        for lane in self.road_lanes:
            for vehicle in lane["vehicles"]:
                rect = pygame.Rect(
                    int(vehicle["x"]),
                    self.lane_y(lane["row"]) + 10,
                    vehicle["w"],
                    self.cell_size - 20,
                )
                pygame.draw.rect(screen, lane["color"], rect, border_radius=10)
                windshield = rect.inflate(-22, -18)
                pygame.draw.rect(screen, theme.BACKGROUND, windshield, border_radius=8)

    def draw_river_movers(self, screen: pygame.Surface) -> None:
        for lane in self.river_lanes:
            for log in lane["logs"]:
                rect = pygame.Rect(
                    int(log["x"]),
                    self.lane_y(lane["row"]) + 14,
                    log["w"],
                    self.cell_size - 28,
                )
                pygame.draw.rect(screen, (122, 84, 52), rect, border_radius=12)
                pygame.draw.line(screen, (92, 60, 38), (rect.left + 14, rect.centery), (rect.right - 14, rect.centery), 4)

    def draw_player(self, screen: pygame.Surface) -> None:
        rect = self.get_player_rect()
        pygame.draw.rect(screen, theme.ACCENT, rect, border_radius=14)
        eye_y = rect.top + 15
        pygame.draw.circle(screen, theme.TEXT, (rect.left + 14, eye_y), 4)
        pygame.draw.circle(screen, theme.TEXT, (rect.right - 14, eye_y), 4)

    def render_hud(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_header(
            screen,
            "Frogger Clone",
            "Move with Arrow Keys or WASD. Reach all home slots. F5 restart, Esc back.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Score: {self.score}",
                f"Lives: {self.lives}",
                f"Level: {self.level}",
                f"Homes: {len(self.filled_homes)}/{len(self.home_slots)}",
            ],
        )
        self.ui.draw_sub_stats(
            screen,
            "Use logs safely, avoid traffic, and finish every lane cleanly.",
        )
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

    def render_game_over_overlay(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.ui.draw_game_over(
            screen,
            self.play_rect,
            "Game Over",
            f"Final Score: {self.score}",
            f"Highest Level: {self.level}  |  Homes Filled: {len(self.filled_homes)}/{len(self.home_slots)}",
        )

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)
        self.rebuild_layout(screen)
        self.draw_board(screen)
        self.draw_river_movers(screen)
        self.draw_road_movers(screen)
        self.draw_player(screen)
        self.render_hud(screen)

        if self.paused and not self.game_over:
            assert self.ui is not None
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            self.render_game_over_overlay(screen)