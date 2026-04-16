from __future__ import annotations

import pygame

from arcade_app.ui import theme


class GameUI:
    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.HEADING_SIZE, bold=True)
        self.info_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.small_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.big_font = pygame.font.SysFont("arial", 52, bold=True)

    def draw_header(self, screen: pygame.Surface, title: str, subtitle: str) -> None:
        title_surf = self.title_font.render(title, True, theme.TEXT)
        subtitle_surf = self.small_font.render(subtitle, True, theme.MUTED_TEXT)

        screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width() // 2, 40)))
        screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(screen.get_width() // 2, 72)))

    def draw_stats_row(self, screen: pygame.Surface, stats: list[str]) -> None:
        if not stats:
            return

        gap = 180
        total_width = gap * (len(stats) - 1)
        start_x = screen.get_width() // 2 - total_width // 2

        for i, stat in enumerate(stats):
            surf = self.info_font.render(stat, True, theme.TEXT)
            screen.blit(surf, surf.get_rect(center=(start_x + i * gap, 112)))

    def draw_sub_stats(self, screen: pygame.Surface, text: str) -> None:
        surf = self.small_font.render(text, True, theme.MUTED_TEXT)
        screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, 138)))

    def draw_footer(self, screen: pygame.Surface, text: str) -> None:
        surf = self.small_font.render(text, True, theme.MUTED_TEXT)
        screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 28)))

    def draw_game_over(
        self,
        screen: pygame.Surface,
        play_rect: pygame.Rect,
        title: str,
        score_text: str,
        summary_text: str,
    ) -> None:
        panel = pygame.Rect(0, 0, 600, 240)
        panel.center = play_rect.center

        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        screen.blit(overlay, panel.topleft)

        pygame.draw.rect(screen, theme.ACCENT, panel, width=2, border_radius=theme.RADIUS_MEDIUM)

        title_surf = self.big_font.render(title, True, theme.TEXT)
        score_surf = self.info_font.render(score_text, True, theme.TEXT)
        summary_surf = self.info_font.render(summary_text, True, theme.TEXT)

        controls = self.small_font.render(
            "Press Space / Enter / Click / F5 to restart   |   Esc to go back",
            True,
            theme.MUTED_TEXT,
        )

        screen.blit(title_surf, title_surf.get_rect(center=(panel.centerx, panel.top + 58)))
        screen.blit(score_surf, score_surf.get_rect(center=(panel.centerx, panel.top + 118)))
        screen.blit(summary_surf, summary_surf.get_rect(center=(panel.centerx, panel.top + 154)))
        screen.blit(controls, controls.get_rect(center=(panel.centerx, panel.top + 198)))

    def draw_pause_overlay(
        self,
        screen: pygame.Surface,
        play_rect: pygame.Rect,
        title: str = "Paused",
        subtitle: str = "Press P to resume",
        help_text: str = "F5 restart   |   Esc back",
    ) -> None:
        panel = pygame.Rect(0, 0, 520, 210)
        panel.center = play_rect.center

        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 220))
        screen.blit(overlay, panel.topleft)

        pygame.draw.rect(screen, theme.ACCENT, panel, width=2, border_radius=theme.RADIUS_MEDIUM)

        title_surf = self.big_font.render(title, True, theme.TEXT)
        subtitle_surf = self.info_font.render(subtitle, True, theme.TEXT)
        help_surf = self.small_font.render(help_text, True, theme.MUTED_TEXT)

        screen.blit(title_surf, title_surf.get_rect(center=(panel.centerx, panel.top + 62)))
        screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(panel.centerx, panel.top + 122)))
        screen.blit(help_surf, help_surf.get_rect(center=(panel.centerx, panel.top + 166)))

    def draw_floating_texts(self, screen: pygame.Surface, popups: list[dict]) -> None:
        for popup in popups:
            text_surface = self.info_font.render(popup["text"], True, popup["color"])
            text_surface.set_alpha(max(0, min(255, int(popup.get("alpha", 255)))))
            screen.blit(text_surface, text_surface.get_rect(center=(int(popup["pos"].x), int(popup["pos"].y))))