from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class ProfileManagerScene(SceneBase):
    def __init__(self, app, return_scene: str = "menu") -> None:
        super().__init__(app)
        self.return_scene = return_scene

        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None

        self.selected_index = 0
        self.name_input = ""
        self.editing = False

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 34, bold=True)
        self.body_font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.meta_font = pygame.font.SysFont("arial", 18)
        active_name = self.app.save_data.get_active_profile_name()
        self.name_input = active_name[:24]
        self.selected_index = 0
        self.editing = False

    def profiles(self) -> list[dict]:
        return self.app.save_data.list_profiles()

    def current_profile(self) -> dict | None:
        profiles = self.profiles()
        if not profiles:
            return None
        self.selected_index = max(0, min(self.selected_index, len(profiles) - 1))
        return profiles[self.selected_index]

    def go_back(self) -> None:
        if self.return_scene == "library":
            from arcade_app.scenes.game_select_scene import GameSelectScene
            self.app.scene_manager.go_to(GameSelectScene(self.app))
            return

        from arcade_app.scenes.main_menu_scene import MainMenuScene
        self.app.scene_manager.go_to(MainMenuScene(self.app))

    def handle_edit_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.editing = False
            self.name_input = self.app.save_data.get_active_profile_name()[:24]
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            profile = self.current_profile()
            if profile is not None:
                self.app.save_data.rename_profile(profile["id"], self.name_input)
            self.editing = False
            return

        if event.key == pygame.K_BACKSPACE:
            self.name_input = self.name_input[:-1]
            return

        if event.unicode and event.unicode.isprintable():
            if len(self.name_input) < 24 and event.unicode not in ("\t", "\r", "\n"):
                self.name_input += event.unicode

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if self.editing:
                self.handle_edit_input(event)
                continue

            profiles = self.profiles()

            if event.key == pygame.K_ESCAPE:
                self.go_back()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = min(max(0, len(profiles) - 1), self.selected_index + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                profile = self.current_profile()
                if profile is not None:
                    self.app.save_data.set_active_profile(profile["id"])
                    self.name_input = profile["name"][:24]
            elif event.key == pygame.K_n:
                new_id = self.app.save_data.create_profile("New Player")
                self.name_input = "New Player"
                for index, profile in enumerate(self.profiles()):
                    if profile["id"] == new_id:
                        self.selected_index = index
                        break
                self.editing = True
            elif event.key == pygame.K_e:
                profile = self.current_profile()
                if profile is not None:
                    self.name_input = profile["name"][:24]
                    self.editing = True
            elif event.key == pygame.K_DELETE:
                profile = self.current_profile()
                if profile is not None and self.app.save_data.delete_profile(profile["id"]):
                    self.selected_index = max(0, self.selected_index - 1)

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.small_font is not None
        assert self.meta_font is not None

        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Local Profiles", True, theme.TEXT)
        subtitle = self.meta_font.render(
            "Enter: Activate  |  N: New  |  E: Rename  |  Delete: Remove  |  Esc: Back",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 56)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 96)))

        panel_rect = pygame.Rect((screen.get_width() - 980) // 2, 150, 980, 560)
        pygame.draw.rect(screen, theme.SURFACE, panel_rect, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel_rect, width=2, border_radius=theme.RADIUS_LARGE)

        left_rect = pygame.Rect(panel_rect.x + 26, panel_rect.y + 26, 430, panel_rect.height - 52)
        right_rect = pygame.Rect(left_rect.right + 24, panel_rect.y + 26, 474, panel_rect.height - 52)

        profiles = self.profiles()
        row_height = 92
        for index, profile in enumerate(profiles):
            row_rect = pygame.Rect(left_rect.x, left_rect.y + index * (row_height + 12), left_rect.width, row_height)
            is_selected = index == self.selected_index
            fill = theme.SURFACE_ALT if is_selected else theme.SURFACE
            border = theme.ACCENT if is_selected else theme.SURFACE_ALT

            pygame.draw.rect(screen, fill, row_rect, border_radius=theme.RADIUS_MEDIUM)
            pygame.draw.rect(screen, border, row_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

            name_surface = self.body_font.render(profile["name"], True, theme.TEXT)
            status_text = "Active profile" if profile["is_active"] else "Local profile"
            stats_text = f"Sessions: {profile['total_sessions']}  |  Unique games: {profile['unique_games']}"

            status_surface = self.meta_font.render(
                status_text,
                True,
                theme.ACCENT if profile["is_active"] else theme.MUTED_TEXT,
            )
            stats_surface = self.small_font.render(stats_text, True, theme.MUTED_TEXT)

            screen.blit(name_surface, name_surface.get_rect(topleft=(row_rect.x + 18, row_rect.y + 14)))
            screen.blit(status_surface, status_surface.get_rect(topleft=(row_rect.x + 18, row_rect.y + 46)))
            screen.blit(stats_surface, stats_surface.get_rect(topright=(row_rect.right - 18, row_rect.y + 50)))

        pygame.draw.rect(screen, theme.SURFACE_ALT, right_rect, border_radius=theme.RADIUS_MEDIUM)

        profile = self.current_profile()
        if profile is None:
            return

        heading = self.body_font.render("Selected Profile", True, theme.TEXT)
        screen.blit(heading, heading.get_rect(topleft=(right_rect.x + 20, right_rect.y + 20)))

        name_label = self.meta_font.render("Display Name", True, theme.MUTED_TEXT)
        screen.blit(name_label, name_label.get_rect(topleft=(right_rect.x + 20, right_rect.y + 70)))

        input_rect = pygame.Rect(right_rect.x + 20, right_rect.y + 100, right_rect.width - 40, 54)
        pygame.draw.rect(screen, theme.SURFACE, input_rect, border_radius=12)
        pygame.draw.rect(
            screen,
            theme.ACCENT if self.editing else theme.SURFACE,
            input_rect,
            width=2,
            border_radius=12,
        )

        display_name = self.name_input if self.editing else profile["name"]
        if self.editing and pygame.time.get_ticks() % 1000 < 500:
            display_name += "|"

        input_surface = self.body_font.render(display_name or "New Player", True, theme.TEXT)
        screen.blit(input_surface, input_surface.get_rect(midleft=(input_rect.x + 14, input_rect.centery)))

        summary_lines = [
            f"Profile ID: {profile['id']}",
            f"Sessions played: {profile['total_sessions']}",
            f"Unique games played: {profile['unique_games']}",
            f"Favorite games: {profile['favorites_count']}",
            "",
            "Workflow:",
            "• Press Enter to make this the active profile.",
            "• Press E to rename the selected profile.",
            "• Press N to create a new local profile.",
            "• Press Delete to remove the selected profile.",
        ]

        y = right_rect.y + 184
        for line in summary_lines:
            font = self.small_font if line.startswith("•") else self.meta_font
            color = theme.MUTED_TEXT if not line.startswith("Workflow") else theme.TEXT
            surface = font.render(line, True, color)
            screen.blit(surface, surface.get_rect(topleft=(right_rect.x + 20, y)))
            y += 28 if line else 16

        footer_text = (
            "Editing name: type, Backspace to erase, Enter to save, Esc to cancel"
            if self.editing
            else "Tip: each profile keeps its own recent games, favorites, and stats."
        )
        footer = self.small_font.render(footer_text, True, theme.MUTED_TEXT)
        screen.blit(footer, footer.get_rect(center=(screen.get_width() // 2, screen.get_height() - 34)))