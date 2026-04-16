from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class TicTacToeGame(GameBase):
    game_id = "tic_tac_toe"
    title = "Tic Tac Toe"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.symbol_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 980, 620)
        self.board_rect = pygame.Rect(0, 0, 360, 360)
        self.pvp_button = pygame.Rect(0, 0, 170, 40)
        self.pvc_button = pygame.Rect(0, 0, 170, 40)

        self.board: list[list[str]] = []
        self.current_player = "X"
        self.winner = ""
        self.draw_state = False
        self.vs_computer = True
        self.game_over = False
        self.paused = False
        self.moves = 0

    def enter(self) -> None:
        self.ui = GameUI()
        self.symbol_font = pygame.font.SysFont("arial", 84, bold=True)
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 980) // 2, 165, 980, 620)
        self.board_rect = pygame.Rect(0, 0, 360, 360)
        self.board_rect.center = self.play_rect.center
        self.board_rect.y -= 15
        self.pvp_button = pygame.Rect(self.play_rect.centerx - 190, self.play_rect.top + 28, 170, 40)
        self.pvc_button = pygame.Rect(self.play_rect.centerx + 20, self.play_rect.top + 28, 170, 40)

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
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

    def available_moves(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]

    def check_winner(self) -> None:
        lines = []

        for i in range(3):
            lines.append(self.board[i])
            lines.append([self.board[0][i], self.board[1][i], self.board[2][i]])

        lines.append([self.board[0][0], self.board[1][1], self.board[2][2]])
        lines.append([self.board[0][2], self.board[1][1], self.board[2][0]])

        for line in lines:
            if line[0] and line.count(line[0]) == 3:
                self.winner = line[0]
                self.game_over = True
                return

        if not self.available_moves():
            self.draw_state = True
            self.game_over = True

    def make_move(self, row: int, col: int) -> None:
        if self.game_over or self.paused or self.board[row][col]:
            return

        self.board[row][col] = self.current_player
        self.moves += 1
        self.check_winner()

        if not self.game_over:
            self.current_player = "O" if self.current_player == "X" else "X"

    def computer_move(self) -> None:
        if self.game_over or self.paused or not self.vs_computer or self.current_player != "O":
            return
        move = random.choice(self.available_moves())
        self.make_move(*move)

    def cell_at(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        if not self.board_rect.collidepoint(pos):
            return None
        cell_size = self.board_rect.width // 3
        col = (pos[0] - self.board_rect.x) // cell_size
        row = (pos[1] - self.board_rect.y) // cell_size
        return int(row), int(col)

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

                cell = self.cell_at(event.pos)
                if cell is not None and (not self.vs_computer or self.current_player == "X"):
                    self.make_move(*cell)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.vs_computer and not self.game_over and not self.paused and self.current_player == "O":
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
        assert self.symbol_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Tic Tac Toe",
            "Click a square to place your mark. Switch between PvP and PvC above the board.",
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
                sub = "Board filled with no winner."
            else:
                sub = f"{self.winner} completed a line."
        else:
            sub = "Control the center, create forks, and avoid giving up easy blocks."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.vs_computer)

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        cell_size = self.board_rect.width // 3
        for i in range(1, 3):
            pygame.draw.line(
                screen,
                theme.SURFACE_ALT,
                (self.board_rect.x + i * cell_size, self.board_rect.y),
                (self.board_rect.x + i * cell_size, self.board_rect.bottom),
                3,
            )
            pygame.draw.line(
                screen,
                theme.SURFACE_ALT,
                (self.board_rect.x, self.board_rect.y + i * cell_size),
                (self.board_rect.right, self.board_rect.y + i * cell_size),
                3,
            )

        for r in range(3):
            for c in range(3):
                value = self.board[r][c]
                if not value:
                    continue
                center = (
                    self.board_rect.x + c * cell_size + cell_size // 2,
                    self.board_rect.y + r * cell_size + cell_size // 2,
                )
                color = theme.ACCENT if value == "X" else theme.WARNING
                text = self.symbol_font.render(value, True, color)
                screen.blit(text, text.get_rect(center=center))

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