from __future__ import annotations

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.games.hangman.data import WORD_BANK
from arcade_app.games.hangman.logic import HangmanLogic
from arcade_app.ui import theme


class HangmanGame(GameBase):
    game_id = "hangman"
    title = "Hangman"

    def __init__(self, app) -> None:
        super().__init__(app)
        self.logic = HangmanLogic()

        self.title_font: pygame.font.Font | None = None
        self.info_font: pygame.font.Font | None = None
        self.word_font: pygame.font.Font | None = None
        self.letter_font: pygame.font.Font | None = None

        self.categories = list(WORD_BANK.keys())
        self.selected_category_index = 0
        self.phase = "category_select"  # category_select or game

        self.input_rect = pygame.Rect(0, 0, 620, 60)

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.word_font = pygame.font.SysFont("consolas", 44, bold=True)
        self.letter_font = pygame.font.SysFont("arial", 24)

    def reset_game(self) -> None:
        category = self.categories[self.selected_category_index]
        self.logic.reset(category)
        self.phase = "game"

    def rebuild_layout(self, screen: pygame.Surface) -> None:
        self.input_rect = pygame.Rect(
            (screen.get_width() - 620) // 2,
            470,
            620,
            60,
        )

    def draw_hangman(self, screen: pygame.Surface) -> None:
        base_x = screen.get_width() // 2 - 280
        base_y = 360

        line_color = theme.TEXT
        width = 5

        pygame.draw.line(screen, line_color, (base_x, base_y), (base_x + 160, base_y), width)
        pygame.draw.line(screen, line_color, (base_x + 40, base_y), (base_x + 40, base_y - 220), width)
        pygame.draw.line(screen, line_color, (base_x + 40, base_y - 220), (base_x + 150, base_y - 220), width)
        pygame.draw.line(screen, line_color, (base_x + 150, base_y - 220), (base_x + 150, base_y - 180), width)

        wrong = self.logic.wrong_guesses

        if wrong >= 1:
            pygame.draw.circle(screen, line_color, (base_x + 150, base_y - 155), 25, width)
        if wrong >= 2:
            pygame.draw.line(screen, line_color, (base_x + 150, base_y - 130), (base_x + 150, base_y - 60), width)
        if wrong >= 3:
            pygame.draw.line(screen, line_color, (base_x + 150, base_y - 110), (base_x + 120, base_y - 85), width)
        if wrong >= 4:
            pygame.draw.line(screen, line_color, (base_x + 150, base_y - 110), (base_x + 180, base_y - 85), width)
        if wrong >= 5:
            pygame.draw.line(screen, line_color, (base_x + 150, base_y - 60), (base_x + 125, base_y - 25), width)
        if wrong >= 6:
            pygame.draw.line(screen, line_color, (base_x + 150, base_y - 60), (base_x + 175, base_y - 25), width)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))
                return

            if self.phase == "category_select":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_category_index = max(0, self.selected_category_index - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_category_index = min(len(self.categories) - 1, self.selected_category_index + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_game()
                return

            if event.key == pygame.K_F5:
                self.reset_game()
            elif event.key == pygame.K_TAB:
                self.phase = "category_select"
            else:
                if event.unicode and event.unicode.isalpha():
                    self.logic.guess_letter(event.unicode)

    def update(self, dt: float) -> None:
        return

    def render_category_select(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.letter_font is not None

        title = self.title_font.render("Hangman", True, theme.TEXT)
        subtitle = self.info_font.render("Choose a category", True, theme.TEXT)
        controls = self.info_font.render(
            "Up/Down: Select  |  Enter: Start  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 140)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)))

        panel = pygame.Rect((screen.get_width() - 520) // 2, 210, 520, 320)
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)

        row_h = 52
        for i, category in enumerate(self.categories):
            row = pygame.Rect(panel.x + 24, panel.y + 24 + i * row_h, panel.width - 48, 40)
            selected = i == self.selected_category_index
            fill = theme.SURFACE_ALT if selected else theme.SURFACE
            border = theme.ACCENT if selected else theme.SURFACE_ALT

            pygame.draw.rect(screen, fill, row, border_radius=theme.RADIUS_MEDIUM)
            pygame.draw.rect(screen, border, row, width=2, border_radius=theme.RADIUS_MEDIUM)

            label = self.letter_font.render(category, True, theme.TEXT)
            screen.blit(label, label.get_rect(center=row.center))

    def render_game(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.info_font is not None
        assert self.word_font is not None
        assert self.letter_font is not None

        title = self.title_font.render("Hangman", True, theme.TEXT)
        status = self.info_font.render(self.logic.get_status_text(), True, theme.TEXT)
        category = self.info_font.render(f"Category: {self.logic.category}", True, theme.MUTED_TEXT)
        controls = self.info_font.render(
            "Type a letter  |  F5: Restart  |  Tab: Categories  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )

        display_word = self.word_font.render(self.logic.get_display_word(), True, theme.TEXT)
        wrong_letters_text = ", ".join(self.logic.wrong_letters) if self.logic.wrong_letters else "None"
        wrong_letters = self.letter_font.render(
            f"Wrong letters: {wrong_letters_text}",
            True,
            theme.MUTED_TEXT,
        )
        attempts = self.letter_font.render(
            f"Wrong guesses: {self.logic.wrong_guesses}/{self.logic.MAX_WRONG_GUESSES}",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 35)))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, 80)))
        screen.blit(category, category.get_rect(center=(screen.get_width() // 2, 115)))

        self.draw_hangman(screen)

        pygame.draw.rect(screen, theme.SURFACE, self.input_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.input_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        screen.blit(display_word, display_word.get_rect(center=(screen.get_width() // 2 + 120, 300)))
        screen.blit(wrong_letters, wrong_letters.get_rect(center=(screen.get_width() // 2 + 120, 390)))
        screen.blit(attempts, attempts.get_rect(center=(screen.get_width() // 2 + 120, 425)))
        screen.blit(controls, controls.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30)))

        input_label = self.letter_font.render("Type any letter on your keyboard to guess.", True, theme.TEXT)
        screen.blit(input_label, input_label.get_rect(center=self.input_rect.center))

    def render(self, screen: pygame.Surface) -> None:
        self.rebuild_layout(screen)
        screen.fill(theme.BACKGROUND)

        if self.phase == "category_select":
            self.render_category_select(screen)
        else:
            self.render_game(screen)