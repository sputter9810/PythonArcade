from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class PipeConnectGame(GameBase):
    game_id = "pipe_connect"
    title = "Pipe Connect"

    DIFFICULTIES = {
        "Easy": 5,
        "Medium": 6,
        "Hard": 7,
    }

    TYPE_STRAIGHT = "straight"
    TYPE_CORNER = "corner"
    TYPE_TEE = "tee"
    TYPE_CROSS = "cross"
    TYPE_SOURCE = "source"
    TYPE_SINK = "sink"

    CONNECTIONS = {
        TYPE_STRAIGHT: {
            0: {"N", "S"},
            1: {"E", "W"},
            2: {"N", "S"},
            3: {"E", "W"},
        },
        TYPE_CORNER: {
            0: {"N", "E"},
            1: {"E", "S"},
            2: {"S", "W"},
            3: {"W", "N"},
        },
        TYPE_TEE: {
            0: {"N", "E", "W"},
            1: {"N", "E", "S"},
            2: {"E", "S", "W"},
            3: {"N", "S", "W"},
        },
        TYPE_CROSS: {
            0: {"N", "E", "S", "W"},
            1: {"N", "E", "S", "W"},
            2: {"N", "E", "S", "W"},
            3: {"N", "E", "S", "W"},
        },
        TYPE_SOURCE: {
            0: {"E"},
            1: {"S"},
            2: {"W"},
            3: {"N"},
        },
        TYPE_SINK: {
            0: {"W"},
            1: {"N"},
            2: {"E"},
            3: {"S"},
        },
    }

    OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
    DIRS = {
        "N": (-1, 0),
        "S": (1, 0),
        "E": (0, 1),
        "W": (0, -1),
    }

    def __init__(self, app):
        super().__init__(app)
        self.ui: GameUI | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1000, 620)
        self.board_rect = pygame.Rect(0, 0, 420, 420)
        self.diff_buttons: dict[str, pygame.Rect] = {}

        self.difficulty = "Medium"
        self.grid_size = 6
        self.cell_size = 64

        self.grid: list[list[dict]] = []
        self.moves = 0
        self.completed = False
        self.paused = False

    def enter(self):
        self.ui = GameUI()
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1000) // 2, 165, 1000, 620)

        top_ui_space = 118
        bottom_margin = 28
        usable_height = self.play_rect.height - top_ui_space - bottom_margin
        board_size = min(500, usable_height, self.play_rect.width - 120)

        self.cell_size = board_size // self.grid_size
        board_size = self.cell_size * self.grid_size

        self.board_rect = pygame.Rect(0, 0, board_size, board_size)
        self.board_rect.centerx = self.play_rect.centerx
        self.board_rect.y = self.play_rect.top + top_ui_space

        self.diff_buttons = {
            "Easy": pygame.Rect(self.play_rect.centerx - 190, self.play_rect.top + 24, 110, 40),
            "Medium": pygame.Rect(self.play_rect.centerx - 55, self.play_rect.top + 24, 110, 40),
            "Hard": pygame.Rect(self.play_rect.centerx + 80, self.play_rect.top + 24, 110, 40),
        }

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.grid_size = self.DIFFICULTIES[difficulty]
        self.reset_game()

    def reset_game(self):
        self.grid_size = self.DIFFICULTIES[self.difficulty]
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.moves = 0
        self.completed = False
        self.paused = False
        self.generate_puzzle()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = max(0, 2000 - self.moves * 10)
        payload["round"] = self.moves
        return payload

    def leave_to_menu(self):
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def empty_grid(self) -> list[list[dict]]:
        return [
            [{"type": None, "rotation": 0, "solution_rotation": 0} for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]

    def generate_puzzle(self) -> None:
        while True:
            if self._generate_once():
                return

    def _generate_once(self) -> bool:
        size = self.grid_size
        self.grid = self.empty_grid()

        path = [(0, 0)]
        visited = {(0, 0)}
        current = (0, 0)
        target = (size - 1, size - 1)

        while current != target:
            r, c = current
            options = []
            for dr, dc in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in visited:
                    score = abs(target[0] - nr) + abs(target[1] - nc)
                    options.append((score, (nr, nc)))

            if not options:
                return False

            options.sort(key=lambda item: item[0] + random.random() * 2.0)
            _, current = options[0]
            path.append(current)
            visited.add(current)

        path_set = set(path)

        for index, (r, c) in enumerate(path):
            entry = None
            exit_dir = None

            if index > 0:
                pr, pc = path[index - 1]
                if pr == r - 1:
                    entry = "N"
                elif pr == r + 1:
                    entry = "S"
                elif pc == c - 1:
                    entry = "W"
                elif pc == c + 1:
                    entry = "E"

            if index < len(path) - 1:
                nr, nc = path[index + 1]
                if nr == r - 1:
                    exit_dir = "N"
                elif nr == r + 1:
                    exit_dir = "S"
                elif nc == c - 1:
                    exit_dir = "W"
                elif nc == c + 1:
                    exit_dir = "E"

            dirs = set()
            if entry:
                dirs.add(entry)
            if exit_dir:
                dirs.add(exit_dir)

            if index == 0:
                pipe_type = self.TYPE_SOURCE
                rotation = self.rotation_for_dirs(pipe_type, dirs)
            elif index == len(path) - 1:
                pipe_type = self.TYPE_SINK
                rotation = self.rotation_for_dirs(pipe_type, dirs)
            elif len(dirs) == 2 and (dirs == {"N", "S"} or dirs == {"E", "W"}):
                pipe_type = self.TYPE_STRAIGHT
                rotation = self.rotation_for_dirs(pipe_type, dirs)
            else:
                pipe_type = self.TYPE_CORNER
                rotation = self.rotation_for_dirs(pipe_type, dirs)

            self.grid[r][c] = {
                "type": pipe_type,
                "rotation": rotation,
                "solution_rotation": rotation,
            }

        extra_count = max(2, size)
        extras_added = 0
        open_cells = [(r, c) for r in range(size) for c in range(size) if (r, c) not in path_set]
        random.shuffle(open_cells)

        for r, c in open_cells:
            if extras_added >= extra_count:
                break
            pipe_type = random.choice([self.TYPE_STRAIGHT, self.TYPE_CORNER, self.TYPE_TEE, self.TYPE_CROSS])
            solution_rotation = random.randint(0, 3)
            self.grid[r][c] = {
                "type": pipe_type,
                "rotation": solution_rotation,
                "solution_rotation": solution_rotation,
            }
            extras_added += 1

        for r in range(size):
            for c in range(size):
                if self.grid[r][c]["type"] is None:
                    pipe_type = random.choice([self.TYPE_STRAIGHT, self.TYPE_CORNER, self.TYPE_TEE])
                    solution_rotation = random.randint(0, 3)
                    self.grid[r][c] = {
                        "type": pipe_type,
                        "rotation": solution_rotation,
                        "solution_rotation": solution_rotation,
                    }

        changed = False
        for r in range(size):
            for c in range(size):
                spin = random.randint(0, 3)
                self.grid[r][c]["rotation"] = (self.grid[r][c]["solution_rotation"] + spin) % 4
                if spin != 0:
                    changed = True

        if not changed or self.is_connected():
            return False

        self.completed = False
        return True

    def rotation_for_dirs(self, pipe_type: str, dirs: set[str]) -> int:
        for rotation, conns in self.CONNECTIONS[pipe_type].items():
            if conns == dirs:
                return rotation
        return 0

    def connections(self, cell: dict) -> set[str]:
        return self.CONNECTIONS[cell["type"]][cell["rotation"]]

    def is_connected(self) -> bool:
        start = (0, 0)
        if self.grid[start[0]][start[1]]["type"] != self.TYPE_SOURCE:
            return False

        visited = set()
        stack = [start]

        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))

            for direction in self.connections(self.grid[r][c]):
                dr, dc = self.DIRS[direction]
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.grid_size and 0 <= nc < self.grid_size):
                    continue
                neighbor = self.grid[nr][nc]
                if self.OPPOSITE[direction] in self.connections(neighbor):
                    stack.append((nr, nc))

        return (self.grid_size - 1, self.grid_size - 1) in visited

    def cell_at(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        if not self.board_rect.collidepoint(pos):
            return None
        col = (pos[0] - self.board_rect.x) // self.cell_size
        row = (pos[1] - self.board_rect.y) // self.cell_size
        return int(row), int(col)

    def rotate_cell(self, row: int, col: int, reverse: bool = False) -> None:
        if self.completed or self.paused:
            return

        step = -1 if reverse else 1
        self.grid[row][col]["rotation"] = (self.grid[row][col]["rotation"] + step) % 4
        self.moves += 1
        self.completed = self.is_connected()

    def draw_diff_button(self, screen: pygame.Surface, label: str, rect: pygame.Rect, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

    def draw_pipe(self, screen: pygame.Surface, rect: pygame.Rect, cell: dict) -> None:
        center = rect.center
        thickness = max(8, self.cell_size // 7)
        color = theme.ACCENT if cell["type"] in (self.TYPE_SOURCE, self.TYPE_SINK) else theme.TEXT
        conns = self.connections(cell)

        hub = pygame.Rect(0, 0, thickness * 2, thickness * 2)
        hub.center = center
        pygame.draw.rect(screen, color, hub, border_radius=999)

        if "N" in conns:
            pygame.draw.line(screen, color, center, (center[0], rect.top + 8), thickness)
        if "S" in conns:
            pygame.draw.line(screen, color, center, (center[0], rect.bottom - 8), thickness)
        if "E" in conns:
            pygame.draw.line(screen, color, center, (rect.right - 8, center[1]), thickness)
        if "W" in conns:
            pygame.draw.line(screen, color, center, (rect.left + 8, center[1]), thickness)

        if cell["type"] == self.TYPE_SOURCE:
            pygame.draw.circle(screen, theme.SUCCESS, center, max(8, thickness))
        elif cell["type"] == self.TYPE_SINK:
            pygame.draw.circle(screen, theme.WARNING, center, max(8, thickness))

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

            elif e.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in self.diff_buttons.items():
                    if rect.collidepoint(e.pos):
                        self.set_difficulty(label)
                        return

                if self.completed:
                    self.reset_game()
                    continue
                if self.paused:
                    continue

                cell = self.cell_at(e.pos)
                if cell is None:
                    continue

                if e.button == 1:
                    self.rotate_cell(*cell, reverse=False)
                elif e.button == 3:
                    self.rotate_cell(*cell, reverse=True)

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render(self, screen):
        assert self.ui is not None
        assert self.mode_font is not None

        screen.fill(theme.BACKGROUND)
        self.rebuild_layout(screen)

        self.ui.draw_header(screen, "Pipe Connect", "Rotate pieces to link the source to the sink.")
        self.ui.draw_stats_row(
            screen,
            [
                f"Difficulty: {self.difficulty}",
                f"Moves: {self.moves}",
                f"Grid: {self.grid_size}x{self.grid_size}",
            ],
        )
        sub = "Every run generates a fresh pipe layout." if not self.completed else "Connection complete."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "Left Click: Rotate CW  |  Right Click: Rotate CCW  |  F5: New Puzzle  |  Esc: Back")

        for label, rect in self.diff_buttons.items():
            self.draw_diff_button(screen, label, rect, label == self.difficulty)

        pygame.draw.rect(screen, theme.SURFACE, self.board_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.board_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                rect = pygame.Rect(
                    self.board_rect.x + c * self.cell_size,
                    self.board_rect.y + r * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=4)
                self.draw_pipe(screen, rect, self.grid[r][c])

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Flow Complete",
                f"Moves: {self.moves}",
                f"Difficulty: {self.difficulty}",
            )