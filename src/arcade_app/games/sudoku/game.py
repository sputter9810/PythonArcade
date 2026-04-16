from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class SudokuGame(GameBase):
    game_id = "sudoku"
    title = "Sudoku"

    DIFFICULTIES = {
        "Easy": 40,
        "Medium": 32,
        "Hard": 26,
    }

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.value_font: pygame.font.Font | None = None
        self.note_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1120, 640)
        self.board_rect = pygame.Rect(0, 0, 540, 540)
        self.diff_buttons: dict[str, pygame.Rect] = {}

        self.solution: list[list[int]] = []
        self.givens: list[list[int]] = []
        self.board: list[list[int]] = []
        self.notes: list[list[set[int]]] = []

        self.selected_row = 0
        self.selected_col = 0
        self.note_mode = False
        self.difficulty = "Medium"

        self.moves = 0
        self.mistakes = 0
        self.completed = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.value_font = pygame.font.SysFont("arial", 28, bold=True)
        self.note_font = pygame.font.SysFont("arial", 12)
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1120) // 2, 165, 1120, 640)
        self.board_rect = pygame.Rect(0, 0, 540, 540)
        self.board_rect.x = self.play_rect.left + 70
        self.board_rect.y = self.play_rect.top + 70

        self.diff_buttons = {
            "Easy": pygame.Rect(self.play_rect.right - 290, self.play_rect.top + 60, 90, 38),
            "Medium": pygame.Rect(self.play_rect.right - 190, self.play_rect.top + 60, 90, 38),
            "Hard": pygame.Rect(self.play_rect.right - 90, self.play_rect.top + 60, 90, 38),
        }

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.solution = self.generate_solution()
        self.givens = self.generate_puzzle(self.solution, self.DIFFICULTIES[self.difficulty])
        self.board = [row[:] for row in self.givens]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]

        self.selected_row = 0
        self.selected_col = 0
        self.note_mode = False
        self.moves = 0
        self.mistakes = 0
        self.completed = False
        self.paused = False

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.reset_game()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = max(0, 1000 - self.mistakes * 100)
        payload["round"] = self.moves
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def is_given(self, row: int, col: int) -> bool:
        return self.givens[row][col] != 0

    def valid_number(self, grid: list[list[int]], row: int, col: int, value: int) -> bool:
        for i in range(9):
            if grid[row][i] == value:
                return False
            if grid[i][col] == value:
                return False

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if grid[r][c] == value:
                    return False

        return True

    def find_empty(self, grid: list[list[int]]) -> tuple[int, int] | None:
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    return r, c
        return None

    def solve_grid(self, grid: list[list[int]]) -> bool:
        empty = self.find_empty(grid)
        if empty is None:
            return True

        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for value in numbers:
            if self.valid_number(grid, row, col, value):
                grid[row][col] = value
                if self.solve_grid(grid):
                    return True
                grid[row][col] = 0

        return False

    def generate_solution(self) -> list[list[int]]:
        grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solve_grid(grid)
        return grid

    def count_solutions(self, grid: list[list[int]], limit: int = 2) -> int:
        empty = self.find_empty(grid)
        if empty is None:
            return 1

        row, col = empty
        count = 0
        for value in range(1, 10):
            if self.valid_number(grid, row, col, value):
                grid[row][col] = value
                count += self.count_solutions(grid, limit)
                grid[row][col] = 0
                if count >= limit:
                    return count
        return count

    def generate_puzzle(self, solution: list[list[int]], clues_target: int) -> list[list[int]]:
        puzzle = [row[:] for row in solution]
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        filled = 81
        for row, col in cells:
            if filled <= clues_target:
                break

            backup = puzzle[row][col]
            puzzle[row][col] = 0

            grid_copy = [r[:] for r in puzzle]
            if self.count_solutions(grid_copy, limit=2) != 1:
                puzzle[row][col] = backup
            else:
                filled -= 1

        return puzzle

    def draw_diff_button(self, screen: pygame.Surface, label: str, rect: pygame.Rect, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

    def set_value(self, value: int) -> None:
        if self.completed or self.paused or self.is_given(self.selected_row, self.selected_col):
            return

        if self.note_mode and value != 0:
            notes = self.notes[self.selected_row][self.selected_col]
            if value in notes:
                notes.remove(value)
            else:
                notes.add(value)
            self.moves += 1
            return

        if value == 0:
            if self.board[self.selected_row][self.selected_col] != 0:
                self.board[self.selected_row][self.selected_col] = 0
                self.notes[self.selected_row][self.selected_col].clear()
                self.moves += 1
            return

        self.moves += 1
        if value != self.solution[self.selected_row][self.selected_col]:
            self.mistakes += 1
            return

        self.board[self.selected_row][self.selected_col] = value
        self.notes[self.selected_row][self.selected_col].clear()
        self.check_complete()

    def check_complete(self) -> None:
        self.completed = self.board == self.solution

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_p and not self.completed:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                elif event.key == pygame.K_TAB:
                    self.note_mode = not self.note_mode
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_col = max(0, self.selected_col - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_col = min(8, self.selected_col + 1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_row = max(0, self.selected_row - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_row = min(8, self.selected_row + 1)
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
                    self.set_value(0)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    self.set_value(event.key - pygame.K_0)
                elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
                    self.set_value(event.key - pygame.K_KP0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in self.diff_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.set_difficulty(label)
                        return

                if self.completed:
                    self.reset_game()
                    continue
                if not self.board_rect.collidepoint(event.pos):
                    continue
                cell_size = self.board_rect.width // 9
                self.selected_col = (event.pos[0] - self.board_rect.x) // cell_size
                self.selected_row = (event.pos[1] - self.board_rect.y) // cell_size

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render_notes(self, screen: pygame.Surface, row: int, col: int, rect: pygame.Rect) -> None:
        assert self.note_font is not None
        notes = sorted(self.notes[row][col])
        for number in notes:
            note_row = (number - 1) // 3
            note_col = (number - 1) % 3
            x = rect.x + 8 + note_col * 18
            y = rect.y + 6 + note_row * 16
            surface = self.note_font.render(str(number), True, theme.MUTED_TEXT)
            screen.blit(surface, (x, y))

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.value_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Sudoku",
            "Arrow Keys / WASD move. 1-9 enters values. Tab toggles notes.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Difficulty: {self.difficulty}",
                f"Moves: {self.moves}",
                f"Mistakes: {self.mistakes}",
                f"Mode: {'Notes' if self.note_mode else 'Values'}",
            ],
        )
        sub = "Generated puzzle with a unique solution." if not self.completed else "Puzzle solved."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  Tab: Notes  |  F5: New Puzzle  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for label, rect in self.diff_buttons.items():
            self.draw_diff_button(screen, label, rect, label == self.difficulty)

        cell_size = self.board_rect.width // 9
        selected_rect = pygame.Rect(
            self.board_rect.x + self.selected_col * cell_size,
            self.board_rect.y + self.selected_row * cell_size,
            cell_size,
            cell_size,
        )
        pygame.draw.rect(screen, (72, 88, 112), selected_rect, border_radius=4)

        for r in range(9):
            for c in range(9):
                rect = pygame.Rect(
                    self.board_rect.x + c * cell_size,
                    self.board_rect.y + r * cell_size,
                    cell_size,
                    cell_size,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=2)

                value = self.board[r][c]
                if value:
                    color = theme.TEXT if self.is_given(r, c) else theme.ACCENT
                    surface = self.value_font.render(str(value), True, color)
                    screen.blit(surface, surface.get_rect(center=rect.center))
                else:
                    self.render_notes(screen, r, c, rect)

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            x = self.board_rect.x + i * cell_size
            y = self.board_rect.y + i * cell_size
            pygame.draw.line(screen, theme.TEXT, (x, self.board_rect.y), (x, self.board_rect.bottom), width)
            pygame.draw.line(screen, theme.TEXT, (self.board_rect.x, y), (self.board_rect.right, y), width)

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Puzzle Complete",
                f"Mistakes: {self.mistakes}",
                f"Moves: {self.moves}  |  Difficulty: {self.difficulty}",
            )