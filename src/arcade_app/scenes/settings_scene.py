from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class SettingsScene(SceneBase):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None

        self.options = ["fullscreen", "sound_enabled", "music_enabled"]
        self.selected_index = 0

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.meta_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)

    def get_option_label(self, option: str) -> str:
        labels = {
            "fullscreen": "Fullscreen",
            "sound_enabled": "Sound Effects",
            "music_enabled": "Music",
        }
        return labels.get(option, option)

    def get_option_value(self, option: str) -> bool:
        return bool(getattr(self.app.config, option))

    def toggle_selected_option(self) -> None:
        option = self.options[self.selected_index]
        current_value = self.get_option_value(option)
        self.app.update_setting(option, not current_value)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                from arcade_app.scenes.main_menu_scene import MainMenuScene
                self.app.scene_manager.go_to(MainMenuScene(self.app))
            elif event.key == pygame.K_p:
                from arcade_app.scenes.profile_manager_scene import ProfileManagerScene
                self.app.scene_manager.go_to(ProfileManagerScene(self.app, return_scene="menu"))
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.toggle_selected_option()

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None

        screen.fill(theme.BACKGROUND)

        title = self.title_font.render("Settings", True, theme.TEXT)
        subtitle = self.body_font.render(
            "Use Up/Down to select and Enter/Space to toggle.",
            True,
            theme.MUTED_TEXT,
        )
        footer = self.meta_font.render("Esc: Back to Main Menu  |  P: Profiles", True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 70)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 120)))
        screen.blit(footer, footer.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)))

        panel_width = 700
        panel_height = 280
        panel_rect = pygame.Rect((screen.get_width() - panel_width) // 2, 190, panel_width, panel_height)
        pygame.draw.rect(screen, theme.SURFACE, panel_rect, border_radius=theme.RADIUS_LARGE)

        row_height = 70
        start_y = panel_rect.y + 40

        for i, option in enumerate(self.options):
            row_rect = pygame.Rect(panel_rect.x + 30, start_y + i * row_height, panel_rect.width - 60, 52)

            is_selected = i == self.selected_index
            fill = theme.SURFACE_ALT if is_selected else theme.SURFACE
            border = theme.ACCENT if is_selected else theme.SURFACE_ALT

            pygame.draw.rect(screen, fill, row_rect, border_radius=theme.RADIUS_MEDIUM)
            pygame.draw.rect(screen, border, row_rect, width=3, border_radius=theme.RADIUS_MEDIUM)

            label = self.body_font.render(self.get_option_label(option), True, theme.TEXT)
            value_text = "On" if self.get_option_value(option) else "Off"
            value_color = theme.SUCCESS if self.get_option_value(option) else theme.DANGER
            value = self.body_font.render(value_text, True, value_color)

            screen.blit(label, label.get_rect(midleft=(row_rect.x + 20, row_rect.centery)))
            screen.blit(value, value.get_rect(midright=(row_rect.right - 20, row_rect.centery)))

        profile = self.app.save_data.get_profile_summary()
        profile_surface = self.meta_font.render(f"Active Profile: {profile['name']}", True, theme.ACCENT)
        screen.blit(profile_surface, profile_surface.get_rect(center=(screen.get_width() // 2, 500)))