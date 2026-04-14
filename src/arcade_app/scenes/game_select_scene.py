from __future__ import annotations

import math
import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.registry import GAME_REGISTRY, create_game_scene, get_game_by_id
from arcade_app.ui import theme
from arcade_app.ui.card import Card


class GameSelectScene(SceneBase):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.footer_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.stats_font: pygame.font.Font | None = None

        self.cols = 4
        self.rows = 4
        self.games_per_page = self.cols * self.rows

        self.current_page = 0
        self.selected_slot = 0
        self.hovered_slot: int | None = None

        self.card_rects: list[pygame.Rect] = []

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.footer_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.meta_font = pygame.font.SysFont("arial", 18)
        self.stats_font = pygame.font.SysFont("arial", 16)

        self.current_page = 0
        self.selected_slot = 0
        self.hovered_slot = None

    def total_pages(self) -> int:
        return max(1, math.ceil(len(GAME_REGISTRY) / self.games_per_page))

    def current_page_games(self) -> list[dict]:
        start = self.current_page * self.games_per_page
        end = start + self.games_per_page
        return GAME_REGISTRY[start:end]

    def selected_game(self) -> dict | None:
        games = self.current_page_games()
        if not games:
            return None
        if self.selected_slot >= len(games):
            self.selected_slot = len(games) - 1
        return games[self.selected_slot]

    def selected_game_id(self) -> str | None:
        game = self.selected_game()
        return game["id"] if game is not None else None

    def launch_selected_game(self) -> None:
        selected_game = self.selected_game()
        if selected_game is None:
            return

        self.app.save_data.set_last_played(selected_game["id"])
        scene = create_game_scene(selected_game["id"], self.app)
        self.app.scene_manager.go_to(scene)

    def move_selection(self, dx: int, dy: int) -> None:
        games = self.current_page_games()
        if not games:
            return

        current_row = self.selected_slot // self.cols
        current_col = self.selected_slot % self.cols

        new_row = max(0, min(self.rows - 1, current_row + dy))
        new_col = max(0, min(self.cols - 1, current_col + dx))

        new_slot = new_row * self.cols + new_col
        if new_slot < len(games):
            self.selected_slot = new_slot

    def change_page(self, delta: int) -> None:
        new_page = self.current_page + delta
        new_page = max(0, min(self.total_pages() - 1, new_page))

        if new_page != self.current_page:
            self.current_page = new_page
            self.hovered_slot = None

            games = self.current_page_games()
            if games:
                self.selected_slot = min(self.selected_slot, len(games) - 1)
            else:
                self.selected_slot = 0

    def rebuild_card_rects(self, screen: pygame.Surface) -> None:
        outer_margin_x = 60
        outer_margin_y = 110
        gap = 20

        grid_width = screen.get_width() - (outer_margin_x * 2)
        grid_height = screen.get_height() - outer_margin_y - 120
        card_width = (grid_width - gap * (self.cols - 1)) // self.cols
        card_height = (grid_height - gap * (self.rows - 1)) // self.rows

        games = self.current_page_games()
        self.card_rects = []

        for i in range(len(games)):
            row = i // self.cols
            col = i % self.cols
            x = outer_margin_x + col * (card_width + gap)
            y = outer_margin_y + row * (card_height + gap)
            self.card_rects.append(pygame.Rect(x, y, card_width, card_height))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from arcade_app.scenes.main_menu_scene import MainMenuScene
                    self.app.scene_manager.go_to(MainMenuScene(self.app))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.move_selection(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.move_selection(1, 0)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.move_selection(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.move_selection(0, 1)
                elif event.key in (pygame.K_q, pygame.K_PAGEUP):
                    self.change_page(-1)
                elif event.key in (pygame.K_e, pygame.K_PAGEDOWN):
                    self.change_page(1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.launch_selected_game()

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                self.hovered_slot = None
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mouse_pos):
                        self.hovered_slot = i
                        self.selected_slot = i
                        break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_slot = i
                        self.launch_selected_game()
                        break

    def update(self, dt: float) -> None:
        return

    def build_card_footer(self, game_id: str) -> str | None:
        stats = self.app.save_data.get_game_stats(game_id)
        play_count = stats.get("play_count")

        if isinstance(play_count, int) and play_count > 0:
            if play_count == 1:
                return "Played 1 time"
            return f"Played {play_count} times"

        return "Not played yet"

    def build_stats_line(self, game_id: str) -> str:
        stats = self.app.save_data.get_game_stats(game_id)
        if not stats:
            return "No saved stats yet"

        parts: list[str] = []

        play_count = stats.get("play_count")
        if isinstance(play_count, int):
            parts.append(f"Plays: {play_count}")

        best_score = stats.get("best_score")
        if isinstance(best_score, int):
            parts.append(f"Best Score: {best_score}")

        best_round = stats.get("best_round")
        if isinstance(best_round, int):
            parts.append(f"Best Round: {best_round}")

        best_wave = stats.get("best_wave")
        if isinstance(best_wave, int):
            parts.append(f"Best Wave: {best_wave}")

        best_lines = stats.get("best_lines")
        if isinstance(best_lines, int):
            parts.append(f"Best Lines: {best_lines}")

        if not parts:
            return "No saved stats yet"

        return "  |  ".join(parts)

    def render_selected_game_meta(self, screen: pygame.Surface) -> None:
        assert self.meta_font is not None
        assert self.stats_font is not None

        selected_game = self.selected_game()
        if selected_game is None:
            return

        category = selected_game.get("category", "Unknown")
        modes = ", ".join(selected_game.get("modes", []))
        status = "Ready to Play" if selected_game.get("implemented", False) else "Coming Soon"

        meta_text = f"{category}  |  {modes}  |  {status}"
        meta_surface = self.meta_font.render(meta_text, True, theme.MUTED_TEXT)
        screen.blit(
            meta_surface,
            meta_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 74)),
        )

        stats_line = self.build_stats_line(selected_game["id"])
        stats_surface = self.stats_font.render(stats_line, True, theme.MUTED_TEXT)
        screen.blit(
            stats_surface,
            stats_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 54)),
        )

    def render_page_indicator(self, screen: pygame.Surface) -> None:
        assert self.meta_font is not None

        page_text = f"Page {self.current_page + 1} / {self.total_pages()}"
        page_surface = self.meta_font.render(page_text, True, theme.MUTED_TEXT)
        screen.blit(
            page_surface,
            page_surface.get_rect(center=(screen.get_width() // 2, 96)),
        )

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.footer_font is not None
        assert self.meta_font is not None
        assert self.stats_font is not None

        self.rebuild_card_rects(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Choose a Game", True, theme.TEXT)
        subtitle = self.body_font.render(
            "Use Arrow Keys / WASD to move, Q/E to change page, Enter to open, Esc to go back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 40)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 75)))
        self.render_page_indicator(screen)

        games = self.current_page_games()
        for i, game in enumerate(games):
            rect = self.card_rects[i]
            footer_text = self.build_card_footer(game["id"])

            card = Card(
                rect=rect,
                title=game["title"],
                description=game["description"],
                footer_text=footer_text,
            )
            card.draw(
                screen,
                self.title_font,
                self.body_font,
                is_selected=(i == self.selected_slot),
                is_hovered=(i == self.hovered_slot),
            )

        self.render_selected_game_meta(screen)

        last_played_id = self.app.save_data.get_last_played_game_id()
        if last_played_id is not None:
            last_played_game = get_game_by_id(last_played_id)
            last_played_label = last_played_game["title"] if last_played_game is not None else last_played_id

            last_played_surface = self.stats_font.render(
                f"Last Played: {last_played_label}",
                True,
                theme.MUTED_TEXT,
            )
            screen.blit(
                last_played_surface,
                last_played_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 96)),
            )

        footer_text = self.footer_font.render(
            "Mouse: Hover/Click  |  Keyboard: Arrow Keys/WASD  |  Q/E: Page  |  Enter: Open  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )
        footer_rect = footer_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(footer_text, footer_rect)