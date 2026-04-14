from __future__ import annotations

import random
import string


class MemoryMatchLogic:
    DIFFICULTIES = {
        "Easy": (4, 4),
        "Medium": (4, 6),
        "Hard": (6, 6),
    }

    PAIR_COLORS = [
        (220, 90, 90),
        (90, 180, 110),
        (90, 130, 220),
        (220, 190, 80),
        (170, 110, 220),
        (80, 200, 200),
        (240, 140, 90),
        (160, 220, 100),
        (255, 120, 160),
        (130, 180, 255),
        (210, 160, 100),
        (180, 220, 180),
        (255, 180, 120),
        (160, 140, 240),
        (100, 210, 170),
        (230, 120, 120),
        (120, 120, 230),
        (230, 210, 120),
    ]

    def __init__(self) -> None:
        self.difficulty = "Easy"
        self.reset(self.difficulty)

    def reset(self, difficulty: str | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty

        self.rows, self.cols = self.DIFFICULTIES[self.difficulty]
        pair_count = (self.rows * self.cols) // 2

        values = list(string.ascii_uppercase[:pair_count]) * 2
        random.shuffle(values)

        self.board: list[list[str]] = []
        index = 0
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(values[index])
                index += 1
            self.board.append(row)

        self.color_map: dict[str, tuple[int, int, int]] = {}
        for i, letter in enumerate(string.ascii_uppercase[:pair_count]):
            self.color_map[letter] = self.PAIR_COLORS[i % len(self.PAIR_COLORS)]

        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.matched = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.selected_tiles: list[tuple[int, int]] = []
        self.moves = 0
        self.matches_found = 0
        self.is_won = False

    def can_select(self, row: int, col: int) -> bool:
        if self.is_won:
            return False
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        if self.matched[row][col] or self.revealed[row][col]:
            return False
        if len(self.selected_tiles) >= 2:
            return False
        return True

    def select_tile(self, row: int, col: int) -> bool:
        if not self.can_select(row, col):
            return False

        self.revealed[row][col] = True
        self.selected_tiles.append((row, col))

        if len(self.selected_tiles) == 2:
            self.moves += 1

        return True

    def resolve_selected_tiles(self) -> None:
        if len(self.selected_tiles) != 2:
            return

        (row1, col1), (row2, col2) = self.selected_tiles
        value1 = self.board[row1][col1]
        value2 = self.board[row2][col2]

        if value1 == value2:
            self.matched[row1][col1] = True
            self.matched[row2][col2] = True
            self.matches_found += 1

            if self.matches_found == (self.rows * self.cols) // 2:
                self.is_won = True
        else:
            self.revealed[row1][col1] = False
            self.revealed[row2][col2] = False

        self.selected_tiles.clear()