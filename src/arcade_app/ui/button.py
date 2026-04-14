from __future__ import annotations

import pygame

from arcade_app.ui import theme


class Button:
    def __init__(self, rect: pygame.Rect, label: str) -> None:
        self.rect = rect
        self.label = label

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, theme.SURFACE_ALT, self.rect, border_radius=theme.RADIUS_MEDIUM)
        text = font.render(self.label, True, theme.TEXT)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
