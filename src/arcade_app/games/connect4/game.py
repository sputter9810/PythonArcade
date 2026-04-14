from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.connect4.logic import Connect4Logic
from arcade_app.ui import theme


class Connect4Game(GameBase):
    game_id = "connect4"
    title = "Connect 4"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = Connect4Logic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 770, 660)
        self.column_rects: list[pygame.Rect] = []

        self.pvp_button = pygame.Rect(0, 0, 180, 44)
        self.pvc_button = pygame.Rect(0, 0, 180, 44)

        self.hovered_col: int | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.mode_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE, bold=True)

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        board_width = 770
        board_height = 660
        board_y = 170

        self.board_rect = pygame.Rect(
            (screen.get_width() - board_width) // 2,
            board_y,
            board_width,
            board_height,
        )

        self.pvp_button = pygame.Rect(screen.get_width() // 2 - 210, 115, 180, 44)
        self.pvc_button = pygame.Rect(screen.get_width() // 2 + 30, 115, 180, 44)

        col_width = self.board_rect.width // Connect4Logic.COLS
        self.column_rects = []
        for col in range(Connect4Logic.COLS):
            rect = pygame.Rect(
                self.board_rect.x + col * col_width,
                self.board_rect.y,
                col_width,
                self.board_rect.height,
            )
            self.column_rects.append(rect)

    def get_status_text(self) -> str:
        if self.logic.winner == Connect4Logic.PLAYER_ONE:
            return "Winner: Red"
        if self.logic.winner == Connect4Logic.PLAYER_TWO:
            if self.logic.vs_computer:
                return "Winner: Computer"
            return "Winner: Yellow"
        if self.logic.is_draw:
            return "Draw game"

        if self.logic.vs_computer:
            if self.logic.current_player == self.logic.computer_player:
                return "Computer is thinking..."
            return "Your turn: Red"

        return "Current turn: Red" if self.logic.current_player == Connect4Logic.PLAYER_ONE else "Current turn: Yellow"

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

            elif event.type == pygame.MOUSEMOTION:
                self.hovered_col = None
                for col, rect in enumerate(self.column_rects):
                    if rect.collidepoint(event.pos):
                        self.hovered_col = col
                        break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.pvp_button.collidepoint(mouse_pos):
                    self.logic.set_mode(False)
                    return

                if self.pvc_button.collidepoint(mouse_pos):
                    self.logic.set_mode(True)
                    return

                for col, rect in enumerate(self.column_rects):
                    if rect.collidepoint(mouse_pos):
                        moved = self.logic.make_move(col)
                        if moved and self.logic.vs_computer:
                            self.logic.make_computer_move()
                        return

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
        assert self.mode_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Connect 4", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        controls = self.info_font.render(
            "Click a column  |  1: PvP  |  2: PvC  |  R: Restart  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 30)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 78)))

        self.draw_mode_button(screen, self.pvp_button, "Player vs Player", not self.logic.vs_computer)
        self.draw_mode_button(screen, self.pvc_button, "Player vs Computer", self.logic.vs_computer)

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        if self.hovered_col is not None:
            hover_rect = self.column_rects[self.hovered_col]
            hover_overlay = pygame.Surface((hover_rect.width, hover_rect.height), pygame.SRCALPHA)
            hover_overlay.fill((255, 255, 255, 20))
            screen.blit(hover_overlay, hover_rect.topleft)

        cell_padding = 10
        cell_width = self.board_rect.width // Connect4Logic.COLS
        cell_height = self.board_rect.height // Connect4Logic.ROWS

        for row in range(Connect4Logic.ROWS):
            for col in range(Connect4Logic.COLS):
                x = self.board_rect.x + col * cell_width + cell_padding
                y = self.board_rect.y + row * cell_height + cell_padding
                w = cell_width - cell_padding * 2
                h = cell_height - cell_padding * 2

                cell_rect = pygame.Rect(x, y, w, h)

                value = self.logic.board[row][col]
                if value == Connect4Logic.PLAYER_ONE:
                    color = (220, 70, 70)
                elif value == Connect4Logic.PLAYER_TWO:
                    color = (235, 210, 70)
                else:
                    color = theme.SURFACE_ALT

                pygame.draw.ellipse(screen, color, cell_rect)

        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))