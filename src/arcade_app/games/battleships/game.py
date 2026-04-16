from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class BattleshipsGame(GameBase):
    game_id = "battleships"
    title = "Battleships"

    GRID_SIZE = 8
    CELL_SIZE = 46
    SHIP_SIZES = [5, 4, 3, 3, 2]

    STATE_PLACEMENT = "placement"
    STATE_BATTLE = "battle"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1120, 640)
        self.player_board_rect = pygame.Rect(0, 0, self.GRID_SIZE * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE)
        self.enemy_board_rect = pygame.Rect(0, 0, self.GRID_SIZE * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE)
        self.pvp_button = pygame.Rect(0, 0, 170, 40)
        self.pvc_button = pygame.Rect(0, 0, 170, 40)

        self.vs_computer = True
        self.paused = False
        self.completed = False
        self.winner_text = ""

        self.state = self.STATE_PLACEMENT
        self.placement_index = 0
        self.placement_horizontal = True
        self.hover_cell: tuple[int, int] | None = None

        self.player_ships: list[set[tuple[int, int]]] = []
        self.enemy_ships: list[set[tuple[int, int]]] = []
        self.player_hits: set[tuple[int, int]] = set()
        self.player_misses: set[tuple[int, int]] = set()
        self.enemy_hits: set[tuple[int, int]] = set()
        self.enemy_misses: set[tuple[int, int]] = set()

        self.turn = "player"
        self.moves = 0
        self.enemy_think_timer = 0.0

    def enter(self) -> None:
        self.ui = GameUI()
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1120) // 2, 165, 1120, 640)
        board_size = self.GRID_SIZE * self.CELL_SIZE
        gap = 100

        self.player_board_rect = pygame.Rect(
            self.play_rect.centerx - gap // 2 - board_size,
            self.play_rect.top + 120,
            board_size,
            board_size,
        )
        self.enemy_board_rect = pygame.Rect(
            self.play_rect.centerx + gap // 2,
            self.play_rect.top + 120,
            board_size,
            board_size,
        )

        self.pvp_button = pygame.Rect(self.play_rect.centerx - 190, self.play_rect.top + 28, 170, 40)
        self.pvc_button = pygame.Rect(self.play_rect.centerx + 20, self.play_rect.top + 28, 170, 40)

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.paused = False
        self.completed = False
        self.winner_text = ""
        self.turn = "player"
        self.moves = 0
        self.enemy_think_timer = 0.5

        self.state = self.STATE_PLACEMENT
        self.placement_index = 0
        self.placement_horizontal = True
        self.hover_cell = None

        self.player_hits.clear()
        self.player_misses.clear()
        self.enemy_hits.clear()
        self.enemy_misses.clear()

        self.player_ships = []
        self.enemy_ships = self.generate_fleet()

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset_game()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = len(self.player_hits) * 100
        payload["round"] = self.moves
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def generate_fleet(self) -> list[set[tuple[int, int]]]:
        ships: list[set[tuple[int, int]]] = []

        for size in self.SHIP_SIZES:
            placed = False
            while not placed:
                horizontal = random.choice([True, False])
                if horizontal:
                    row = random.randint(0, self.GRID_SIZE - 1)
                    col = random.randint(0, self.GRID_SIZE - size)
                    ship = {(row, col + i) for i in range(size)}
                else:
                    row = random.randint(0, self.GRID_SIZE - size)
                    col = random.randint(0, self.GRID_SIZE - 1)
                    ship = {(row + i, col) for i in range(size)}

                if all(ship.isdisjoint(existing) for existing in ships):
                    ships.append(ship)
                    placed = True

        return ships

    def board_cell_at(self, pos: tuple[int, int], board_rect: pygame.Rect) -> tuple[int, int] | None:
        if not board_rect.collidepoint(pos):
            return None
        col = (pos[0] - board_rect.x) // self.CELL_SIZE
        row = (pos[1] - board_rect.y) // self.CELL_SIZE
        return int(row), int(col)

    def ship_at(self, ships: list[set[tuple[int, int]]], cell: tuple[int, int]) -> set[tuple[int, int]] | None:
        for ship in ships:
            if cell in ship:
                return ship
        return None

    def all_sunk(self, ships: list[set[tuple[int, int]]], hits: set[tuple[int, int]]) -> bool:
        return all(all(cell in hits for cell in ship) for ship in ships)

    def current_ship_size(self) -> int | None:
        if self.placement_index >= len(self.SHIP_SIZES):
            return None
        return self.SHIP_SIZES[self.placement_index]

    def build_ship_cells(self, start: tuple[int, int], size: int, horizontal: bool) -> set[tuple[int, int]] | None:
        row, col = start
        cells: set[tuple[int, int]] = set()

        for i in range(size):
            r = row
            c = col + i if horizontal else col
            if not horizontal:
                r = row + i

            if not (0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE):
                return None
            cells.add((r, c))

        return cells

    def can_place_ship(self, ship: set[tuple[int, int]]) -> bool:
        return all(ship.isdisjoint(existing) for existing in self.player_ships)

    def place_current_ship(self, start: tuple[int, int]) -> None:
        if self.state != self.STATE_PLACEMENT or self.completed:
            return

        size = self.current_ship_size()
        if size is None:
            return

        ship = self.build_ship_cells(start, size, self.placement_horizontal)
        if ship is None or not self.can_place_ship(ship):
            return

        self.player_ships.append(ship)
        self.placement_index += 1

        if self.placement_index >= len(self.SHIP_SIZES):
            self.state = self.STATE_BATTLE
            self.turn = "player"

    def undo_last_ship(self) -> None:
        if self.state != self.STATE_PLACEMENT or not self.player_ships:
            return
        self.player_ships.pop()
        self.placement_index = max(0, self.placement_index - 1)

    def fire_at_enemy(self, cell: tuple[int, int]) -> None:
        if self.completed or self.paused or self.state != self.STATE_BATTLE or self.turn != "player":
            return
        if cell in self.player_hits or cell in self.player_misses:
            return

        self.moves += 1
        ship = self.ship_at(self.enemy_ships, cell)
        if ship is not None:
            self.player_hits.add(cell)
            if self.all_sunk(self.enemy_ships, self.player_hits):
                self.completed = True
                self.winner_text = "Player Wins"
                return
        else:
            self.player_misses.add(cell)

        self.turn = "enemy"

    def enemy_move(self) -> None:
        available = [
            (r, c)
            for r in range(self.GRID_SIZE)
            for c in range(self.GRID_SIZE)
            if (r, c) not in self.enemy_hits and (r, c) not in self.enemy_misses
        ]
        if not available:
            return

        cell = random.choice(available)
        ship = self.ship_at(self.player_ships, cell)
        if ship is not None:
            self.enemy_hits.add(cell)
            if self.all_sunk(self.player_ships, self.enemy_hits):
                self.completed = True
                self.winner_text = "Enemy Wins"
                return
        else:
            self.enemy_misses.add(cell)

        self.turn = "player"

    def draw_mode_button(self, screen: pygame.Surface, rect: pygame.Rect, label: str, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.hover_cell = self.board_cell_at(mouse_pos, self.player_board_rect) if self.state == self.STATE_PLACEMENT else None

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.completed and self.state == self.STATE_BATTLE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif self.state == self.STATE_PLACEMENT:
                    if event.key == pygame.K_r:
                        self.placement_horizontal = not self.placement_horizontal
                    elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        self.undo_last_ship()

            elif event.type == pygame.MOUSEMOTION:
                self.hover_cell = self.board_cell_at(event.pos, self.player_board_rect) if self.state == self.STATE_PLACEMENT else None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.pvp_button.collidepoint(event.pos):
                        self.set_mode(False)
                        return
                    if self.pvc_button.collidepoint(event.pos):
                        self.set_mode(True)
                        return

                    if self.completed:
                        self.reset_game()
                        continue
                    if self.paused:
                        continue

                    if self.state == self.STATE_PLACEMENT:
                        cell = self.board_cell_at(event.pos, self.player_board_rect)
                        if cell is not None:
                            self.place_current_ship(cell)
                    else:
                        target = self.board_cell_at(event.pos, self.enemy_board_rect)
                        if target is not None:
                            self.fire_at_enemy(target)

                elif event.button == 3 and self.state == self.STATE_PLACEMENT:
                    self.placement_horizontal = not self.placement_horizontal

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.paused or self.completed or self.state != self.STATE_BATTLE:
            return

        if self.vs_computer and self.turn == "enemy":
            self.enemy_think_timer -= dt
            if self.enemy_think_timer <= 0:
                self.enemy_move()
                self.enemy_think_timer = 0.5

    def draw_board(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        ships: list[set[tuple[int, int]]],
        hits: set[tuple[int, int]],
        misses: set[tuple[int, int]],
        reveal_ships: bool,
    ) -> None:
        pygame.draw.rect(screen, theme.SURFACE, rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                cell_rect = pygame.Rect(
                    rect.x + c * self.CELL_SIZE,
                    rect.y + r * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, cell_rect, width=1, border_radius=2)

                cell = (r, c)
                ship = self.ship_at(ships, cell)

                if reveal_ships and ship is not None and cell not in hits:
                    inner = cell_rect.inflate(-8, -8)
                    pygame.draw.rect(screen, (90, 110, 145), inner, border_radius=6)

                if cell in misses:
                    pygame.draw.circle(screen, theme.MUTED_TEXT, cell_rect.center, 6)
                elif cell in hits:
                    pygame.draw.circle(screen, theme.DANGER, cell_rect.center, 12)
                    pygame.draw.line(screen, theme.TEXT, (cell_rect.left + 10, cell_rect.top + 10), (cell_rect.right - 10, cell_rect.bottom - 10), 3)
                    pygame.draw.line(screen, theme.TEXT, (cell_rect.right - 10, cell_rect.top + 10), (cell_rect.left + 10, cell_rect.bottom - 10), 3)

    def draw_placement_preview(self, screen: pygame.Surface) -> None:
        if self.state != self.STATE_PLACEMENT or self.hover_cell is None:
            return

        size = self.current_ship_size()
        if size is None:
            return

        ship = self.build_ship_cells(self.hover_cell, size, self.placement_horizontal)
        if ship is None:
            return

        valid = self.can_place_ship(ship)
        color = theme.ACCENT if valid else theme.DANGER

        for r, c in ship:
            cell_rect = pygame.Rect(
                self.player_board_rect.x + c * self.CELL_SIZE,
                self.player_board_rect.y + r * self.CELL_SIZE,
                self.CELL_SIZE,
                self.CELL_SIZE,
            ).inflate(-10, -10)
            pygame.draw.rect(screen, color, cell_rect, width=3, border_radius=6)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.mode_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        if self.state == self.STATE_PLACEMENT:
            size = self.current_ship_size()
            subtitle = (
                f"Place ship {self.placement_index + 1}/{len(self.SHIP_SIZES)} "
                f"(size {size}). Click to place, R or Right Click to rotate, Backspace to undo."
                if size is not None
                else "Placement complete."
            )
        else:
            subtitle = "Click enemy cells to fire. Sink the opposing fleet before yours is destroyed."

        self.ui.draw_header(screen, "Battleships", subtitle)
        self.ui.draw_stats_row(
            screen,
            [
                f"Mode: {'PvC' if self.vs_computer else 'PvP-lite'}",
                f"Phase: {'Placement' if self.state == self.STATE_PLACEMENT else 'Battle'}",
                f"Turn: {self.turn.title() if self.state == self.STATE_BATTLE and not self.completed else '--'}",
                f"Shots: {self.moves}",
            ],
        )

        if self.completed:
            sub = self.winner_text
        elif self.state == self.STATE_PLACEMENT:
            sub = f"Ships placed: {len(self.player_ships)}/{len(self.SHIP_SIZES)}  |  Orientation: {'Horizontal' if self.placement_horizontal else 'Vertical'}"
        else:
            sub = "Track hits, finish damaged ships, and avoid wasting shots."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(
            screen,
            "Placement: Click place, R/Right Click rotate, Backspace undo  |  Battle: P Pause, F5 Restart, Esc Back"
        )

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.vs_computer)

        left_label = self.mode_font.render("Your Fleet", True, theme.TEXT)
        right_label = self.mode_font.render("Enemy Waters", True, theme.TEXT)
        screen.blit(left_label, left_label.get_rect(center=(self.player_board_rect.centerx, self.player_board_rect.y - 22)))
        screen.blit(right_label, right_label.get_rect(center=(self.enemy_board_rect.centerx, self.enemy_board_rect.y - 22)))

        self.draw_board(screen, self.player_board_rect, self.player_ships, self.enemy_hits, self.enemy_misses, True)
        self.draw_board(
            screen,
            self.enemy_board_rect,
            self.enemy_ships,
            self.player_hits,
            self.player_misses,
            self.completed,
        )
        self.draw_placement_preview(screen)

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                self.winner_text or "Match Over",
                f"Shots Taken: {self.moves}",
                f"Enemy Hits: {len(self.enemy_hits)}  |  Player Hits: {len(self.player_hits)}",
            )