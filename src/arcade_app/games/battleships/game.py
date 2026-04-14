from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.battleships.logic import BattleshipsLogic
from arcade_app.ui import theme


class BattleshipsGame(GameBase):
    game_id = "battleships"
    title = "Battleships"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = BattleshipsLogic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.left_board_rect = pygame.Rect(0, 0, 420, 420)
        self.right_board_rect = pygame.Rect(0, 0, 420, 420)

        self.left_cells: list[list[pygame.Rect]] = []
        self.right_cells: list[list[pygame.Rect]] = []

        self.pvp_button = pygame.Rect(0, 0, 180, 44)
        self.pvc_button = pygame.Rect(0, 0, 180, 44)

        self.hovered_cell: tuple[int, int] | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)

        # Ensure the default starting mode is fully initialized.
        # This fixes the bug where PvC could start without enemy ships placed.
        self.logic.set_mode(self.logic.vs_computer)
        self.hovered_cell = None

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.left_board_rect = pygame.Rect(150, 230, 420, 420)
        self.right_board_rect = pygame.Rect(screen.get_width() - 570, 230, 420, 420)

        self.pvp_button = pygame.Rect(screen.get_width() // 2 - 210, 115, 180, 44)
        self.pvc_button = pygame.Rect(screen.get_width() // 2 + 30, 115, 180, 44)

        self.left_cells = self.build_cell_grid(self.left_board_rect)
        self.right_cells = self.build_cell_grid(self.right_board_rect)

    def build_cell_grid(self, rect: pygame.Rect) -> list[list[pygame.Rect]]:
        padding = 6
        cell_size = (rect.width - padding * 9) // 8
        grid: list[list[pygame.Rect]] = []

        for row in range(8):
            row_rects = []
            for col in range(8):
                x = rect.x + padding + col * (cell_size + padding)
                y = rect.y + padding + row * (cell_size + padding)
                row_rects.append(pygame.Rect(x, y, cell_size, cell_size))
            grid.append(row_rects)

        return grid

    def status_text(self) -> str:
        if self.logic.phase == "placement":
            player_label = "Player 1" if self.logic.placement_player == 1 else "Player 2"
            size = self.logic.current_ship_size()
            orientation = "Horizontal" if self.logic.placement_orientation == "horizontal" else "Vertical"
            return f"{player_label}: place ship of size {size} ({orientation})"

        if self.logic.winner == 1:
            return "Winner: Player 1"
        if self.logic.winner == 2:
            return "Winner: Computer" if self.logic.vs_computer else "Winner: Player 2"

        if self.logic.current_player == 1:
            return "Player 1 turn"
        return "Computer turn" if self.logic.vs_computer else "Player 2 turn"

    def draw_mode_button(self, screen: pygame.Surface, rect: pygame.Rect, label: str, selected: bool) -> None:
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT

        pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border, rect, width=3, border_radius=theme.RADIUS_MEDIUM)

        assert self.small_font is not None
        text = self.small_font.render(label, True, theme.TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    def get_hover_preview_cells(self) -> list[tuple[int, int]]:
        if self.logic.phase != "placement" or self.hovered_cell is None:
            return []

        row, col = self.hovered_cell
        size = self.logic.current_ship_size()
        if size is None:
            return []

        cells: list[tuple[int, int]] = []

        if self.logic.placement_orientation == "horizontal":
            for c in range(col, col + size):
                if 0 <= c < self.logic.BOARD_SIZE:
                    cells.append((row, c))
                else:
                    return []
        else:
            for r in range(row, row + size):
                if 0 <= r < self.logic.BOARD_SIZE:
                    cells.append((r, col))
                else:
                    return []

        return cells

    def can_place_hover_preview(self) -> bool:
        if self.logic.phase != "placement" or self.hovered_cell is None:
            return False

        row, col = self.hovered_cell
        size = self.logic.current_ship_size()
        if size is None:
            return False

        board = self.logic.get_active_board_for_placement()
        return self.logic.can_place_ship(board, row, col, size, self.logic.placement_orientation)

    def draw_board(
        self,
        screen: pygame.Surface,
        board_rect: pygame.Rect,
        cells: list[list[pygame.Rect]],
        ship_board: list[list[int]],
        shot_board: list[list[int]],
        reveal_ships: bool,
        preview_cells: list[tuple[int, int]] | None = None,
        preview_valid: bool = True,
    ) -> None:
        assert self.small_font is not None

        pygame.draw.rect(screen, theme.SURFACE, board_rect, border_radius=theme.RADIUS_MEDIUM)

        preview_set = set(preview_cells or [])

        for row in range(8):
            for col in range(8):
                rect = cells[row][col]

                fill = theme.SURFACE_ALT

                if reveal_ships and ship_board[row][col] == 1:
                    fill = (90, 120, 170)

                if shot_board[row][col] == 1:
                    fill = (120, 120, 130)
                elif shot_board[row][col] == 2:
                    fill = theme.DANGER

                pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_SMALL)

                if (row, col) in preview_set:
                    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    overlay.fill((100, 220, 140, 110) if preview_valid else (220, 90, 90, 110))
                    screen.blit(overlay, rect.topleft)

                if shot_board[row][col] == 1:
                    text = self.small_font.render("•", True, theme.TEXT)
                    screen.blit(text, text.get_rect(center=rect.center))
                elif shot_board[row][col] == 2:
                    text = self.small_font.render("X", True, theme.TEXT)
                    screen.blit(text, text.get_rect(center=rect.center))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    current_mode = self.logic.vs_computer
                    self.logic.set_mode(current_mode)
                    self.hovered_cell = None
                elif event.key == pygame.K_1:
                    self.logic.set_mode(False)
                    self.hovered_cell = None
                elif event.key == pygame.K_2:
                    self.logic.set_mode(True)
                    self.hovered_cell = None
                elif event.key == pygame.K_r and self.logic.phase == "placement":
                    self.logic.placement_orientation = (
                        "vertical" if self.logic.placement_orientation == "horizontal" else "horizontal"
                    )

            elif event.type == pygame.MOUSEMOTION:
                self.hovered_cell = None
                if self.logic.phase == "placement":
                    target_cells = self.left_cells if self.logic.placement_player == 1 else self.right_cells
                    for row in range(8):
                        for col in range(8):
                            if target_cells[row][col].collidepoint(event.pos):
                                self.hovered_cell = (row, col)
                                return

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.pvp_button.collidepoint(mouse_pos):
                    self.logic.set_mode(False)
                    self.hovered_cell = None
                    return

                if self.pvc_button.collidepoint(mouse_pos):
                    self.logic.set_mode(True)
                    self.hovered_cell = None
                    return

                if self.logic.phase == "placement":
                    target_cells = self.left_cells if self.logic.placement_player == 1 else self.right_cells
                    for row in range(8):
                        for col in range(8):
                            if target_cells[row][col].collidepoint(mouse_pos):
                                self.logic.place_next_ship(row, col)
                                return

                elif self.logic.phase == "battle" and self.logic.current_player == 1 and self.logic.winner is None:
                    for row in range(8):
                        for col in range(8):
                            if self.right_cells[row][col].collidepoint(mouse_pos):
                                self.logic.attack(row, col)
                                return

    def update(self, dt: float) -> None:
        if self.logic.vs_computer and self.logic.phase == "battle" and self.logic.current_player == 2:
            self.logic.ai_take_turn()

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Battleships", True, theme.TEXT)
        status = self.info_font.render(self.status_text(), True, theme.TEXT)
        controls = self.info_font.render(
            "Placement: Click to place, R to rotate  |  Battle: Click enemy grid  |  1: PvP  |  2: PvC  |  F5: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        left_label = self.info_font.render("Player 1 Fleet", True, theme.TEXT)
        right_label_text = "Enemy Fleet" if self.logic.vs_computer else "Player 2 Fleet"
        right_label = self.info_font.render(right_label_text, True, theme.TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 32)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 78)))

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.logic.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.logic.vs_computer)

        screen.blit(left_label, left_label.get_rect(center=(self.left_board_rect.centerx, 205)))
        screen.blit(right_label, right_label.get_rect(center=(self.right_board_rect.centerx, 205)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

        reveal_enemy_ships = not self.logic.vs_computer and self.logic.phase == "placement" and self.logic.placement_player == 2
        reveal_enemy_battle = not self.logic.vs_computer and self.logic.winner is not None

        preview_cells = self.get_hover_preview_cells()
        preview_valid = self.can_place_hover_preview()

        left_preview = preview_cells if self.logic.phase == "placement" and self.logic.placement_player == 1 else []
        right_preview = preview_cells if self.logic.phase == "placement" and self.logic.placement_player == 2 else []

        self.draw_board(
            screen,
            self.left_board_rect,
            self.left_cells,
            self.logic.player_board,
            self.logic.enemy_shots,
            reveal_ships=True,
            preview_cells=left_preview,
            preview_valid=preview_valid,
        )

        self.draw_board(
            screen,
            self.right_board_rect,
            self.right_cells,
            self.logic.enemy_board,
            self.logic.player_shots,
            reveal_ships=reveal_enemy_ships or reveal_enemy_battle,
            preview_cells=right_preview,
            preview_valid=preview_valid,
        )