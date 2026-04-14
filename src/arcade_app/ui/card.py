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
        hero_text: str | None = None,
        badges: list[str] | None = None,
    ) -> None:
        self.rect = rect
        self.title = title
        self.description = description
        self.footer_text = footer_text
        self.hero_text = hero_text
        self.badges = badges or []

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
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word

        lines.append(current)
        return lines

    def _truncate_lines_to_fit(
        self,
        lines: list[str],
        font: pygame.font.Font,
        max_lines: int,
        max_width: int,
    ) -> list[str]:
        if len(lines) <= max_lines:
            return lines

        trimmed = lines[:max_lines]
        last = trimmed[-1]

        while last and font.size(f"{last}...")[0] > max_width:
            last = last[:-1].rstrip()

        trimmed[-1] = f"{last}..." if last else "..."
        return trimmed

    def _hero_area(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.left + 18,
            self.rect.top + 18,
            self.rect.width - 36,
            58,
        )

    def _icon_color(self, category: str) -> tuple[int, int, int]:
        category = category.lower()
        mapping = {
            "arcade": theme.ACCENT,
            "action": theme.WARNING,
            "puzzle": (112, 196, 255),
            "strategy": (186, 148, 255),
            "memory": (255, 170, 90),
            "skill": (96, 232, 170),
            "word": (255, 124, 124),
        }
        return mapping.get(category, theme.ACCENT)

    def _draw_arcade_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        cabinet = rect.inflate(-rect.width // 2, -12)
        cabinet.center = rect.center
        cabinet.height = 34
        pygame.draw.rect(screen, color, cabinet, border_radius=8)

        screen_rect = pygame.Rect(0, 0, cabinet.width - 18, 10)
        screen_rect.midtop = (cabinet.centerx, cabinet.top + 6)
        pygame.draw.rect(screen, theme.BACKGROUND, screen_rect, border_radius=4)

        stick_base = pygame.Rect(cabinet.left + 10, cabinet.bottom - 12, 10, 6)
        pygame.draw.rect(screen, theme.BACKGROUND, stick_base, border_radius=3)
        pygame.draw.circle(screen, theme.BACKGROUND, (stick_base.centerx, stick_base.top - 5), 4)

        for i in range(3):
            pygame.draw.circle(
                screen,
                theme.BACKGROUND,
                (cabinet.right - 16 - i * 12, cabinet.bottom - 9),
                4,
            )

    def _draw_action_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        center = rect.center
        points = [
            (center[0] - 22, center[1] + 12),
            (center[0] - 4, center[1] - 16),
            (center[0] + 4, center[1] - 4),
            (center[0] + 18, center[1] - 20),
            (center[0] + 8, center[1] + 2),
            (center[0] + 26, center[1] + 2),
            (center[0] - 2, center[1] + 20),
            (center[0] + 2, center[1] + 6),
        ]
        pygame.draw.polygon(screen, color, points)

    def _draw_puzzle_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        piece = pygame.Rect(0, 0, 34, 26)
        piece.center = rect.center
        pygame.draw.rect(screen, color, piece, border_radius=6)
        pygame.draw.circle(screen, color, (piece.centerx, piece.top - 2), 7)
        pygame.draw.circle(screen, theme.BACKGROUND, (piece.right + 2, piece.centery), 7)
        pygame.draw.circle(screen, color, (piece.left + 7, piece.bottom + 1), 6)

    def _draw_strategy_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        grid = pygame.Rect(0, 0, 42, 42)
        grid.center = rect.center
        pygame.draw.rect(screen, color, grid, width=3, border_radius=6)

        third_w = grid.width // 3
        third_h = grid.height // 3
        for i in range(1, 3):
            x = grid.left + i * third_w
            y = grid.top + i * third_h
            pygame.draw.line(screen, color, (x, grid.top + 4), (x, grid.bottom - 4), 2)
            pygame.draw.line(screen, color, (grid.left + 4, y), (grid.right - 4, y), 2)

        pygame.draw.circle(screen, color, (grid.left + third_w // 2 + 4, grid.top + third_h // 2 + 4), 5, width=2)
        pygame.draw.line(
            screen,
            color,
            (grid.left + third_w + 8, grid.top + third_h + 8),
            (grid.left + 2 * third_w - 2, grid.top + 2 * third_h - 2),
            3,
        )
        pygame.draw.line(
            screen,
            color,
            (grid.left + 2 * third_w - 2, grid.top + third_h + 8),
            (grid.left + third_w + 8, grid.top + 2 * third_h - 2),
            3,
        )

    def _draw_memory_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        back = pygame.Rect(0, 0, 24, 32)
        front = pygame.Rect(0, 0, 24, 32)
        back.center = (rect.centerx - 8, rect.centery + 2)
        front.center = (rect.centerx + 10, rect.centery - 2)

        pygame.draw.rect(screen, color, back, border_radius=6)
        pygame.draw.rect(screen, theme.BACKGROUND, back.inflate(-10, -12), border_radius=4)

        pygame.draw.rect(screen, color, front, border_radius=6)
        pygame.draw.circle(screen, theme.BACKGROUND, front.center, 5)

    def _draw_skill_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        center = rect.center
        pygame.draw.circle(screen, color, center, 18, width=3)
        pygame.draw.circle(screen, color, center, 10, width=3)
        pygame.draw.circle(screen, color, center, 3)
        pygame.draw.line(screen, color, (center[0] - 24, center[1]), (center[0] - 8, center[1]), 2)
        pygame.draw.line(screen, color, (center[0] + 8, center[1]), (center[0] + 24, center[1]), 2)
        pygame.draw.line(screen, color, (center[0], center[1] - 24), (center[0], center[1] - 8), 2)
        pygame.draw.line(screen, color, (center[0], center[1] + 8), (center[0], center[1] + 24), 2)

    def _draw_word_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        bubble = pygame.Rect(0, 0, 42, 28)
        bubble.center = (rect.centerx, rect.centery - 2)
        pygame.draw.rect(screen, color, bubble, border_radius=12)

        tail = [
            (bubble.left + 12, bubble.bottom - 2),
            (bubble.left + 18, bubble.bottom + 10),
            (bubble.left + 24, bubble.bottom - 2),
        ]
        pygame.draw.polygon(screen, color, tail)

        line_y = bubble.centery
        pygame.draw.line(screen, theme.BACKGROUND, (bubble.left + 10, line_y), (bubble.right - 10, line_y), 3)
        pygame.draw.line(
            screen,
            theme.BACKGROUND,
            (bubble.left + 14, line_y - 7),
            (bubble.right - 14, line_y - 7),
            2,
        )

    def _draw_default_icon(self, screen: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        pygame.draw.circle(screen, color, rect.center, 16)
        pygame.draw.circle(screen, theme.BACKGROUND, rect.center, 7)

    def _draw_hero_icon(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        category = self.badges[0] if self.badges else ""
        color = self._icon_color(category)

        category_lower = category.lower()
        if category_lower == "arcade":
            self._draw_arcade_icon(screen, rect, color)
        elif category_lower == "action":
            self._draw_action_icon(screen, rect, color)
        elif category_lower == "puzzle":
            self._draw_puzzle_icon(screen, rect, color)
        elif category_lower == "strategy":
            self._draw_strategy_icon(screen, rect, color)
        elif category_lower == "memory":
            self._draw_memory_icon(screen, rect, color)
        elif category_lower == "skill":
            self._draw_skill_icon(screen, rect, color)
        elif category_lower == "word":
            self._draw_word_icon(screen, rect, color)
        else:
            self._draw_default_icon(screen, rect, color)

    def _draw_badges_and_meta_row(
        self,
        screen: pygame.Surface,
        badge_font: pygame.font.Font,
        meta_font: pygame.font.Font,
        start_y: int,
    ) -> int:
        left_x = self.rect.left + 18
        right_x = self.rect.right - 18
        y = start_y
        badge_height = 28
        gap = 8

        current_x = left_x
        for badge in self.badges[:3]:
            badge_surface = badge_font.render(badge, True, theme.TEXT)
            badge_rect = pygame.Rect(
                current_x,
                y,
                badge_surface.get_width() + 20,
                badge_height,
            )
            pygame.draw.rect(screen, theme.SURFACE_ALT, badge_rect, border_radius=999)
            screen.blit(badge_surface, badge_surface.get_rect(center=badge_rect.center))
            current_x = badge_rect.right + gap

        if self.footer_text:
            meta_surface = meta_font.render(self.footer_text, True, theme.MUTED_TEXT)
            meta_rect = meta_surface.get_rect(
                right=right_x,
                centery=y + badge_height // 2,
            )
            screen.blit(meta_surface, meta_rect)

        return y + badge_height

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

        hero_rect = self._hero_area()
        pygame.draw.rect(screen, theme.BACKGROUND, hero_rect, border_radius=theme.RADIUS_SMALL)
        pygame.draw.rect(screen, theme.SURFACE_ALT, hero_rect, width=1, border_radius=theme.RADIUS_SMALL)

        self._draw_hero_icon(screen, hero_rect)

        title_surface = title_font.render(self.title, True, theme.TEXT)
        title_rect = title_surface.get_rect(center=(self.rect.centerx, hero_rect.bottom + 34))
        screen.blit(title_surface, title_rect)

        badge_font = pygame.font.SysFont("arial", 15)
        meta_font = pygame.font.SysFont("arial", 16)
        meta_row_bottom = self._draw_badges_and_meta_row(
            screen,
            badge_font,
            meta_font,
            title_rect.bottom + 16,
        )

        desc_font = pygame.font.SysFont("arial", 20)
        desc_left = self.rect.left + 18
        desc_right = self.rect.right - 18
        desc_width = desc_right - desc_left
        desc_top = meta_row_bottom + 18
        desc_bottom = self.rect.bottom - 22
        line_height = desc_font.get_height() + 4
        available_height = max(0, desc_bottom - desc_top)
        max_lines = max(1, available_height // line_height)

        desc_lines = self.wrap_text(self.description, desc_font, desc_width)
        desc_lines = self._truncate_lines_to_fit(desc_lines, desc_font, max_lines, desc_width)

        current_y = desc_top
        for line in desc_lines:
            desc_surface = desc_font.render(line, True, theme.MUTED_TEXT)
            screen.blit(desc_surface, (desc_left, current_y))
            current_y += line_height