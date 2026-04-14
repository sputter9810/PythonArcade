from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme


class SudokuGame(GameBase):
    game_id = "sudoku"
    title = "Sudoku"

    BASE_SOLUTION = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    def __init__(self, app) -> None:
        super().__init__(app)

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.cell_font: pygame.font.Font | None = None
        self.note_font: pygame.font.Font | None = None

        self.board_rect = pygame.Rect(0, 0, 630, 630)
        self.grid: list[list[int]] = []
        self.solution: list[list[int]] = []
        self.fixed: list[list[bool]] = []
        self.notes: list[list[set[int]]] = []
        self.wrong_marks: dict[tuple[int, int], int] = {}

        self.selected_cell: tuple[int, int] | None = None
        self.note_mode = False
        self.lives = 3
        self.is_won = False
        self.is_game_over = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.cell_font = pygame.font.SysFont("arial", 30, bold=True)
        self.note_font = pygame.font.SysFont("arial", 12, bold=True)
        self.reset_game()

    def shuffled_solution(self) -> list[list[int]]:
        board = [row[:] for row in self.BASE_SOLUTION]

        # shuffle row groups
        row_groups = [board[0:3], board[3:6], board[6:9]]
        random.shuffle(row_groups)
        board = [row for group in row_groups for row in group]

        # shuffle rows within groups
        new_board: list[list[int]] = []
        for start in range(0, 9, 3):
            group = board[start:start + 3]
            random.shuffle(group)
            new_board.extend(group)
        board = new_board

        # transpose, do same for columns
        board = [list(row) for row in zip(*board)]

        col_groups = [board[0:3], board[3:6], board[6:9]]
        random.shuffle(col_groups)
        board = [col for group in col_groups for col in group]

        new_board = []
        for start in range(0, 9, 3):
            group = board[start:start + 3]
            random.shuffle(group)
            new_board.extend(group)
        board = new_board

        board = [list(row) for row in zip(*board)]

        # remap digits
        digits = list(range(1, 10))
        shuffled_digits = digits[:]
        random.shuffle(shuffled_digits)
        mapping = {digits[i]: shuffled_digits[i] for i in range(9)}

        for r in range(9):
            for c in range(9):
                board[r][c] = mapping[board[r][c]]

        return board

    def create_puzzle(self, solution: list[list[int]], remove_count: int = 45) -> list[list[int]]:
        puzzle = [row[:] for row in solution]
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        for i in range(remove_count):
            r, c = cells[i]
            puzzle[r][c] = 0

        return puzzle

    def reset_game(self) -> None:
        self.solution = self.shuffled_solution()
        self.grid = self.create_puzzle(self.solution, remove_count=45)
        self.fixed = [[value != 0 for value in row] for row in self.grid]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.wrong_marks = {}
        self.selected_cell = None
        self.note_mode = False
        self.lives = 3
        self.is_won = False
        self.is_game_over = False

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.board_rect = pygame.Rect(
            (screen.get_width() - 630) // 2,
            160,
            630,
            630,
        )

    def check_win(self) -> None:
        self.is_won = self.grid == self.solution
        if self.is_won:
            self.is_game_over = False

    def note_is_valid(self, row: int, col: int, number: int) -> bool:
        for c in range(9):
            if c != col and self.grid[row][c] == number:
                return False

        for r in range(9):
            if r != row and self.grid[r][col] == number:
                return False

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col) and self.grid[r][c] == number:
                    return False

        return True

    def handle_number_input(self, number: int) -> None:
        if self.selected_cell is None or self.is_won or self.is_game_over:
            return

        row, col = self.selected_cell
        if self.fixed[row][col]:
            return

        if self.note_mode:
            if self.grid[row][col] != 0 or not self.note_is_valid(row, col, number):
                return

            if number in self.notes[row][col]:
                self.notes[row][col].remove(number)
            else:
                self.notes[row][col].add(number)
            return

        self.notes[row][col].clear()

        correct_value = self.solution[row][col]
        if number == correct_value:
            self.grid[row][col] = number
            self.wrong_marks.pop((row, col), None)
            self.check_win()
        else:
            self.wrong_marks[(row, col)] = number
            self.lives -= 1
            if self.lives <= 0:
                self.is_game_over = True

    def clear_selected(self) -> None:
        if self.selected_cell is None or self.is_won or self.is_game_over:
            return

        row, col = self.selected_cell
        if self.fixed[row][col]:
            return

        self.grid[row][col] = 0
        self.notes[row][col].clear()
        self.wrong_marks.pop((row, col), None)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.game_select_scene import GameSelectScene
                    self.app.scene_manager.go_to(GameSelectScene(self.app))
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif event.key == pygame.K_n:
                    if not self.is_won and not self.is_game_over:
                        self.note_mode = not self.note_mode
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
                    self.clear_selected()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    self.handle_number_input(event.key - pygame.K_0)
                elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
                    self.handle_number_input(event.key - pygame.K_KP0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell_size = self.board_rect.width // 9

                if self.board_rect.collidepoint(event.pos):
                    col = (event.pos[0] - self.board_rect.x) // cell_size
                    row = (event.pos[1] - self.board_rect.y) // cell_size
                    self.selected_cell = (row, col)

    def update(self, dt: float) -> None:
        return

    def draw_notes(self, screen: pygame.Surface, row: int, col: int, rect: pygame.Rect) -> None:
        assert self.note_font is not None

        notes = self.notes[row][col]
        if not notes:
            return

        mini_w = rect.width // 3
        mini_h = rect.height // 3

        for number in sorted(notes):
            mini_row = (number - 1) // 3
            mini_col = (number - 1) % 3

            x = rect.x + mini_col * mini_w + mini_w // 2
            y = rect.y + mini_row * mini_h + mini_h // 2

            text = self.note_font.render(str(number), True, theme.MUTED_TEXT)
            screen.blit(text, text.get_rect(center=(x, y)))

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.cell_font is not None
        assert self.note_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Sudoku", True, theme.TEXT)

        if self.is_won:
            status_text = "Puzzle complete!"
        elif self.is_game_over:
            status_text = "Out of lives"
        else:
            status_text = "Fill the grid so every row, column, and box contains 1-9"

        status = self.info_font.render(status_text, True, theme.TEXT)
        lives = self.info_font.render(f"Lives: {self.lives}", True, theme.TEXT)
        mode_text = "Mode: Notes" if self.note_mode else "Mode: Entry"
        mode = self.info_font.render(mode_text, True, theme.ACCENT if self.note_mode else theme.TEXT)
        controls = self.info_font.render(
            "Click cell  |  Type 1-9  |  N: Notes  |  Backspace/Delete: Clear  |  F5: New Puzzle  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(lives, lives.get_rect(center=(screen.get_width() // 2 - 110, 115)))
        screen.blit(mode, mode.get_rect(center=(screen.get_width() // 2 + 110, 115)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)

        cell_size = self.board_rect.width // 9

        if self.selected_cell is not None:
            row, col = self.selected_cell
            highlight_rect = pygame.Rect(
                self.board_rect.x + col * cell_size,
                self.board_rect.y + row * cell_size,
                cell_size,
                cell_size,
            )
            highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            highlight.fill((100, 170, 240, 80))
            screen.blit(highlight, highlight_rect.topleft)

        for row in range(9):
            for col in range(9):
                x = self.board_rect.x + col * cell_size
                y = self.board_rect.y + row * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)

                pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1)

                value = self.grid[row][col]
                wrong_value = self.wrong_marks.get((row, col))

                if value != 0:
                    color = theme.TEXT if self.fixed[row][col] else theme.ACCENT
                    text = self.cell_font.render(str(value), True, color)
                    screen.blit(text, text.get_rect(center=rect.center))
                elif wrong_value is not None:
                    text = self.cell_font.render(str(wrong_value), True, theme.DANGER)
                    screen.blit(text, text.get_rect(center=rect.center))
                else:
                    self.draw_notes(screen, row, col, rect)

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            pygame.draw.line(
                screen,
                theme.TEXT,
                (self.board_rect.x, self.board_rect.y + i * cell_size),
                (self.board_rect.right, self.board_rect.y + i * cell_size),
                width,
            )
            pygame.draw.line(
                screen,
                theme.TEXT,
                (self.board_rect.x + i * cell_size, self.board_rect.y),
                (self.board_rect.x + i * cell_size, self.board_rect.bottom),
                width,
            )