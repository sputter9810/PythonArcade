from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.ui import theme


class RunSummaryScene(SceneBase):
    def __init__(self, app, summary: dict, next_scene: SceneBase) -> None:
        super().__init__(app)
        self.summary = summary
        self.next_scene = next_scene
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.body_font = pygame.font.SysFont("arial", 24)
        self.meta_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 16)

    def continue_to_next(self) -> None:
        self.app.scene_manager.go_to(self.next_scene)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_BACKSPACE):
                self.continue_to_next()

    def update(self, dt: float) -> None:
        return

    def _format_metadata_rows(self) -> list[str]:
        metadata = self.summary.get("metadata", {})
        if not isinstance(metadata, dict):
            return []
        rows: list[str] = []
        label_map = {
            "wave": "Wave",
            "round": "Round",
            "lines": "Lines",
            "hits": "Hits",
            "accuracy": "Accuracy",
            "reaction_ms": "Best Reaction",
            "difficulty": "Difficulty",
            "seed": "Seed",
        }
        for key in ("difficulty", "wave", "round", "lines", "hits", "accuracy", "reaction_ms", "seed"):
            value = metadata.get(key)
            if value is None:
                continue
            if key == "accuracy":
                rows.append(f"{label_map[key]}: {float(value):.1f}%")
            elif key == "reaction_ms":
                rows.append(f"{label_map[key]}: {value} ms")
            else:
                rows.append(f"{label_map[key]}: {value}")
        return rows

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None
        assert self.small_font is not None

        screen.fill(theme.BACKGROUND)
        panel = pygame.Rect(220, 120, screen.get_width() - 440, screen.get_height() - 240)
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel, width=2, border_radius=theme.RADIUS_LARGE)

        title = self.title_font.render(f"{self.summary.get('title', 'Run')} Summary", True, theme.TEXT)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, panel.y + 54)))

        if self.summary.get("challenge_id"):
            badge = self.meta_font.render(self.summary.get("challenge_title", "Daily Challenge"), True, theme.WARNING)
            screen.blit(badge, badge.get_rect(center=(screen.get_width() // 2, panel.y + 92)))
            profile_y = panel.y + 124
        else:
            profile_y = panel.y + 96

        profile = self.meta_font.render(f"Profile: {self.summary.get('profile_name', 'Player')}", True, theme.MUTED_TEXT)
        screen.blit(profile, profile.get_rect(center=(screen.get_width() // 2, profile_y)))

        y = panel.y + 170
        score = self.summary.get("score")
        score_text = f"Score: {score}" if score is not None else "Score: —"
        duration = self.summary.get("duration_seconds")
        duration_text = f"Duration: {float(duration):.2f}s" if isinstance(duration, (int, float)) else "Duration: —"
        rank = self.summary.get("leaderboard_rank")
        rank_text = f"Leaderboard Rank: #{rank}" if isinstance(rank, int) else "Leaderboard Rank: Not ranked yet"

        for row in (score_text, duration_text, rank_text):
            surface = self.body_font.render(row, True, theme.TEXT)
            screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
            y += 42

        if self.summary.get("is_new_best_score"):
            badge = self.body_font.render("New personal best score!", True, theme.SUCCESS)
            screen.blit(badge, badge.get_rect(center=(screen.get_width() // 2, y + 6)))
            y += 46

        metadata_rows = self._format_metadata_rows()
        for row in metadata_rows:
            surface = self.meta_font.render(row, True, theme.MUTED_TEXT)
            screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
            y += 30

        highlights = self.summary.get("stat_highlights", [])
        if isinstance(highlights, list) and highlights:
            y += 14
            heading = self.body_font.render("Highlights", True, theme.TEXT)
            screen.blit(heading, heading.get_rect(center=(screen.get_width() // 2, y)))
            y += 40
            for highlight in highlights[:4]:
                surface = self.meta_font.render(f"• {highlight}", True, theme.ACCENT)
                screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
                y += 28

        footer = self.small_font.render("Enter / Space / Esc: Continue", True, theme.MUTED_TEXT)
        screen.blit(footer, footer.get_rect(center=(screen.get_width() // 2, panel.bottom - 34)))
