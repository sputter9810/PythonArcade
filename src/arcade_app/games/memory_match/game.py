from __future__ import annotations

import random
import string

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class MemoryMatchGame(GameBase):
    game_id = "memory_match"
    title = "Memory Match"

    DIFFICULTIES = {
        "Easy": (4, 4),
        "Medium": (4, 5),
        "Hard": (6, 6),
    }

    PAIR_COLORS = [
        (80, 170, 100),
        (190, 80, 80),
        (80, 120, 200),
        (200, 180, 70),
        (180, 110, 220),
        (80, 180, 180),
        (230, 130, 80),
        (130, 200, 120),
        (220, 110, 150),
        (110, 150, 230),
        (210, 210, 110),
        (160, 120, 230),
        (120, 200, 200),
        (230, 90, 90),
        (100, 180, 120),
        (240, 160, 80),
        (140, 180, 255),
        (255, 210, 120),
    ]

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.card_font: pygame.font.Font | None = None
        self.mode_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1000, 620)
        self.cards: list[dict] = []
        self.difficulty = "Easy"
        self.diff_buttons: dict[str, pygame.Rect] = {}
        self.symbol_colors: dict[str, tuple[int, int, int]] = {}

        self.first_index: int | None = None
        self.second_index: int | None = None
        self.hide_timer = 0.0

        self.matches = 0
        self.total_pairs = 0
        self.moves = 0
        self.completed = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.card_font = pygame.font.SysFont("arial", 34, bold=True)
        self.mode_font = pygame.font.SysFont("arial", 18, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1000) // 2, 165, 1000, 620)

        self.diff_buttons = {
            "Easy": pygame.Rect(self.play_rect.centerx - 210, self.play_rect.top + 24, 120, 40),
            "Medium": pygame.Rect(self.play_rect.centerx - 60, self.play_rect.top + 24, 120, 40),
            "Hard": pygame.Rect(self.play_rect.centerx + 90, self.play_rect.top + 24, 120, 40),
        }

    def build_cards(self) -> None:
        cols, rows = self.DIFFICULTIES[self.difficulty]
        pair_count = (cols * rows) // 2
        letters = list(string.ascii_uppercase[:pair_count])
        deck = letters * 2
        random.shuffle(deck)

        self.symbol_colors = {
            symbol: self.PAIR_COLORS[i % len(self.PAIR_COLORS)]
            for i, symbol in enumerate(letters)
        }

        max_width = self.play_rect.width - 80
        max_height = self.play_rect.height - 160
        gap = 18

        card_w = min(140, (max_width - gap * (cols - 1)) // cols)
        card_h = min(100, (max_height - gap * (rows - 1)) // rows)

        total_w = cols * card_w + (cols - 1) * gap
        total_h = rows * card_h + (rows - 1) * gap
        start_x = self.play_rect.centerx - total_w // 2
        start_y = self.play_rect.top + 90 + max(0, (max_height - total_h) // 2)

        self.cards = []
        index = 0
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    start_x + c * (card_w + gap),
                    start_y + r * (card_h + gap),
                    card_w,
                    card_h,
                )
                self.cards.append(
                    {
                        "rect": rect,
                        "symbol": deck[index],
                        "revealed": False,
                        "matched": False,
                    }
                )
                index += 1

        self.total_pairs = pair_count

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.first_index = None
        self.second_index = None
        self.hide_timer = 0.0
        self.matches = 0
        self.moves = 0
        self.completed = False
        self.paused = False

        self.build_cards()

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.reset_game()

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["score"] = max(0, 1500 - self.moves * 20)
        payload["round"] = self.moves
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def reveal_card(self, index: int) -> None:
        if self.paused or self.completed or self.hide_timer > 0:
            return

        card = self.cards[index]
        if card["revealed"] or card["matched"]:
            return

        card["revealed"] = True

        if self.first_index is None:
            self.first_index = index
            return

        if self.second_index is None:
            self.second_index = index
            self.moves += 1

            first = self.cards[self.first_index]
            second = self.cards[self.second_index]
            if first["symbol"] == second["symbol"]:
                first["matched"] = True
                second["matched"] = True
                self.matches += 1
                self.first_index = None
                self.second_index = None
                if self.matches == self.total_pairs:
                    self.completed = True
            else:
                self.hide_timer = 0.8

    def draw_diff_button(self, screen: pygame.Surface, label: str, rect: pygame.Rect, selected: bool) -> None:
        assert self.mode_font is not None
        fill = theme.SURFACE_ALT if selected else theme.SURFACE
        border = theme.ACCENT if selected else theme.SURFACE_ALT
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
        surface = self.mode_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=rect.center))

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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in self.diff_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.set_difficulty(label)
                        return

                if self.completed:
                    self.reset_game()
                    continue
                if self.paused:
                    continue
                for i, card in enumerate(self.cards):
                    if card["rect"].collidepoint(event.pos):
                        self.reveal_card(i)
                        break

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        if self.hide_timer > 0 and not self.paused:
            self.hide_timer -= dt
            if self.hide_timer <= 0 and self.first_index is not None and self.second_index is not None:
                self.cards[self.first_index]["revealed"] = False
                self.cards[self.second_index]["revealed"] = False
                self.first_index = None
                self.second_index = None

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.card_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Memory Match",
            "Click cards to reveal matching letters. Choose a difficulty above the board.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Difficulty: {self.difficulty}",
                f"Pairs: {self.matches}/{self.total_pairs}",
                f"Moves: {self.moves}",
            ],
        )
        sub = "Track revealed positions and reduce wasted flips." if not self.completed else "All pairs matched."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "P: Pause  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        for label, rect in self.diff_buttons.items():
            self.draw_diff_button(screen, label, rect, label == self.difficulty)

        for card in self.cards:
            pair_color = self.symbol_colors.get(card["symbol"], theme.ACCENT)

            if card["matched"]:
                fill = pair_color
                text_color = theme.BACKGROUND
            elif card["revealed"]:
                fill = pair_color
                text_color = theme.BACKGROUND
            else:
                fill = theme.SURFACE
                text_color = theme.TEXT

            pygame.draw.rect(screen, fill, card["rect"], border_radius=14)
            pygame.draw.rect(screen, theme.TEXT, card["rect"], width=2, border_radius=14)

            if card["revealed"] or card["matched"]:
                surface = self.card_font.render(card["symbol"], True, text_color)
                screen.blit(surface, surface.get_rect(center=card["rect"].center))

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect)

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "Board Cleared",
                f"Pairs Matched: {self.matches}",
                f"Difficulty: {self.difficulty}  |  Total Moves: {self.moves}",
            )