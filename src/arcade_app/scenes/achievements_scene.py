from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class AchievementsScene(SceneBase):
    def __init__(self, app, return_scene: str = "menu") -> None:
        super().__init__(app)
        self.return_scene = return_scene
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.scroll_offset = 0
        self.max_scroll = 0

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 42, bold=True)
        self.body_font = pygame.font.SysFont("arial", 24)
        self.meta_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 15)
        self.scroll_offset = 0
        self.max_scroll = 0

    def go_back(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        from arcade_app.scenes.main_menu_scene import MainMenuScene

        if self.return_scene == "library":
            self.app.scene_manager.go_to(GameSelectScene(self.app))
        else:
            self.app.scene_manager.go_to(MainMenuScene(self.app))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self.go_back()
                elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_PAGEDOWN):
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 50)
                elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_PAGEUP):
                    self.scroll_offset = max(0, self.scroll_offset - 50)
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 40))

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None
        assert self.small_font is not None

        screen.fill(theme.BACKGROUND)
        profile = self.app.save_data.get_profile_summary()
        achievement_rows = self.app.save_data.get_achievement_rows()
        recent_unlocks = self.app.save_data.get_recent_achievement_unlocks()

        title = self.title_font.render("Achievements", True, theme.TEXT)
        subtitle = self.meta_font.render(
            f"{profile['name']}  |  Unlocked {profile['achievement_count']} / {len(achievement_rows)} achievements",
            True,
            theme.MUTED_TEXT,
        )
        footer = self.small_font.render(
            "Esc: Back  |  Mouse Wheel / Up / Down to scroll",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title, title.get_rect(topleft=(90, 42)))
        screen.blit(subtitle, subtitle.get_rect(topleft=(92, 94)))
        screen.blit(footer, footer.get_rect(bottomleft=(92, screen.get_height() - 24)))

        recent_panel = pygame.Rect(screen.get_width() - 430, 42, 340, 150)
        pygame.draw.rect(screen, theme.SURFACE, recent_panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, recent_panel, width=2, border_radius=theme.RADIUS_LARGE)
        heading = self.meta_font.render("Recent Unlocks", True, theme.TEXT)
        screen.blit(heading, heading.get_rect(topleft=(recent_panel.x + 18, recent_panel.y + 16)))

        recent_y = recent_panel.y + 52
        if recent_unlocks:
            for row in recent_unlocks[:4]:
                line = self.small_font.render(f"• {row['name']}", True, theme.ACCENT)
                screen.blit(line, line.get_rect(topleft=(recent_panel.x + 18, recent_y)))
                recent_y += 26
        else:
            empty = self.small_font.render("No achievements unlocked yet.", True, theme.MUTED_TEXT)
            screen.blit(empty, empty.get_rect(topleft=(recent_panel.x + 18, recent_y)))

        list_rect = pygame.Rect(90, 150, screen.get_width() - 540, screen.get_height() - 240)
        pygame.draw.rect(screen, theme.SURFACE, list_rect, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, list_rect, width=2, border_radius=theme.RADIUS_LARGE)

        visible_top = list_rect.y + 20
        content_y = visible_top - self.scroll_offset
        row_height = 96

        for row in achievement_rows:
            item_rect = pygame.Rect(list_rect.x + 20, content_y, list_rect.width - 40, row_height)
            if item_rect.bottom >= list_rect.y + 8 and item_rect.top <= list_rect.bottom - 8:
                fill = theme.SURFACE_ALT if row["unlocked"] else theme.SURFACE
                border = theme.SUCCESS if row["unlocked"] else theme.SURFACE_ALT
                pygame.draw.rect(screen, fill, item_rect, border_radius=theme.RADIUS_MEDIUM)
                pygame.draw.rect(screen, border, item_rect, width=2, border_radius=theme.RADIUS_MEDIUM)

                name = self.body_font.render(row["name"], True, theme.TEXT)
                desc = self.meta_font.render(row["description"], True, theme.MUTED_TEXT)
                category = self.small_font.render(row["category"], True, theme.ACCENT)
                progress_color = theme.SUCCESS if row["unlocked"] else theme.WARNING
                progress = self.small_font.render(row["progress_text"], True, progress_color)
                status_text = "Unlocked" if row["unlocked"] else "In Progress"
                status = self.small_font.render(status_text, True, progress_color)

                screen.blit(name, name.get_rect(topleft=(item_rect.x + 18, item_rect.y + 14)))
                screen.blit(desc, desc.get_rect(topleft=(item_rect.x + 18, item_rect.y + 44)))
                screen.blit(category, category.get_rect(bottomleft=(item_rect.x + 18, item_rect.bottom - 12)))
                screen.blit(status, status.get_rect(topright=(item_rect.right - 18, item_rect.y + 16)))
                screen.blit(progress, progress.get_rect(bottomright=(item_rect.right - 18, item_rect.bottom - 12)))

            content_y += row_height + 12

        total_height = len(achievement_rows) * (row_height + 12)
        self.max_scroll = max(0, total_height - (list_rect.height - 20))
