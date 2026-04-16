from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class CrosswordGame(GameBase):
    game_id = "crossword"
    title = "Crossword"

    WORD_SETS = [
        {
            "rows": ["BALL", "AREA", "LEAD", "LADY"],
            "clues": {
                "BALL": "A round object used in many sports",
                "AREA": "A region or amount of space",
                "LEAD": "To guide or go in front",
                "LADY": "A polite term for a woman",
            },
        },
        {
            "rows": ["MATE", "AREA", "TEAR", "EARN"],
            "clues": {
                "MATE": "A friend or companion",
                "AREA": "A region or amount of space",
                "TEAR": "A drop from the eye or a rip",
                "EARN": "To receive through effort or work",
            },
        },
        {
            "rows": ["BARE", "AREA", "REAL", "EARN"],
            "clues": {
                "BARE": "Without covering",
                "AREA": "A region or amount of space",
                "REAL": "True or genuine",
                "EARN": "To receive through effort or work",
            },
        },
        {
            "rows": ["CARE", "AREA", "REAR", "EARN"],
            "clues": {
                "CARE": "To look after or be concerned",
                "AREA": "A region or amount of space",
                "REAR": "The back part of something",
                "EARN": "To receive through effort or work",
            },
        },
        {
            "rows": ["DARE", "AREA", "REAR", "EARN"],
            "clues": {
                "DARE": "To challenge or have courage",
                "AREA": "A region or amount of space",
                "REAR": "The back part of something",
                "EARN": "To receive through effort or work",
            },
        },
    ]

    def __init__(self, app):
        super().__init__(app)
        self.ui: GameUI | None = None
        self.cell_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.clue_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1120, 640)
        self.board_rect = pygame.Rect(0, 0, 320, 320)

        self.solution_grid: list[list[str]] = []
        self.input_grid: list[list[str]] = []
        self.number_grid: list[list[int | None]] = []

        self.rows = 0
        self.cols = 0

        self.selected = (0, 0)
        self.direction = "across"

        self.completed = False
        self.paused = False
        self.filled_count = 0

        self.across_clues: list[tuple[int, str, tuple[int, int], int]] = []
        self.down_clues: list[tuple[int, str, tuple[int, int], int]] = []

    def enter(self):
        self.ui = GameUI()
        self.cell_font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 12, bold=True)
        self.clue_font = pygame.font.SysFont("arial", 18)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1120) // 2, 165, 1120, 640)
        self.board_rect = pygame.Rect(self.play_rect.left + 60, self.play_rect.top + 90, 320, 320)

    def generate_puzzle(self) -> None:
        word_set = random.choice(self.WORD_SETS)
        rows = word_set["rows"]
        size = len(rows)

        self.solution_grid = [list(word) for word in rows]
        self.rows = size
        self.cols = size

        self.input_grid = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        self.number_grid = self.build_number_grid()

        self.across_clues = []
        self.down_clues = []

        clue_num = 1
        for r in range(self.rows):
            word = "".join(self.solution_grid[r])
            self.across_clues.append((clue_num, word_set["clues"][word], (r, 0), self.cols))
            clue_num += 1

        for c in range(self.cols):
            word = "".join(self.solution_grid[r][c] for r in range(self.rows))
            clue_text = word_set["clues"].get(word, f"Generated vertical word: {word}")
            self.down_clues.append((clue_num, clue_text, (0, c), self.rows))
            clue_num += 1

    def reset_game(self):
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.generate_puzzle()

        self.selected = (0, 0)
        self.direction = "across"
        self.completed = False
        self.paused = False
        self.filled_count = 0

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = self.filled_count * 50
        payload["round"] = self.filled_count
        return payload

    def leave_to_menu(self):
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def build_number_grid(self) -> list[list[int | None]]:
        numbers = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        clue_num = 1
        for r in range(self.rows):
            numbers[r][0] = clue_num
            clue_num += 1
        for c in range(self.cols):
            numbers[0][c] = clue_num
            clue_num += 1
        return numbers

    def check_complete(self) -> None:
        self.completed = True
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.input_grid[r][c] != self.solution_grid[r][c]:
                    self.completed = False
                if self.input_grid[r][c]:
                    count += 1
        self.filled_count = count

    def move_selection(self, dr: int, dc: int) -> None:
        r, c = self.selected
        nr = max(0, min(self.rows - 1, r + dr))
        nc = max(0, min(self.cols - 1, c + dc))
        self.selected = (nr, nc)

    def advance_cursor(self) -> None:
        r, c = self.selected
        if self.direction == "across":
            c = (c + 1) % self.cols
        else:
            r = (r + 1) % self.rows
        self.selected = (r, c)

    def set_letter(self, letter: str) -> None:
        if self.completed or self.paused:
            return
        r, c = self.selected
        self.input_grid[r][c] = letter
        self.check_complete()
        self.advance_cursor()

    def clear_letter(self) -> None:
        if self.completed or self.paused:
            return
        r, c = self.selected
        self.input_grid[r][c] = ""
        self.check_complete()

    def cell_in_clue(self, cell: tuple[int, int], start: tuple[int, int], length: int, direction: str) -> bool:
        r, c = cell
        sr, sc = start
        if direction == "across":
            return r == sr and sc <= c < sc + length
        return c == sc and sr <= r < sr + length

    def active_clues(self) -> tuple[str | None, str | None]:
        cell = self.selected
        across = None
        down = None

        for number, clue, start, length in self.across_clues:
            if self.cell_in_clue(cell, start, length, "across"):
                across = f"{number}. {clue}"
                break

        for number, clue, start, length in self.down_clues:
            if self.cell_in_clue(cell, start, length, "down"):
                down = f"{number}. {clue}"
                break

        return across, down

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif e.key == pygame.K_p and not self.completed:
                    self.paused = not self.paused
                elif e.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif e.key == pygame.K_TAB:
                    self.direction = "down" if self.direction == "across" else "across"
                elif e.key == pygame.K_LEFT:
                    self.move_selection(0, -1)
                elif e.key == pygame.K_RIGHT:
                    self.move_selection(0, 1)
                elif e.key == pygame.K_UP:
                    self.move_selection(-1, 0)
                elif e.key == pygame.K_DOWN:
                    self.move_selection(1, 0)
                elif e.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    self.clear_letter()
                elif e.unicode and e.unicode.isalpha():
                    self.set_letter(e.unicode.upper())

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.completed:
                    self.reset_game()
                    continue
                if self.paused:
                    continue
                if self.board_rect.collidepoint(e.pos):
                    cell_size = self.board_rect.width // self.cols
                    col = (e.pos[0] - self.board_rect.x) // cell_size
                    row = (e.pos[1] - self.board_rect.y) // cell_size
                    if self.selected == (row, col):
                        self.direction = "down" if self.direction == "across" else "across"
                    self.selected = (row, col)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def wrap_text(self, text: str, max_chars: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def render(self, screen):
        assert self.ui is not None
        assert self.cell_font is not None
        assert self.small_font is not None
        assert self.clue_font is not None

        screen.fill(theme.BACKGROUND)
        self.rebuild_layout(screen)

        self.ui.draw_header(screen, "Crossword", "Fill the grid using the clues. Arrow Keys move. Tab switches direction.")
        self.ui.draw_stats_row(
            screen,
            [
                f"Filled: {self.filled_count}",
                f"Direction: {self.direction.title()}",
                f"Size: {self.rows}x{self.cols}",
            ],
        )
        sub = "Each run chooses a different generated mini-crossword." if not self.completed else "Crossword completed."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "Arrow Keys Only  |  Tab: Switch Direction  |  F5: New Puzzle  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        cell_size = self.board_rect.width // self.cols
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    self.board_rect.x + c * cell_size,
                    self.board_rect.y + r * cell_size,
                    cell_size,
                    cell_size,
                )

                fill = theme.SURFACE_ALT
                if (r, c) == self.selected:
                    fill = (84, 102, 132)

                pygame.draw.rect(screen, fill, rect)
                pygame.draw.rect(screen, theme.TEXT, rect, 1)

                number = self.number_grid[r][c]
                if number is not None:
                    surface = self.small_font.render(str(number), True, theme.MUTED_TEXT)
                    screen.blit(surface, (rect.x + 4, rect.y + 2))

                value = self.input_grid[r][c]
                if value:
                    color = theme.ACCENT if value == self.solution_grid[r][c] else theme.WARNING
                    surface = self.cell_font.render(value, True, color)
                    screen.blit(surface, surface.get_rect(center=rect.center))

        panel_rect = pygame.Rect(self.board_rect.right + 40, self.board_rect.y, 340, self.board_rect.height)
        pygame.draw.rect(screen, theme.SURFACE, panel_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        across, down = self.active_clues()
        title = self.clue_font.render("Clues", True, theme.TEXT)
        screen.blit(title, (panel_rect.x + 18, panel_rect.y + 16))

        y = panel_rect.y + 56
        for label, clue in [("Across", across), ("Down", down)]:
            heading = self.clue_font.render(label, True, theme.ACCENT)
            screen.blit(heading, (panel_rect.x + 18, y))
            y += 28

            clue_text = clue or "-"
            wrapped = self.wrap_text(clue_text, 34)
            for line in wrapped:
                surface = self.clue_font.render(line, True, theme.TEXT)
                screen.blit(surface, (panel_rect.x + 18, y))
                y += 24
            y += 16

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Crossword Complete",
                f"Filled Cells: {self.filled_count}",
                "Nice solve.",
            )