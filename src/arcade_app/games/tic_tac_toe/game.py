from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.tic_tac_toe.logic import TicTacToeLogic
from arcade_app.ui import theme


class TicTacToeGame(GameBase):
    game_id = "tic_tac_toe"
    title = "Tic Tac Toe"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = TicTacToeLogic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.cell_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 540, 540)
        self.cell_rects: list[pygame.Rect] = []

        self.pvp_button = pygame.Rect(520, 110, 220, 44)
        self.pvc_button = pygame.Rect(860, 110, 220, 44)

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.cell_font = pygame.font.SysFont("arial", 72, bold=True)
        self.mode_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        board_size = 540
        self.board_rect = pygame.Rect(
            (screen.get_width() - board_size) // 2,
            170,
            board_size,
            board_size,
        )

        self.pvp_button = pygame.Rect(screen.get_width() // 2 - 250, 110, 180, 44)
        self.pvc_button = pygame.Rect(screen.get_width() // 2 + 70, 110, 180, 44)

        self.cell_rects = []
        cell_size = board_size // 3

        for row in range(3):
            for col in range(3):
                x = self.board_rect.x + col * cell_size
                y = self.board_rect.y + row * cell_size
                self.cell_rects.append(pygame.Rect(x, y, cell_size, cell_size))

    def get_status_text(self) -> str:
        if self.logic.winner is not None:
            return f"Winner: {self.logic.winner}"
        if self.logic.is_draw:
            return "Draw game"
        if self.logic.vs_computer:
            if self.logic.current_player == self.logic.computer_player:
                return "Computer is thinking..."
            return f"Your turn: {self.logic.current_player}"
        return f"Current turn: {self.logic.current_player}"

    def draw_mode_button(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        selected: bool,
    ) -> None:
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT

        pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border, rect, width=3, border_radius=theme.RADIUS_MEDIUM)

        assert self.mode_font is not None
        text = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(text, text.get_rect(center=rect.center))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_r:
                    current_mode = self.logic.vs_computer
                    self.logic.reset()
                    self.logic.vs_computer = current_mode
                elif event.key == pygame.K_1:
                    self.logic.set_mode(False)
                elif event.key == pygame.K_2:
                    self.logic.set_mode(True)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.pvp_button.collidepoint(mouse_pos):
                    self.logic.set_mode(False)
                    return

                if self.pvc_button.collidepoint(mouse_pos):
                    self.logic.set_mode(True)
                    return

                for index, rect in enumerate(self.cell_rects):
                    if rect.collidepoint(mouse_pos):
                        moved = self.logic.make_move(index)
                        if moved and self.logic.vs_computer:
                            self.logic.make_computer_move()
                        break

    def update(self, dt: float) -> None:
        if (
            self.logic.vs_computer
            and self.logic.current_player == self.logic.computer_player
            and self.logic.winner is None
            and not self.logic.is_draw
        ):
            self.logic.make_computer_move()

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.cell_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Tic Tac Toe", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        controls = self.info_font.render(
            "Click a cell  |  1: PvP  |  2: PvC  |  R: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 40)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, 760)))

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.logic.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.logic.vs_computer)

        pygame.draw.rect(
            screen,
            theme.SURFACE,
            self.board_rect,
            border_radius=theme.RADIUS_MEDIUM,
        )

        for rect in self.cell_rects:
            pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=3, border_radius=theme.RADIUS_SMALL)

        for index, rect in enumerate(self.cell_rects):
            value = self.logic.board[index]
            if value:
                text = self.cell_font.render(value, True, theme.TEXT)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)