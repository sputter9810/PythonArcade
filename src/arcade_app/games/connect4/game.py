from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class Connect4Game(GameBase):
    game_id = "connect4"
    title = "Connect 4"

    ROWS = 6
    COLS = 7
    CELL_SIZE = 78

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1000, 620)
        self.board_rect = pygame.Rect(0, 0, self.COLS * self.CELL_SIZE, self.ROWS * self.CELL_SIZE)
        self.pvp_button = pygame.Rect(0, 0, 170, 40)
        self.pvc_button = pygame.Rect(0, 0, 170, 40)

        self.board: list[list[str]] = []
        self.current_player = "R"
        self.winner = ""
        self.draw_state = False
        self.game_over = False
        self.paused = False
        self.vs_computer = True
        self.moves = 0

    def enter(self) -> None:
        self.ui = GameUI()
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1000) // 2, 165, 1000, 620)
        self.board_rect = pygame.Rect(0, 0, self.COLS * self.CELL_SIZE, self.ROWS * self.CELL_SIZE)
        self.board_rect.center = self.play_rect.center
        self.board_rect.y -= 10
        self.pvp_button = pygame.Rect(self.play_rect.centerx - 190, self.play_rect.top + 28, 170, 40)
        self.pvc_button = pygame.Rect(self.play_rect.centerx + 20, self.play_rect.top + 28, 170, 40)

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.board = [["" for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.current_player = "R"
        self.winner = ""
        self.draw_state = False
        self.game_over = False
        self.paused = False
        self.moves = 0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["round"] = self.moves
        return payload

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset_game()

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def valid_columns(self) -> list[int]:
        return [c for c in range(self.COLS) if self.board[0][c] == ""]

    def drop_disc(self, col: int) -> bool:
        if self.game_over or self.paused or col not in self.valid_columns():
            return False

        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == "":
                self.board[row][col] = self.current_player
                self.moves += 1
                self.check_winner(row, col)
                if not self.game_over:
                    self.current_player = "Y" if self.current_player == "R" else "R"
                return True
        return False

    def check_winner(self, row: int, col: int) -> None:
        token = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1

            for sign in (-1, 1):
                r, c = row + dr * sign, col + dc * sign
                while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] == token:
                    count += 1
                    r += dr * sign
                    c += dc * sign

            if count >= 4:
                self.winner = token
                self.game_over = True
                return

        if not self.valid_columns():
            self.draw_state = True
            self.game_over = True

    def computer_move(self) -> None:
        if self.game_over or self.paused or not self.vs_computer or self.current_player != "Y":
            return
        self.drop_disc(random.choice(self.valid_columns()))

    def column_at(self, pos: tuple[int, int]) -> int | None:
        if not self.board_rect.collidepoint(pos):
            return None
        col = (pos[0] - self.board_rect.x) // self.CELL_SIZE
        return int(col)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.game_over and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif not self.game_over and not self.paused:
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
                        self.drop_disc(int(event.unicode) - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pvp_button.collidepoint(event.pos):
                    self.set_mode(False)
                    return
                if self.pvc_button.collidepoint(event.pos):
                    self.set_mode(True)
                    return

                if self.game_over:
                    self.reset_game()
                    return

                if self.paused:
                    continue

                if not self.vs_computer or self.current_player == "R":
                    col = self.column_at(event.pos)
                    if col is not None:
                        self.drop_disc(col)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.vs_computer and not self.game_over and not self.paused and self.current_player == "Y":
            self.computer_move()

    def draw_mode_button(self, screen: pygame.Surface, rect: pygame.Rect, label: str, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border, rect, width=3, border_radius=theme.RADIUS_MEDIUM)
        text = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Connect 4",
            "Click a column or press 1-7 to drop a disc. Connect four before your opponent.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Turn: {self.current_player}" if not self.game_over else "Turn: --",
                f"Mode: {'PvC' if self.vs_computer else 'PvP'}",
                f"Moves: {self.moves}",
            ],
        )

        if self.game_over:
            if self.draw_state:
                sub = "Board filled with no four-in-a-row."
            else:
                sub = f"{self.winner} connected four."
        else:
            sub = "Control the center columns and build threats on multiple lines."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.vs_computer)

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for r in range(self.ROWS):
            for c in range(self.COLS):
                cell_rect = pygame.Rect(
                    self.board_rect.x + c * self.CELL_SIZE,
                    self.board_rect.y + r * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                center = cell_rect.center
                pygame.draw.circle(screen, theme.BACKGROUND, center, self.CELL_SIZE // 2 - 8)

                value = self.board[r][c]
                if value == "R":
                    pygame.draw.circle(screen, theme.DANGER, center, self.CELL_SIZE // 2 - 10)
                elif value == "Y":
                    pygame.draw.circle(screen, theme.WARNING, center, self.CELL_SIZE // 2 - 10)

        if self.paused and not self.game_over:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.game_over:
            title = "Draw" if self.draw_state else f"{self.winner} Wins"
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                title,
                f"Total Moves: {self.moves}",
                f"Mode: {'PvC' if self.vs_computer else 'PvP'}",
            )