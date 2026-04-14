from __future__ import annotations

import random


class BattleshipsLogic:
    BOARD_SIZE = 8
    SHIP_SIZES = [5, 4, 3, 3, 2]

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.player_board = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.enemy_board = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

        self.player_shots = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.enemy_shots = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

        self.vs_computer = True
        self.current_player = 1
        self.phase = "placement"
        self.placement_player = 1
        self.placing_ship_index = 0
        self.placement_orientation = "horizontal"

        self.winner: int | None = None
        self.ai_targets: list[tuple[int, int]] = []

    def set_mode(self, vs_computer: bool) -> None:
        self.vs_computer = vs_computer
        self.reset()

        if self.vs_computer:
            self.randomly_place_all_ships(self.enemy_board)
            self.phase = "placement"
            self.placement_player = 1

    def current_ship_size(self) -> int | None:
        if self.placing_ship_index >= len(self.SHIP_SIZES):
            return None
        return self.SHIP_SIZES[self.placing_ship_index]

    def get_active_board_for_placement(self) -> list[list[int]]:
        return self.player_board if self.placement_player == 1 else self.enemy_board

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def get_ship_cells(self, row: int, col: int, size: int, orientation: str) -> list[tuple[int, int]]:
        cells: list[tuple[int, int]] = []

        if orientation == "horizontal":
            for c in range(col, col + size):
                cells.append((row, c))
        else:
            for r in range(row, row + size):
                cells.append((r, col))

        return cells

    def get_neighbor_cells(self, row: int, col: int) -> list[tuple[int, int]]:
        neighbors: list[tuple[int, int]] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr = row + dr
                nc = col + dc
                if self.in_bounds(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors

    def can_place_ship(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        size: int,
        orientation: str,
    ) -> bool:
        cells = self.get_ship_cells(row, col, size, orientation)

        for r, c in cells:
            if not self.in_bounds(r, c):
                return False

        # no overlap and no touching rule
        for r, c in cells:
            for nr, nc in self.get_neighbor_cells(r, c):
                if board[nr][nc] != 0 and (nr, nc) not in cells:
                    return False
            if board[r][c] != 0:
                return False

        return True

    def place_ship(
        self,
        board: list[list[int]],
        row: int,
        col: int,
        size: int,
        orientation: str,
    ) -> bool:
        if not self.can_place_ship(board, row, col, size, orientation):
            return False

        for r, c in self.get_ship_cells(row, col, size, orientation):
            board[r][c] = 1

        return True

    def place_next_ship(self, row: int, col: int) -> bool:
        if self.phase != "placement":
            return False

        size = self.current_ship_size()
        if size is None:
            return False

        board = self.get_active_board_for_placement()
        placed = self.place_ship(board, row, col, size, self.placement_orientation)
        if not placed:
            return False

        self.placing_ship_index += 1

        if self.placing_ship_index >= len(self.SHIP_SIZES):
            if self.vs_computer:
                self.phase = "battle"
                self.current_player = 1
            else:
                if self.placement_player == 1:
                    self.placement_player = 2
                    self.placing_ship_index = 0
                else:
                    self.phase = "battle"
                    self.current_player = 1

        return True

    def randomly_place_all_ships(self, board: list[list[int]]) -> None:
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                board[row][col] = 0

        for size in self.SHIP_SIZES:
            placed = False
            attempts = 0

            while not placed and attempts < 500:
                attempts += 1
                orientation = random.choice(["horizontal", "vertical"])
                row = random.randint(0, self.BOARD_SIZE - 1)
                col = random.randint(0, self.BOARD_SIZE - 1)
                placed = self.place_ship(board, row, col, size, orientation)

            if not placed:
                # very unlikely fallback: start over
                self.randomly_place_all_ships(board)
                return

    def attack(self, row: int, col: int) -> bool:
        if self.phase != "battle" or self.winner is not None:
            return False

        if self.current_player == 1:
            shots = self.player_shots
            target_board = self.enemy_board
        else:
            shots = self.enemy_shots
            target_board = self.player_board

        if shots[row][col] != 0:
            return False

        if target_board[row][col] == 1:
            shots[row][col] = 2
        else:
            shots[row][col] = 1

        self.check_winner()

        if self.winner is None:
            self.current_player = 2 if self.current_player == 1 else 1

        return True

    def check_winner(self) -> None:
        enemy_ship_cells = sum(cell == 1 for row in self.enemy_board for cell in row)
        enemy_hits = sum(cell == 2 for row in self.player_shots for cell in row)

        player_ship_cells = sum(cell == 1 for row in self.player_board for cell in row)
        player_hits = sum(cell == 2 for row in self.enemy_shots for cell in row)

        if enemy_ship_cells > 0 and enemy_hits >= enemy_ship_cells:
            self.winner = 1
        elif player_ship_cells > 0 and player_hits >= player_ship_cells:
            self.winner = 2

    def ai_take_turn(self) -> None:
        if not self.vs_computer or self.phase != "battle" or self.current_player != 2 or self.winner is not None:
            return

        row, col = self.choose_ai_shot()
        hit = self.player_board[row][col] == 1

        self.enemy_shots[row][col] = 2 if hit else 1

        if hit:
            self.add_adjacent_ai_targets(row, col)

        self.check_winner()

        if self.winner is None:
            self.current_player = 1

    def choose_ai_shot(self) -> tuple[int, int]:
        while self.ai_targets:
            row, col = self.ai_targets.pop(0)
            if self.enemy_shots[row][col] == 0:
                return row, col

        available = [
            (row, col)
            for row in range(self.BOARD_SIZE)
            for col in range(self.BOARD_SIZE)
            if self.enemy_shots[row][col] == 0
        ]
        return random.choice(available)

    def add_adjacent_ai_targets(self, row: int, col: int) -> None:
        candidates = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]

        for r, c in candidates:
            if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE and self.enemy_shots[r][c] == 0:
                if (r, c) not in self.ai_targets:
                    self.ai_targets.append((r, c))