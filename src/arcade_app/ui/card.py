from __future__ import annotations

import pygame

from arcade_app.ui import theme


class Card:
    def __init__(
        self,
        rect: pygame.Rect,
        title: str,
        description: str,
        footer_text: str | None = None,
    ) -> None:
        self.rect = rect
        self.title = title
        self.description = description
        self.footer_text = footer_text

    def wrap_text(
        self,
        text: str,
        font: pygame.font.Font,
        max_width: int,
    ) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]

        for word in words[1:]:
            test = f"{current} {word}"
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    def draw(
        self,
        screen: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        is_selected: bool = False,
        is_hovered: bool = False,
    ) -> None:
        fill = theme.SURFACE
        border = theme.SURFACE_ALT
        border_width = 2

        if is_hovered:
            fill = theme.SURFACE_ALT

        if is_selected:
            border = theme.ACCENT
            border_width = 4

        pygame.draw.rect(screen, fill, self.rect, border_radius=theme.RADIUS_MEDIUM)
        pygame.draw.rect(
            screen,
            border,
            self.rect,
            width=border_width,
            border_radius=theme.RADIUS_MEDIUM,
        )

        title = title_font.render(self.title, True, theme.TEXT)
        title_rect = title.get_rect(midtop=(self.rect.centerx, self.rect.top + 18))
        screen.blit(title, title_rect)

        desc_lines = self.wrap_text(self.description, body_font, self.rect.width - 28)
        current_y = title_rect.bottom + 10

        max_desc_lines = 3
        for line in desc_lines[:max_desc_lines]:
            desc = body_font.render(line, True, theme.MUTED_TEXT)
            desc_rect = desc.get_rect(centerx=self.rect.centerx, top=current_y)
            screen.blit(desc, desc_rect)
            current_y += desc.get_height() + 4

        if self.footer_text:
            footer = body_font.render(self.footer_text, True, theme.MUTED_TEXT)
            footer_rect = footer.get_rect(midbottom=(self.rect.centerx, self.rect.bottom - 16))
            screen.blit(footer, footer_rect)