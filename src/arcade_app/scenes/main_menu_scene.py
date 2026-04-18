from __future__ import annotations

import pygame

from arcade_app.constants import APP_VERSION
from arcade_app.core.scene_base import SceneBase
from arcade_app.platform.challenges import build_daily_challenge
from arcade_app.registry import get_game_by_id
from arcade_app.ui import theme


class MainMenuScene(SceneBase):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.title_font: pygame.font.Font | None = None
        self.body_font: pygame.font.Font | None = None
        self.meta_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.SysFont("arial", theme.TITLE_SIZE, bold=True)
        self.body_font = pygame.font.SysFont("arial", theme.BODY_SIZE)
        self.meta_font = pygame.font.SysFont("arial", theme.CAPTION_SIZE)
        self.small_font = pygame.font.SysFont("arial", 16)

    def open_daily_challenge(self) -> None:
        from arcade_app.scenes.daily_challenge_scene import DailyChallengeScene
        self.app.scene_manager.go_to(DailyChallengeScene(self.app, return_scene="menu"))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_1:
                from arcade_app.scenes.game_select_scene import GameSelectScene
                self.app.scene_manager.go_to(GameSelectScene(self.app))
            elif event.key == pygame.K_2:
                from arcade_app.scenes.settings_scene import SettingsScene
                self.app.scene_manager.go_to(SettingsScene(self.app))
            elif event.key == pygame.K_3:
                from arcade_app.scenes.credits_scene import CreditsScene
                self.app.scene_manager.go_to(CreditsScene(self.app))
            elif event.key == pygame.K_4:
                from arcade_app.scenes.achievements_scene import AchievementsScene
                self.app.scene_manager.go_to(AchievementsScene(self.app, return_scene="menu"))
            elif event.key == pygame.K_5:
                self.open_daily_challenge()
            elif event.key == pygame.K_p:
                from arcade_app.scenes.profile_manager_scene import ProfileManagerScene
                self.app.scene_manager.go_to(ProfileManagerScene(self.app, return_scene="menu"))
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()

    def update(self, dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        assert self.title_font is not None
        assert self.body_font is not None
        assert self.meta_font is not None
        assert self.small_font is not None

        screen.fill(theme.BACKGROUND)
        active_profile = self.app.save_data.get_profile_summary()
        challenge = build_daily_challenge()
        challenge_record = self.app.save_data.get_daily_challenge_record(challenge["id"]) if challenge else None

        title = self.title_font.render("Arcade", True, theme.TEXT)
        subtitle = self.body_font.render(
            "1: Play  |  2: Settings  |  3: Credits  |  4: Achievements  |  5: Daily Challenge  |  P: Profiles  |  Esc: Quit",
            True,
            theme.MUTED_TEXT,
        )
        version = self.meta_font.render(f"Version {APP_VERSION}", True, theme.MUTED_TEXT)
        profile = self.meta_font.render(f"Active Profile: {active_profile['name']}", True, theme.ACCENT)
        sessions = self.meta_font.render(
            f"Sessions: {active_profile['total_sessions']}  |  Unique Games: {active_profile['unique_games']}",
            True,
            theme.MUTED_TEXT,
        )
        achievements = self.meta_font.render(
            f"Achievements: {active_profile['achievement_count']} unlocked",
            True,
            theme.WARNING,
        )

        last_played_id = self.app.save_data.get_last_played_game_id()
        if last_played_id is None:
            last_played_text = "Last Played: None yet"
        else:
            last_played_game = get_game_by_id(last_played_id)
            last_played_label = last_played_game["title"] if last_played_game is not None else last_played_id
            last_played_text = f"Last Played: {last_played_label}"
        last_played = self.meta_font.render(last_played_text, True, theme.MUTED_TEXT)

        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 164)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 236)))
        screen.blit(version, version.get_rect(center=(screen.get_width() // 2, 296)))
        screen.blit(profile, profile.get_rect(center=(screen.get_width() // 2, 334)))
        screen.blit(sessions, sessions.get_rect(center=(screen.get_width() // 2, 366)))
        screen.blit(achievements, achievements.get_rect(center=(screen.get_width() // 2, 398)))
        screen.blit(last_played, last_played.get_rect(center=(screen.get_width() // 2, 430)))

        panel = pygame.Rect((screen.get_width() - 760) // 2, 500, 760, 180)
        pygame.draw.rect(screen, theme.SURFACE, panel, border_radius=theme.RADIUS_LARGE)
        pygame.draw.rect(screen, theme.SURFACE_ALT, panel, width=2, border_radius=theme.RADIUS_LARGE)

        heading = self.body_font.render("Today's Daily Challenge", True, theme.TEXT)
        screen.blit(heading, heading.get_rect(topleft=(panel.x + 24, panel.y + 20)))

        if challenge:
            title_surface = self.meta_font.render(challenge["title"], True, theme.ACCENT)
            desc_surface = self.small_font.render(challenge["description"], True, theme.MUTED_TEXT)
            seed_surface = self.small_font.render(f"Seed: {challenge['seed']}  |  Game: {challenge['game_title']}", True, theme.MUTED_TEXT)
            progress_text = "No attempt yet today"
            if challenge_record:
                best_score = challenge_record.get("best_score")
                best_duration = challenge_record.get("best_duration_seconds")
                if best_score is not None:
                    progress_text = f"Best Score Today: {best_score}"
                elif best_duration is not None:
                    progress_text = f"Best Time Today: {float(best_duration):.2f}s"
                progress_text += f"  |  Attempts: {challenge_record.get('attempts', 0)}"
            progress_surface = self.small_font.render(progress_text, True, theme.WARNING if challenge_record else theme.MUTED_TEXT)
            footer = self.small_font.render("Press 5 to open the challenge card and launch the seeded run.", True, theme.MUTED_TEXT)
            screen.blit(title_surface, title_surface.get_rect(topleft=(panel.x + 24, panel.y + 60)))
            screen.blit(desc_surface, desc_surface.get_rect(topleft=(panel.x + 24, panel.y + 92)))
            screen.blit(seed_surface, seed_surface.get_rect(topleft=(panel.x + 24, panel.y + 120)))
            screen.blit(progress_surface, progress_surface.get_rect(topleft=(panel.x + 24, panel.y + 146)))
            screen.blit(footer, footer.get_rect(topright=(panel.right - 24, panel.y + 146)))
