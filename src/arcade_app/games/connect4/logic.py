from __future__ import annotations

import random


class Connect4Logic:
    ROWS = 6
    COLS = 7
    EMPTY = ""
    PLAYER_ONE = "R"
    PLAYER_TWO = "Y"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board = [
            [self.EMPTY for _ in range(self.COLS)]
            for _ in range(self.ROWS)
        ]
        self.current_player = self.PLAYER_ONE
        self.winner: str | None = None
        self.is_draw = False
        self.vs_computer = False
        self.computer_player = self.PLAYER_TWO

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset()
        self.vs_computer = vs_computer

    def is_valid_column(self, col: int) -> bool:
        return 0 <= col < self.COLS and self.board[0][col] == self.EMPTY

    def get_valid_columns(self) -> list[int]:
        return [col for col in range(self.COLS) if self.is_valid_column(col)]

    def get_drop_row(self, col: int) -> int | None:
        if not self.is_valid_column(col):
            return None

        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == self.EMPTY:
                return row
        return None

    def make_move(self, col: int) -> bool:
        if self.winner is not None or self.is_draw:
            return False

        row = self.get_drop_row(col)
        if row is None:
            return False

        self.board[row][col] = self.current_player
        self.check_game_state(row, col)

        if self.winner is None and not self.is_draw:
            self.current_player = (
                self.PLAYER_TWO if self.current_player == self.PLAYER_ONE else self.PLAYER_ONE
            )

        return True

    def check_game_state(self, row: int, col: int) -> None:
        piece = self.board[row][col]
        if piece == self.EMPTY:
            return

        directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]

        for dr, dc in directions:
            count = 1
            count += self.count_direction(row, col, dr, dc, piece)
            count += self.count_direction(row, col, -dr, -dc, piece)
            if count >= 4:
                self.winner = piece
                return

        if not self.get_valid_columns():
            self.is_draw = True

    def count_direction(self, row: int, col: int, dr: int, dc: int, piece: str) -> int:
        count = 0
        r = row + dr
        c = col + dc

        while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] == piece:
            count += 1
            r += dr
            c += dc

        return count

    def make_computer_move(self) -> bool:
        if not self.vs_computer:
            return False

        if self.current_player != self.computer_player:
            return False

        if self.winner is not None or self.is_draw:
            return False

        move = self.find_best_simple_move()
        if move is None:
            return False

        return self.make_move(move)

    def find_best_simple_move(self) -> int | None:
        valid_cols = self.get_valid_columns()
        if not valid_cols:
            return None

        # 1. Win immediately if possible
        for col in valid_cols:
            if self.is_winning_move(col, self.computer_player):
                return col

        # 2. Block opponent win
        human_player = self.PLAYER_ONE if self.computer_player == self.PLAYER_TWO else self.PLAYER_TWO
        for col in valid_cols:
            if self.is_winning_move(col, human_player):
                return col

        # 3. Prefer center columns
        center_order = [3, 2, 4, 1, 5, 0, 6]
        for col in center_order:
            if col in valid_cols:
                return col

        return random.choice(valid_cols)

    def is_winning_move(self, col: int, player: str) -> bool:
        row = self.get_drop_row(col)
        if row is None:
            return False

        self.board[row][col] = player
        won = self.has_winner_at(row, col, player)
        self.board[row][col] = self.EMPTY
        return won

    def has_winner_at(self, row: int, col: int, piece: str) -> bool:
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        for dr, dc in directions:
            count = 1
            count += self.count_direction(row, col, dr, dc, piece)
            count += self.count_direction(row, col, -dr, -dc, piece)
            if count >= 4:
                return True

        return False