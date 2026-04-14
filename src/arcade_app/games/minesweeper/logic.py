from __future__ import annotations

import random


class MinesweeperLogic:
    ROWS = 10
    COLS = 10
    MINE_COUNT = 12

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.mines: set[tuple[int, int]] = set()
        self.revealed = [[False for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.flagged = [[False for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.adjacent_counts = [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]

        self.is_game_over = False
        self.is_won = False
        self.first_click_done = False

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.ROWS and 0 <= col < self.COLS

    def neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        cells = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = row + dr
                nc = col + dc
                if self.in_bounds(nr, nc):
                    cells.append((nr, nc))
        return cells

    def place_mines(self, safe_row: int, safe_col: int) -> None:
        forbidden = {(safe_row, safe_col), *self.neighbors(safe_row, safe_col)}

        available = [
            (row, col)
            for row in range(self.ROWS)
            for col in range(self.COLS)
            if (row, col) not in forbidden
        ]

        self.mines = set(random.sample(available, self.MINE_COUNT))
        self.calculate_adjacent_counts()

    def calculate_adjacent_counts(self) -> None:
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if (row, col) in self.mines:
                    self.adjacent_counts[row][col] = -1
                else:
                    count = sum((nr, nc) in self.mines for nr, nc in self.neighbors(row, col))
                    self.adjacent_counts[row][col] = count

    def reveal(self, row: int, col: int) -> bool:
        if self.is_game_over or self.is_won:
            return False

        if not self.in_bounds(row, col):
            return False

        if self.flagged[row][col] or self.revealed[row][col]:
            return False

        if not self.first_click_done:
            self.place_mines(row, col)
            self.first_click_done = True

        self.revealed[row][col] = True

        if (row, col) in self.mines:
            self.is_game_over = True
            return True

        if self.adjacent_counts[row][col] == 0:
            self.flood_reveal(row, col)

        self.check_win()
        return True

    def flood_reveal(self, row: int, col: int) -> None:
        stack = [(row, col)]
        visited = set()

        while stack:
            current_row, current_col = stack.pop()
            if (current_row, current_col) in visited:
                continue
            visited.add((current_row, current_col))

            for nr, nc in self.neighbors(current_row, current_col):
                if self.flagged[nr][nc] or self.revealed[nr][nc]:
                    continue
                if (nr, nc) in self.mines:
                    continue

                self.revealed[nr][nc] = True
                if self.adjacent_counts[nr][nc] == 0:
                    stack.append((nr, nc))

    def toggle_flag(self, row: int, col: int) -> bool:
        if self.is_game_over or self.is_won:
            return False

        if not self.in_bounds(row, col):
            return False

        if self.revealed[row][col]:
            return False

        self.flagged[row][col] = not self.flagged[row][col]
        return True

    def check_win(self) -> None:
        safe_cells = self.ROWS * self.COLS - self.MINE_COUNT
        revealed_safe = 0

        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.revealed[row][col] and (row, col) not in self.mines:
                    revealed_safe += 1

        if revealed_safe == safe_cells:
            self.is_won = True

    def get_flag_count(self) -> int:
        total = 0
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.flagged[row][col]:
                    total += 1
        return total