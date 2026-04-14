from __future__ import annotations

import random


class Game2048Logic:
    SIZE = 4
    TARGET = 2048

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.grid = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.score = 0
        self.has_won = False
        self.is_game_over = False
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self) -> None:
        empty_cells = [
            (row, col)
            for row in range(self.SIZE)
            for col in range(self.SIZE)
            if self.grid[row][col] == 0
        ]
        if not empty_cells:
            return

        row, col = random.choice(empty_cells)
        self.grid[row][col] = 4 if random.random() < 0.1 else 2

    def compress_line(self, line: list[int]) -> tuple[list[int], int]:
        filtered = [value for value in line if value != 0]
        merged: list[int] = []
        score_gain = 0
        i = 0

        while i < len(filtered):
            if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
                new_value = filtered[i] * 2
                merged.append(new_value)
                score_gain += new_value
                i += 2
            else:
                merged.append(filtered[i])
                i += 1

        while len(merged) < self.SIZE:
            merged.append(0)

        return merged, score_gain

    def move_left(self) -> bool:
        moved = False

        for row in range(self.SIZE):
            original = self.grid[row][:]
            compressed, gained = self.compress_line(original)
            self.grid[row] = compressed
            self.score += gained

            if self.grid[row] != original:
                moved = True

        return moved

    def move_right(self) -> bool:
        moved = False

        for row in range(self.SIZE):
            original = self.grid[row][:]
            reversed_row = list(reversed(original))
            compressed, gained = self.compress_line(reversed_row)
            new_row = list(reversed(compressed))
            self.grid[row] = new_row
            self.score += gained

            if new_row != original:
                moved = True

        return moved

    def move_up(self) -> bool:
        moved = False

        for col in range(self.SIZE):
            original = [self.grid[row][col] for row in range(self.SIZE)]
            compressed, gained = self.compress_line(original)

            for row in range(self.SIZE):
                self.grid[row][col] = compressed[row]

            self.score += gained
            if compressed != original:
                moved = True

        return moved

    def move_down(self) -> bool:
        moved = False

        for col in range(self.SIZE):
            original = [self.grid[row][col] for row in range(self.SIZE)]
            reversed_col = list(reversed(original))
            compressed, gained = self.compress_line(reversed_col)
            new_col = list(reversed(compressed))

            for row in range(self.SIZE):
                self.grid[row][col] = new_col[row]

            self.score += gained
            if new_col != original:
                moved = True

        return moved

    def move(self, direction: str) -> bool:
        if self.has_won or self.is_game_over:
            return False

        moved = False

        if direction == "left":
            moved = self.move_left()
        elif direction == "right":
            moved = self.move_right()
        elif direction == "up":
            moved = self.move_up()
        elif direction == "down":
            moved = self.move_down()

        if moved:
            self.add_random_tile()
            self.update_state()

        return moved

    def update_state(self) -> None:
        for row in self.grid:
            for value in row:
                if value >= self.TARGET:
                    self.has_won = True

        if self.can_make_move():
            self.is_game_over = False
        else:
            self.is_game_over = True

    def can_make_move(self) -> bool:
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                value = self.grid[row][col]
                if value == 0:
                    return True

                if col + 1 < self.SIZE and self.grid[row][col + 1] == value:
                    return True

                if row + 1 < self.SIZE and self.grid[row + 1][col] == value:
                    return True

        return False