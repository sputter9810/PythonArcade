from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.memory_match.logic import MemoryMatchLogic
from arcade_app.ui import theme


class MemoryMatchGame(GameBase):
    game_id = "memory_match"
    title = "Memory Match"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = MemoryMatchLogic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.tile_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 640, 640)
        self.tile_rects: list[list[pygame.Rect]] = []

        self.pending_resolution = False
        self.pending_timer = 0.0
        self.pending_delay = 0.7

        self.phase = "difficulty_select"
        self.difficulties = list(self.logic.DIFFICULTIES.keys())
        self.selected_difficulty_index = 0

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.tile_font = pygame.font.SysFont("arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

    def start_game(self) -> None:
        difficulty = self.difficulties[self.selected_difficulty_index]
        self.logic.reset(difficulty)
        self.pending_resolution = False
        self.pending_timer = 0.0
        self.phase = "game"

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        width = 720
        height = 560
        self.board_rect = pygame.Rect(
            (screen.get_width() - width) // 2,
            150,
            width,
            height,
        )

        padding = 16
        tile_w = (self.board_rect.width - padding * (self.logic.cols + 1)) // self.logic.cols
        tile_h = (self.board_rect.height - padding * (self.logic.rows + 1)) // self.logic.rows

        self.tile_rects = []
        for row in range(self.logic.rows):
            rect_row = []
            for col in range(self.logic.cols):
                x = self.board_rect.x + padding + col * (tile_w + padding)
                y = self.board_rect.y + padding + row * (tile_h + padding)
                rect_row.append(pygame.Rect(x, y, tile_w, tile_h))
            self.tile_rects.append(rect_row)

    def get_status_text(self) -> str:
        if self.logic.is_won:
            return "You matched all pairs!"
        if self.pending_resolution:
            return "Checking pair..."
        return f"Difficulty: {self.logic.difficulty}"

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.phase == "difficulty_select":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        from arcade_app.scenes.game_select_scene import GameSelectScene
                        self.app.scene_manager.go_to(GameSelectScene(self.app))
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_difficulty_index = max(0, self.selected_difficulty_index - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_difficulty_index = min(len(self.difficulties) - 1, self.selected_difficulty_index + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_game()
            return

        if self.pending_resolution:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.phase = "difficulty_select"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for row in range(self.logic.rows):
                    for col in range(self.logic.cols):
                        rect = self.tile_rects[row][col]
                        if rect.collidepoint(mouse_pos):
                            moved = self.logic.select_tile(row, col)
                            if moved and len(self.logic.selected_tiles) == 2:
                                self.pending_resolution = True
                                self.pending_timer = self.pending_delay
                            return

    def update(self, dt: float) -> None:
        if self.pending_resolution:
            self.pending_timer -= dt
            if self.pending_timer <= 0:
                self.logic.resolve_selected_tiles()
                self.pending_resolution = False
                self.pending_timer = 0.0

    def render_difficulty_select(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None

        title = self.title_font.render("Memory Match", True, theme.TEXT)
        subtitle = self.info_font.render("Choose a difficulty", True, theme.TEXT)
        controls = self.info_font.render(
            "Up/Down: Select  |  Enter: Start  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 140)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)))

        panel = pygame.Rect((screen.get_width() - 520) // 2, 220, 520, 240)
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)

        for i, difficulty in enumerate(self.difficulties):
            row = pygame.Rect(panel.x + 24, panel.y + 28 + i * 64, panel.width - 48, 46)
            selected = i == self.selected_difficulty_index
            fill = theme.SURFACE_ALT if selected else theme.SURFACE
            border = theme.ACCENT if selected else theme.SURFACE_ALT

            pygame.draw.rect(screen, fill, row, border_radius=theme.RADIUS_MEDIUM)
            pygame.draw.rect(screen, border, row, width=2, border_radius=theme.RADIUS_MEDIUM)

            label = self.info_font.render(difficulty, True, theme.TEXT)
            screen.blit(label, label.get_rect(center=row.center))

    def render_game(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.tile_font is not None
        assert self.small_font is not None

        self.rebuild_layout(screen)

        title = self.title_font.render("Memory Match", True, theme.TEXT)
        status = self.info_font.render(self.get_status_text(), True, theme.TEXT)
        moves = self.info_font.render(f"Moves: {self.logic.moves}", True, theme.TEXT)
        controls = self.info_font.render(
            "Click tiles to reveal  |  F5: Back to Difficulty Select  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(moves, moves.get_rect(center=(screen.get_width() // 2, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        for row in range(self.logic.rows):
            for col in range(self.logic.cols):
                rect = self.tile_rects[row][col]
                value = self.logic.board[row][col]
                is_revealed = self.logic.revealed[row][col]
                is_matched = self.logic.matched[row][col]

                if is_matched or is_revealed:
                    fill = self.logic.color_map[value]
                else:
                    fill = theme.SURFACE_ALT

                pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MEDIUM)

                if is_revealed or is_matched:
                    text = self.tile_font.render(str(value), True, theme.TEXT)
                else:
                    text = self.tile_font.render("?", True, theme.MUTED_TEXT)

                screen.blit(text, text.get_rect(center=rect.center))

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(theme.BACKGROUND)

        if self.phase == "difficulty_select":
            self.render_difficulty_select(screen)
        else:
            self.render_game(screen)