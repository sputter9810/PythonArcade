from __future__ import annotations

import math

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.registry import GAME_REGISTRY, create_game_scene, get_game_by_id
from arcade_app.ui import theme
from arcade_app.ui.card import Card


class GameSelectScene(SceneBase):
    def __init__(self, app, initial_game_id: str | None = None) -> None:
        super().__init__(app)
        self.initial_game_id = initial_game_id
        self.title_font: pygame.font.Font | None = None
        self.subtitle_font: pygame.font.Font | None = None
        self.card_title_font: pygame.font.Font | None = None
        self.card_body_font: pygame.font.Font | None = None
        self.footer_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.stats_font: pygame.font.Font | None = None
        self.recent_font: pygame.font.Font | None = None
        self.search_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

        self.cols = 3
        self.rows = 2
        self.games_per_page = self.cols * self.rows

        self.current_page = 0
        self.selected_slot = 0
        self.hovered_slot: int | None = None

        self.card_rects: list[pygame.Rect] = []
        self.recent_rects: list[tuple[str, pygame.Rect]] = []

        self.search_query = ""
        self.search_focused = False
        self.search_rect = pygame.Rect(90, 146, 470, 42)

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 22)
        self.card_title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.card_body_font = pygame.font.SysFont("arial", 19)
        self.footer_font = pygame.font.SysFont("arial", 18)
        self.meta_font = pygame.font.SysFont("arial", 22)
        self.stats_font = pygame.font.SysFont("arial", 18)
        self.recent_font = pygame.font.SysFont("arial", 16)
        self.search_font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 15)

        self.current_page = 0
        self.selected_slot = 0
        self.hovered_slot = None
        self.search_focused = False
        if self.initial_game_id:
            self.focus_game_id(self.initial_game_id)
        else:
            self.focus_last_played_page()

    def filtered_games(self) -> list[dict]:
        query = self.search_query.strip().lower()
        favorites = set(self.app.save_data.get_favorite_game_ids())

        games = GAME_REGISTRY
        if query:
            filtered: list[dict] = []
            for game in games:
                haystack = " ".join(
                    [
                        str(game.get("title", "")),
                        str(game.get("description", "")),
                        str(game.get("category", "")),
                        " ".join(game.get("modes", [])),
                    ]
                ).lower()
                if query in haystack:
                    filtered.append(game)
            games = filtered

        return sorted(
            games,
            key=lambda game: (
                0 if game["id"] in favorites else 1,
                str(game.get("title", "")).lower(),
            ),
        )

    def total_pages(self) -> int:
        return max(1, math.ceil(len(self.filtered_games()) / self.games_per_page))

    def current_page_games(self) -> list[dict]:
        games = self.filtered_games()
        start = self.current_page * self.games_per_page
        end = start + self.games_per_page
        return games[start:end]

    def selected_game(self) -> dict | None:
        games = self.current_page_games()
        if not games:
            return None
        if self.selected_slot >= len(games):
            self.selected_slot = len(games) - 1
        return games[self.selected_slot]

    def ensure_valid_selection(self) -> None:
        self.current_page = max(0, min(self.current_page, self.total_pages() - 1))
        games = self.current_page_games()
        if not games:
            self.selected_slot = 0
        else:
            self.selected_slot = max(0, min(self.selected_slot, len(games) - 1))

    def launch_selected_game(self) -> None:
        selected_game = self.selected_game()
        if selected_game is None:
            return

        self.app.save_data.set_last_played(selected_game["id"])
        scene = create_game_scene(selected_game["id"], self.app)
        self.app.scene_manager.go_to(scene)

    def launch_game_by_id(self, game_id: str) -> None:
        games = self.filtered_games()
        for index, game in enumerate(games):
            if game["id"] == game_id:
                self.current_page = index // self.games_per_page
                self.selected_slot = index % self.games_per_page
                self.launch_selected_game()
                return

    def focus_game_id(self, game_id: str) -> None:
        games = self.filtered_games()
        for index, game in enumerate(games):
            if game["id"] == game_id:
                self.current_page = index // self.games_per_page
                self.selected_slot = index % self.games_per_page
                return

    def focus_last_played_page(self) -> None:
        last_played_id = self.app.save_data.get_last_played_game_id()
        if last_played_id is None:
            return
        self.focus_game_id(last_played_id)

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
        new_page = max(0, min(self.total_pages() - 1, self.current_page + delta))
        if new_page != self.current_page:
            self.current_page = new_page
            self.hovered_slot = None
            games = self.current_page_games()
            self.selected_slot = min(self.selected_slot, max(0, len(games) - 1))

    def toggle_favorite_for_selected(self) -> None:
        selected_game = self.selected_game()
        if selected_game is None:
            return
        self.app.save_data.toggle_favorite(selected_game["id"])

    def rebuild_card_rects(self, screen: pygame.Surface) -> None:
        side_margin = 90
        grid_top = 260
        grid_bottom_margin = 180
        gap_x = 28
        gap_y = 24

        grid_width = screen.get_width() - (side_margin * 2)
        grid_height = screen.get_height() - grid_top - grid_bottom_margin

        card_width = (grid_width - gap_x * (self.cols - 1)) // self.cols
        base_card_height = (grid_height - gap_y * (self.rows - 1)) // self.rows
        card_height = base_card_height + 20

        self.card_rects = []
        for i in range(len(self.current_page_games())):
            row = i // self.cols
            col = i % self.cols
            x = side_margin + col * (card_width + gap_x)
            y = grid_top + row * (card_height + gap_y)
            self.card_rects.append(pygame.Rect(x, y, card_width, card_height))

    def rebuild_recent_rects(self) -> None:
        recent_ids = self.app.save_data.get_recent_game_ids()[:4]
        self.recent_rects = []
        if not recent_ids:
            return

        x = 90
        y = 220
        gap = 12

        for game_id in recent_ids:
            game = get_game_by_id(game_id)
            if game is None:
                continue
            width = max(150, min(250, 42 + len(game["title"]) * 9))
            rect = pygame.Rect(x, y, width, 38)
            self.recent_rects.append((game_id, rect))
            x = rect.right + gap

    def update_search_query(self, text: str) -> None:
        self.search_query = text[:32]
        self.current_page = 0
        self.selected_slot = 0
        self.hovered_slot = None
        self.ensure_valid_selection()

    def handle_search_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.search_focused = False
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.search_focused = False
            return
        if event.key == pygame.K_BACKSPACE:
            self.update_search_query(self.search_query[:-1])
            return
        if event.key == pygame.K_SPACE:
            self.update_search_query(self.search_query + " ")
            return
        if event.unicode and event.unicode.isprintable():
            if event.unicode.isalnum() or event.unicode in (" ", "-", "_", "'"):
                self.update_search_query(self.search_query + event.unicode)

    def handle_navigation_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            from arcade_app.scenes.main_menu_scene import MainMenuScene
            self.app.scene_manager.go_to(MainMenuScene(self.app))
        elif event.key == pygame.K_SLASH:
            self.search_focused = True
        elif event.key == pygame.K_TAB:
            from arcade_app.scenes.game_details_scene import GameDetailsScene
            selected = self.selected_game()
            if selected:
                self.app.scene_manager.go_to(GameDetailsScene(self.app, selected["id"]))
        elif event.key == pygame.K_h:
            from arcade_app.scenes.achievements_scene import AchievementsScene
            self.app.scene_manager.go_to(AchievementsScene(self.app, return_scene="library"))
        elif event.key == pygame.K_c:
            from arcade_app.scenes.daily_challenge_scene import DailyChallengeScene
            selected = self.selected_game()
            preferred_id = selected["id"] if selected else None
            self.app.scene_manager.go_to(DailyChallengeScene(self.app, preferred_game_id=preferred_id, return_scene="library"))
        elif event.key == pygame.K_p:
            from arcade_app.scenes.profile_manager_scene import ProfileManagerScene
            self.app.scene_manager.go_to(ProfileManagerScene(self.app, return_scene="library"))
        elif event.key == pygame.K_f:
            self.toggle_favorite_for_selected()
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

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.search_focused:
                    self.handle_search_input(event)
                else:
                    self.handle_navigation_input(event)

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
                if self.search_rect.collidepoint(mouse_pos):
                    self.search_focused = True
                    continue
                self.search_focused = False

                for game_id, rect in self.recent_rects:
                    if rect.collidepoint(mouse_pos):
                        self.launch_game_by_id(game_id)
                        return

                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_slot = i
                        self.launch_selected_game()
                        return

    def update(self, dt: float) -> None:
        self.ensure_valid_selection()
        self.rebuild_recent_rects()

    def build_card_footer(self, game_id: str) -> str:
        stats = self.app.save_data.get_game_stats(game_id)
        play_count = stats.get("play_count")
        if isinstance(play_count, int) and play_count > 0:
            return f"Played {play_count} time" if play_count == 1 else f"Played {play_count} times"
        return "Not played yet"

    def build_stats_line(self, game_id: str) -> str:
        stats = self.app.save_data.get_game_stats(game_id)
        if not stats:
            return "No saved stats yet"

        parts: list[str] = []
        for label, key in (
            ("Plays", "play_count"),
            ("Best Score", "best_score"),
            ("Best Round", "best_round"),
            ("Best Wave", "best_wave"),
            ("Best Lines", "best_lines"),
            ("Best Hits", "best_hits"),
        ):
            value = stats.get(key)
            if isinstance(value, int):
                parts.append(f"{label}: {value}")

        best_accuracy = stats.get("best_accuracy")
        if isinstance(best_accuracy, (int, float)):
            parts.append(f"Best Accuracy: {float(best_accuracy):.1f}%")

        best_reaction_ms = stats.get("best_reaction_ms")
        if isinstance(best_reaction_ms, int):
            parts.append(f"Best RT: {best_reaction_ms} ms")

        return "  |  ".join(parts) if parts else "No saved stats yet"

    def build_card_badges(self, game: dict) -> list[str]:
        badges = [str(game.get("category", "Unknown"))]
        modes = game.get("modes", [])
        badges.append("/".join(modes[:2]) if modes else "Solo")
        if self.app.save_data.is_favorite(game["id"]):
            badges.append("Favorite")
        return badges

    def build_card_hero(self, game: dict) -> str:
        words = str(game.get("title", "")).replace("-", " ").split()
        initials = "".join(word[0] for word in words[:2]).upper()
        return initials or "G"

    def render_selected_game_meta(self, screen: pygame.Surface) -> None:
        assert self.meta_font is not None
        assert self.stats_font is not None

        selected_game = self.selected_game()
        if selected_game is None:
            return

        category = selected_game.get("category", "Unknown")
        modes = " | ".join(selected_game.get("modes", []))
        status = "Ready to Play" if selected_game.get("implemented", False) else "Coming Soon"

        meta_text = f"{category}  |  {modes}  |  {status}"
        meta_surface = self.meta_font.render(meta_text, True, theme.MUTED_TEXT)
        screen.blit(meta_surface, meta_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 118)))

        stats_line = self.build_stats_line(selected_game["id"])
        stats_surface = self.stats_font.render(stats_line, True, theme.MUTED_TEXT)
        screen.blit(stats_surface, stats_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 88)))

    def render_page_indicator(self, screen: pygame.Surface) -> None:
        assert self.meta_font is not None
        total_results = len(self.filtered_games())
        page_text = f"Page {self.current_page + 1} / {self.total_pages()}"
        if self.search_query:
            page_text = f"{page_text}  |  {total_results} results"
        page_surface = self.meta_font.render(page_text, True, theme.MUTED_TEXT)
        screen.blit(page_surface, page_surface.get_rect(topright=(screen.get_width() - 90, 232)))

    def render_profile_panel(self, screen: pygame.Surface) -> None:
        assert self.meta_font is not None
        assert self.stats_font is not None
        assert self.small_font is not None

        profile = self.app.save_data.get_profile_summary()
        panel_rect = pygame.Rect(screen.get_width() - 370, 120, 280, 110)

        pygame.draw.rect(screen, theme.SURFACE, panel_rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

        title = self.meta_font.render(profile["name"], True, theme.TEXT)
        sessions = self.stats_font.render(f"Sessions played: {profile['total_sessions']}", True, theme.MUTED_TEXT)
        unique = self.stats_font.render(f"Unique games: {profile['unique_games']}", True, theme.MUTED_TEXT)
        achievements = self.small_font.render(f"Achievements: {profile['achievement_count']}", True, theme.WARNING)
        hint = self.small_font.render("P: Profiles  |  H: Achievements", True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(topleft=(panel_rect.x + 16, panel_rect.y + 12)))
        screen.blit(sessions, sessions.get_rect(topleft=(panel_rect.x + 16, panel_rect.y + 42)))
        screen.blit(unique, unique.get_rect(topleft=(panel_rect.x + 16, panel_rect.y + 62)))
        screen.blit(achievements, achievements.get_rect(topleft=(panel_rect.x + 16, panel_rect.y + 84)))
        screen.blit(hint, hint.get_rect(bottomright=(panel_rect.right - 14, panel_rect.bottom - 10)))

    def render_recent_games(self, screen: pygame.Surface) -> None:
        assert self.recent_font is not None
        assert self.stats_font is not None

        label = self.stats_font.render("Recently Played", True, theme.MUTED_TEXT)
        screen.blit(label, label.get_rect(topleft=(90, 226)))

        if not self.recent_rects:
            empty = self.recent_font.render("No recent games yet", True, theme.MUTED_TEXT)
            screen.blit(empty, empty.get_rect(topleft=(240, 229)))
            return

        for game_id, rect in self.recent_rects:
            game = get_game_by_id(game_id)
            if game is None:
                continue
            pygame.draw.rect(screen, theme.SURFACE, rect, border_radius=999)
            pygame.draw.rect(screen, theme.SURFACE_ALT, rect, width=1, border_radius=999)
            text_surface = self.recent_font.render(game["title"], True, theme.TEXT)
            screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def render_search_bar(self, screen: pygame.Surface) -> None:
        assert self.search_font is not None

        self.search_rect = pygame.Rect(90, 146, 470, 42)

        border = theme.ACCENT if self.search_focused else theme.SURFACE_ALT
        border_width = 3 if self.search_focused else 2
        pygame.draw.rect(screen, theme.SURFACE, self.search_rect, border_radius=999)
        pygame.draw.rect(screen, border, self.search_rect, width=border_width, border_radius=999)

        prefix = "Search: "
        if self.search_query:
            text = self.search_query
            color = theme.TEXT
        else:
            text = "Click or press / to search"
            color = theme.MUTED_TEXT

        display_text = prefix + text
        if self.search_focused and pygame.time.get_ticks() % 1000 < 500:
            display_text += "|"

        text_surface = self.search_font.render(display_text, True, color)
        text_rect = text_surface.get_rect(midleft=(self.search_rect.left + 18, self.search_rect.centery))
        screen.blit(text_surface, text_rect)

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.subtitle_font is not None
        assert self.card_title_font is not None
        assert self.footer_font is not None
        assert self.stats_font is not None
        assert self.search_font is not None
        assert self.meta_font is not None

        self.rebuild_card_rects(screen)
        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Arcade Library", True, theme.TEXT)
        subtitle = self.subtitle_font.render(
            "Arrows/WASD: Move  |  Enter: Play  |  F: Favorite  |  P: Profiles  |  H: Achievements  |  Q/E: Page  |  /: Search  |  Tab: Details",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(title, title.get_rect(topleft=(90, 40)))
        screen.blit(subtitle, subtitle.get_rect(topleft=(90, 92)))

        self.render_search_bar(screen)
        self.render_profile_panel(screen)
        self.render_page_indicator(screen)
        self.render_recent_games(screen)

        games = self.current_page_games()
        for i, game in enumerate(games):
            rect = self.card_rects[i]
            card = Card(
                rect=rect,
                title=game["title"],
                description=game["description"],
                footer_text=self.build_card_footer(game["id"]),
                hero_text=self.build_card_hero(game),
                badges=self.build_card_badges(game),
            )
            card.draw(
                screen,
                self.card_title_font,
                self.footer_font,
                is_selected=(i == self.selected_slot),
                is_hovered=(i == self.hovered_slot),
            )

        if not games:
            empty_surface = self.meta_font.render("No games match that search.", True, theme.MUTED_TEXT)
            screen.blit(empty_surface, empty_surface.get_rect(center=(screen.get_width() // 2, 420)))

        selected = self.selected_game()
        if selected is not None:
            favorite_text = "Favorite game" if self.app.save_data.is_favorite(selected["id"]) else "Press F to favorite"
            favorite_surface = self.stats_font.render(favorite_text, True, theme.MUTED_TEXT)
            screen.blit(favorite_surface, favorite_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 148)))

        self.render_selected_game_meta(screen)

        footer_text = self.footer_font.render(
            "Esc: Back  |  Recent chips are clickable  |  Favorite games sort to the top",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(footer_text, footer_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)))
