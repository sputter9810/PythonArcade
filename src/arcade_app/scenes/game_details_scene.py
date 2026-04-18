from __future__ import annotations

import pygame

from arcade_app.core.scene_base import SceneBase
from arcade_app.platform.challenges import build_daily_challenge, build_launch_context
from arcade_app.platform.library import format_metric_rows
from arcade_app.registry import create_game_scene, get_game_by_id
from arcade_app.ui import theme


class GameDetailsScene(SceneBase):
    def __init__(self, app, game_id: str, return_scene: str = "library") -> None:
        super().__init__(app)
        self.game_id = game_id
        self.return_scene = return_scene
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", 44, bold=True)
        self.body_font = pygame.font.SysFont("arial", 24)
        self.meta_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 16)

    def game(self) -> dict | None:
        return get_game_by_id(self.game_id)

    def launch_game(self) -> None:
        game = self.game()
        if game is None:
            return
        self.app.save_data.set_last_played(game["id"])
        self.app.scene_manager.go_to(create_game_scene(game["id"], self.app))

    def launch_daily_challenge(self) -> None:
        challenge = build_daily_challenge(preferred_game_id=self.game_id)
        if not challenge:
            return
        self.app.save_data.set_last_played(self.game_id)
        self.app.scene_manager.go_to(create_game_scene(self.game_id, self.app, launch_context=build_launch_context(challenge)))

    def go_back(self) -> None:
        from arcade_app.scenes.game_select_scene import GameSelectScene
        from arcade_app.scenes.main_menu_scene import MainMenuScene
        if self.return_scene == "main_menu":
            self.app.scene_manager.go_to(MainMenuScene(self.app))
        else:
            self.app.scene_manager.go_to(GameSelectScene(self.app, initial_game_id=self.game_id))

    def open_achievements(self) -> None:
        from arcade_app.scenes.achievements_scene import AchievementsScene
        self.app.scene_manager.go_to(AchievementsScene(self.app, return_scene="library"))

    def open_daily_challenge_card(self) -> None:
        from arcade_app.scenes.daily_challenge_scene import DailyChallengeScene
        self.app.scene_manager.go_to(DailyChallengeScene(self.app, preferred_game_id=self.game_id, return_scene="library"))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self.go_back()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.launch_game()
            elif event.key == pygame.K_f:
                self.app.save_data.toggle_favorite_game(self.game_id)
            elif event.key == pygame.K_h:
                self.open_achievements()
            elif event.key == pygame.K_c:
                self.open_daily_challenge_card()

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font and self.body_font and self.meta_font and self.small_font
        screen.fill(theme.BACKGROUND)
        game = self.game()
        if game is None:
            missing = self.title_font.render("Game not found", True, theme.TEXT)
            screen.blit(missing, missing.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
            return

        stats = self.app.save_data.get_game_stats(self.game_id)
        is_favorite = self.app.save_data.is_favorite(self.game_id)
        profile = self.app.save_data.get_profile_summary()
        achievements = self.app.save_data.get_achievement_rows()
        unlocked_count = profile.get("achievement_count", 0)
        total_count = len(achievements)
        challenge = build_daily_challenge(preferred_game_id=self.game_id)
        challenge_record = self.app.save_data.get_daily_challenge_record(challenge["id"]) if challenge else None

        panel = pygame.Rect(100, 70, screen.get_width() - 200, screen.get_height() - 140)
        left_panel = pygame.Rect(panel.x, panel.y, int(panel.width * 0.58), panel.height)
        right_panel = pygame.Rect(left_panel.right + 24, panel.y, panel.right - (left_panel.right + 24), panel.height)
        pygame.draw.rect(screen, theme.SURFACE, left_panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, left_panel, width=2, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE, right_panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, right_panel, width=2, border_radius=theme.RADIUS_LARGE)

        title = self.title_font.render(game["title"], True, theme.TEXT)
        screen.blit(title, title.get_rect(topleft=(left_panel.x + 28, left_panel.y + 28)))
        favorite_label = "★ Favorite" if is_favorite else "☆ Not Favorite"
        favorite_surface = self.meta_font.render(favorite_label, True, theme.WARNING if is_favorite else theme.MUTED_TEXT)
        screen.blit(favorite_surface, favorite_surface.get_rect(topright=(left_panel.right - 28, left_panel.y + 38)))

        subtitle = self.body_font.render(
            f"{game.get('category', 'Unknown')}  |  {', '.join(game.get('modes', [])) or 'Unknown'}  |  {game.get('status_label', 'Ready')}",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(subtitle, subtitle.get_rect(topleft=(left_panel.x + 28, left_panel.y + 92)))

        description_lines = self._wrap_text(str(game.get("description", "")), self.body_font, left_panel.width - 56)
        current_y = left_panel.y + 150
        for line in description_lines:
            screen.blit(self.body_font.render(line, True, theme.TEXT), (left_panel.x + 28, current_y))
            current_y += self.body_font.get_height() + 6

        current_y += 12
        for bullet in game.get("detail_bullets", []):
            bullet_lines = self._wrap_text(f"• {bullet}", self.meta_font, left_panel.width - 56)
            for line in bullet_lines:
                surface = self.meta_font.render(line, True, theme.MUTED_TEXT)
                screen.blit(surface, (left_panel.x + 28, current_y))
                current_y += self.meta_font.get_height() + 6
            current_y += 4

        if challenge:
            challenge_rect = pygame.Rect(left_panel.x + 24, left_panel.bottom - 192, left_panel.width - 48, 104)
            pygame.draw.rect(screen, theme.SURFACE_ALT, challenge_rect, border_radius=theme.RADIUS_MEDIUM)
            challenge_title = self.meta_font.render("Today's Seeded Challenge", True, theme.WARNING)
            challenge_desc = self.small_font.render(challenge["description"], True, theme.MUTED_TEXT)
            challenge_meta = self.small_font.render(f"Seed: {challenge['seed']}  |  Press C to open / launch", True, theme.ACCENT)
            progress_text = "No run recorded today yet"
            if challenge_record:
                best_score = challenge_record.get("best_score")
                best_duration = challenge_record.get("best_duration_seconds")
                progress_text = f"Attempts: {challenge_record.get('attempts', 0)}"
                if best_score is not None:
                    progress_text += f"  |  Best Score: {best_score}"
                elif best_duration is not None:
                    progress_text += f"  |  Best Time: {float(best_duration):.2f}s"
            progress_surface = self.small_font.render(progress_text, True, theme.MUTED_TEXT)
            screen.blit(challenge_title, challenge_title.get_rect(topleft=(challenge_rect.x + 16, challenge_rect.y + 14)))
            screen.blit(challenge_desc, challenge_desc.get_rect(topleft=(challenge_rect.x + 16, challenge_rect.y + 44)))
            screen.blit(challenge_meta, challenge_meta.get_rect(topleft=(challenge_rect.x + 16, challenge_rect.y + 68)))
            screen.blit(progress_surface, progress_surface.get_rect(topleft=(challenge_rect.x + 16, challenge_rect.y + 86)))

        controls = self.small_font.render(
            "Enter/Space: Play  |  C: Daily Challenge  |  F: Favorite  |  H: Achievements  |  Backspace/Esc: Back",
            True,
            theme.MUTED_TEXT,
        )
        screen.blit(controls, controls.get_rect(topleft=(left_panel.x + 28, left_panel.bottom - 44)))

        stats_title = self.body_font.render("Game Stats", True, theme.TEXT)
        screen.blit(stats_title, stats_title.get_rect(topleft=(right_panel.x + 24, right_panel.y + 24)))
        progress_surface = self.meta_font.render(f"Profile Progress: {unlocked_count}/{total_count} achievements unlocked", True, theme.WARNING)
        screen.blit(progress_surface, progress_surface.get_rect(topleft=(right_panel.x + 24, right_panel.y + 60)))

        rows = format_metric_rows(stats)
        current_y = right_panel.y + 106
        for row in rows:
            row_surface = self.meta_font.render(row, True, theme.MUTED_TEXT)
            screen.blit(row_surface, row_surface.get_rect(topleft=(right_panel.x + 24, current_y)))
            current_y += self.meta_font.get_height() + 12

        current_y += 20
        recent_unlocks = self.app.save_data.get_recent_achievement_unlocks()
        unlock_heading = self.meta_font.render("Recent Achievement Unlocks", True, theme.TEXT)
        screen.blit(unlock_heading, unlock_heading.get_rect(topleft=(right_panel.x + 24, current_y)))
        current_y += 34
        if recent_unlocks:
            for row in recent_unlocks[:4]:
                unlock_surface = self.small_font.render(f"• {row['name']}", True, theme.ACCENT)
                screen.blit(unlock_surface, unlock_surface.get_rect(topleft=(right_panel.x + 24, current_y)))
                current_y += self.small_font.get_height() + 10
        else:
            empty = self.small_font.render("No recent unlocks on this profile yet.", True, theme.MUTED_TEXT)
            screen.blit(empty, empty.get_rect(topleft=(right_panel.x + 24, current_y)))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
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
