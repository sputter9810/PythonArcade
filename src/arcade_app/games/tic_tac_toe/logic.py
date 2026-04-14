from __future__ import annotations

import random


class TicTacToeLogic:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board = [""] * 9
        self.current_player = "X"
        self.winner: str | None = None
        self.is_draw = False
        self.vs_computer = False
        self.computer_player = "O"

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset()
        self.vs_computer = vs_computer

    def make_move(self, index: int) -> bool:
        if self.winner is not None or self.is_draw:
            return False

        if index < 0 or index >= 9:
            return False

        if self.board[index] != "":
            return False

        self.board[index] = self.current_player
        self.check_game_state()

        if self.winner is None and not self.is_draw:
            self.current_player = "O" if self.current_player == "X" else "X"

        return True

    def get_available_moves(self) -> list[int]:
        return [i for i, cell in enumerate(self.board) if cell == ""]

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
        available = self.get_available_moves()
        if not available:
            return None

        # 1. Win if possible
        for move in available:
            if self.is_winning_move(move, self.computer_player):
                return move

        # 2. Block opponent if needed
        human_player = "X" if self.computer_player == "O" else "O"
        for move in available:
            if self.is_winning_move(move, human_player):
                return move

        # 3. Take center
        if 4 in available:
            return 4

        # 4. Take a corner
        corners = [i for i in [0, 2, 6, 8] if i in available]
        if corners:
            return random.choice(corners)

        # 5. Take any side
        return random.choice(available)

    def is_winning_move(self, index: int, player: str) -> bool:
        if self.board[index] != "":
            return False

        original = self.board[index]
        self.board[index] = player
        won = self.has_winner(player)
        self.board[index] = original
        return won

    def has_winner(self, player: str) -> bool:
        winning_lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in winning_lines:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return True

        return False

    def check_game_state(self) -> None:
        winning_lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in winning_lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                return

        if all(cell != "" for cell in self.board):
            self.is_draw = True