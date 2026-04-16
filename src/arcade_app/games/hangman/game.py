from __future__ import annotations

import random
import string

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.hangman.data import WORDS
from arcade_app.ui import theme
from arcade_app.ui.game_ui import GameUI


class HangmanGame(GameBase):
    game_id = "hangman"
    title = "Hangman"

    MAX_WRONG = 6

    def __init__(self, app) -> None:
        super().__init__(app)
        self.ui: GameUI | None = None
        self.word_font: pygame.font.Font | None = None
        self.letter_font: pygame.font.Font | None = None

        self.play_rect = pygame.Rect(0, 0, 1080, 640)
        self.keyboard_rects: dict[str, pygame.Rect] = {}
        self.pause_button = pygame.Rect(0, 0, 120, 40)

        self.category = ""
        self.secret_word = ""
        self.guessed_letters: set[str] = set()
        self.wrong_letters: list[str] = []

        self.completed = False
        self.won = False
        self.paused = False

    def enter(self) -> None:
        self.ui = GameUI()
        self.word_font = pygame.font.SysFont("arial", 34, bold=True)
        self.letter_font = pygame.font.SysFont("arial", 22, bold=True)
        self.reset_game()

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.play_rect = pygame.Rect((screen.get_width() - 1080) // 2, 165, 1080, 640)
        self.pause_button = pygame.Rect(self.play_rect.right - 150, self.play_rect.top + 18, 120, 40)

        self.keyboard_rects = {}
        letters = list(string.ascii_uppercase)
        cols = 9
        key_w = 80
        key_h = 48
        gap_x = 12
        gap_y = 12

        row_counts = [9, 9, len(letters) - 18]
        start_y = self.play_rect.bottom - 180

        index = 0
        for row, count in enumerate(row_counts):
            total_w = count * key_w + (count - 1) * gap_x
            start_x = self.play_rect.centerx - total_w // 2
            for col in range(count):
                rect = pygame.Rect(start_x + col * (key_w + gap_x), start_y + row * (key_h + gap_y), key_w, key_h)
                self.keyboard_rects[letters[index]] = rect
                index += 1

    def reset_game(self) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

        self.category = random.choice(list(WORDS.keys()))
        self.secret_word = random.choice(WORDS[self.category])
        self.guessed_letters = set()
        self.wrong_letters = []
        self.completed = False
        self.won = False
        self.paused = False

    def get_persistence_payload(self) -> dict:
        payload = super().get_persistence_payload()
        payload["hits"] = len([ch for ch in self.secret_word if ch in self.guessed_letters])
        payload["round"] = len(self.guessed_letters)
        return payload

    def leave_to_menu(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        self.app.scene_manager.go_to(GameSelectScene(self.app))

    def masked_word(self) -> str:
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.secret_word)

    def guess(self, letter: str) -> None:
        if self.completed or self.paused or letter in self.guessed_letters or letter in self.wrong_letters:
            return

        if letter in self.secret_word:
            self.guessed_letters.add(letter)
            if all(ch in self.guessed_letters for ch in self.secret_word):
                self.completed = True
                self.won = True
        else:
            self.wrong_letters.append(letter)
            if len(self.wrong_letters) >= self.MAX_WRONG:
                self.completed = True
                self.won = False

    def draw_hangman(self, screen: pygame.Surface) -> None:
        origin_x = self.play_rect.left + 120
        origin_y = self.play_rect.top + 140

        pygame.draw.line(screen, theme.TEXT, (origin_x, origin_y + 220), (origin_x + 120, origin_y + 220), 6)
        pygame.draw.line(screen, theme.TEXT, (origin_x + 30, origin_y + 220), (origin_x + 30, origin_y), 6)
        pygame.draw.line(screen, theme.TEXT, (origin_x + 30, origin_y), (origin_x + 140, origin_y), 6)
        pygame.draw.line(screen, theme.TEXT, (origin_x + 140, origin_y), (origin_x + 140, origin_y + 34), 6)

        wrong = len(self.wrong_letters)
        if wrong >= 1:
            pygame.draw.circle(screen, theme.WARNING, (origin_x + 140, origin_y + 60), 24, width=4)
        if wrong >= 2:
            pygame.draw.line(screen, theme.WARNING, (origin_x + 140, origin_y + 84), (origin_x + 140, origin_y + 150), 4)
        if wrong >= 3:
            pygame.draw.line(screen, theme.WARNING, (origin_x + 140, origin_y + 102), (origin_x + 110, origin_y + 128), 4)
        if wrong >= 4:
            pygame.draw.line(screen, theme.WARNING, (origin_x + 140, origin_y + 102), (origin_x + 170, origin_y + 128), 4)
        if wrong >= 5:
            pygame.draw.line(screen, theme.WARNING, (origin_x + 140, origin_y + 150), (origin_x + 114, origin_y + 192), 4)
        if wrong >= 6:
            pygame.draw.line(screen, theme.WARNING, (origin_x + 140, origin_y + 150), (origin_x + 166, origin_y + 192), 4)

    def draw_pause_button(self, screen: pygame.Surface) -> None:
        label = "Resume" if self.paused else "Pause"
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.pause_button, border_radius=10)
        pygame.draw.rect(screen, theme.ACCENT, self.pause_button, width=2, border_radius=10)
        surface = self.letter_font.render(label, True, theme.TEXT)
        screen.blit(surface, surface.get_rect(center=self.pause_button.center))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.leave_to_menu()
                elif event.key == pygame.K_F5:
                    self.reset_game()
                elif self.completed and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.reset_game()
                else:
                    if event.unicode and event.unicode.isalpha():
                        self.guess(event.unicode.upper())

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_button.collidepoint(event.pos) and not self.completed:
                    self.paused = not self.paused
                    continue

                if self.completed:
                    self.reset_game()
                    continue
                if self.paused:
                    continue
                for letter, rect in self.keyboard_rects.items():
                    if rect.collidepoint(event.pos):
                        self.guess(letter)
                        break

    def update(self, dt: float) -> None:
        screen = pygame.display.get_surface()
        if screen is not None:
            self.rebuild_layout(screen)

    def render(self, screen: pygame.Surface) -> None:
        assert self.ui is not None
        assert self.word_font is not None
        assert self.letter_font is not None

        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        self.ui.draw_header(
            screen,
            "Hangman",
            "Type letters or click the keyboard. Find the word before the drawing completes.",
        )
        self.ui.draw_stats_row(
            screen,
            [
                f"Category: {self.category}",
                f"Wrong: {len(self.wrong_letters)}/{self.MAX_WRONG}",
                f"Guessed: {len(self.guessed_letters) + len(self.wrong_letters)}",
            ],
        )

        if self.completed:
            sub = "Word solved." if self.won else "No guesses left."
        else:
            sub = "Start with common vowels and consonants to reveal structure quickly."
        self.ui.draw_sub_stats(screen, sub)
        self.ui.draw_footer(screen, "Mouse Pause Button  |  F5: Restart  |  Esc: Back")

        pygame.draw.rect(screen, theme.SURFACE, self.play_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.play_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        self.draw_pause_button(screen)
        self.draw_hangman(screen)

        word_surface = self.word_font.render(self.masked_word(), True, theme.TEXT)
        screen.blit(word_surface, word_surface.get_rect(center=(self.play_rect.centerx + 120, self.play_rect.top + 190)))

        wrong_text = "Wrong Letters: " + (" ".join(self.wrong_letters) if self.wrong_letters else "-")
        wrong_surface = self.letter_font.render(wrong_text, True, theme.MUTED_TEXT)
        screen.blit(wrong_surface, wrong_surface.get_rect(center=(self.play_rect.centerx + 120, self.play_rect.top + 250)))

        for letter, rect in self.keyboard_rects.items():
            used = letter in self.guessed_letters or letter in self.wrong_letters
            fill = theme.SURFACE_ALT if used else theme.SURFACE
            border = theme.ACCENT if letter in self.guessed_letters else theme.WARNING if letter in self.wrong_letters else theme.SURFACE_ALT
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, width=2, border_radius=10)
            surface = self.letter_font.render(letter, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=rect.center))

        if self.paused and not self.completed:
            self.ui.draw_pause_overlay(screen, self.play_rect, subtitle="Click the pause button to resume")

        if self.completed:
            self.ui.draw_game_over(
                screen,
                self.play_rect,
                "You Win" if self.won else "Game Over",
                f"Word: {self.secret_word}",
                f"Wrong Guesses: {len(self.wrong_letters)}",
            )