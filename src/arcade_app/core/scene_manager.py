from __future__ import annotations

import random

import pygame

from arcade_app.core.game_base import GameBase
from arcade_app.core.scene_base import SceneBase


class SceneManager:
    def __init__(self, app) -> None:
        self.app = app
        self.current_scene: SceneBase | None = None

    def _build_summary(self, game_scene: GameBase, payload: dict, run_result) -> dict:
        existing_stats = self.app.save_data.get_game_stats(game_scene.game_id)
        previous_best_score = existing_stats.get("best_score") if isinstance(existing_stats, dict) else None
        previous_best_round = existing_stats.get("best_round") if isinstance(existing_stats, dict) else None
        previous_best_wave = existing_stats.get("best_wave") if isinstance(existing_stats, dict) else None
        previous_best_lines = existing_stats.get("best_lines") if isinstance(existing_stats, dict) else None
        previous_best_hits = existing_stats.get("best_hits") if isinstance(existing_stats, dict) else None
        previous_best_accuracy = existing_stats.get("best_accuracy") if isinstance(existing_stats, dict) else None
        previous_best_reaction = existing_stats.get("best_reaction_ms") if isinstance(existing_stats, dict) else None

        score = payload.get("score") if isinstance(payload.get("score"), int) else None
        is_new_best_score = isinstance(score, int) and (previous_best_score is None or score > previous_best_score)

        stat_highlights: list[str] = []
        if isinstance(payload.get("wave"), int) and (previous_best_wave is None or payload["wave"] > previous_best_wave):
            stat_highlights.append(f"New best wave: {payload['wave']}")
        if isinstance(payload.get("round"), int) and (previous_best_round is None or payload["round"] > previous_best_round):
            stat_highlights.append(f"New best round: {payload['round']}")
        if isinstance(payload.get("lines"), int) and (previous_best_lines is None or payload["lines"] > previous_best_lines):
            stat_highlights.append(f"New best lines: {payload['lines']}")
        if isinstance(payload.get("hits"), int) and (previous_best_hits is None or payload["hits"] > previous_best_hits):
            stat_highlights.append(f"New best hits: {payload['hits']}")
        if isinstance(payload.get("accuracy"), (int, float)) and (previous_best_accuracy is None or float(payload['accuracy']) > float(previous_best_accuracy)):
            stat_highlights.append(f"New best accuracy: {float(payload['accuracy']):.1f}%")
        if isinstance(payload.get("reaction_ms"), int) and (previous_best_reaction is None or payload["reaction_ms"] < previous_best_reaction):
            stat_highlights.append(f"Fastest reaction: {payload['reaction_ms']} ms")

        active_profile_entry = self.app.save_data.get_active_profile_leaderboard_entry(game_scene.game_id)
        leaderboard_rank = active_profile_entry.get("rank") if isinstance(active_profile_entry, dict) else None

        metadata = dict(run_result.metadata)
        return {
            "game_id": game_scene.game_id,
            "title": getattr(game_scene, "title", game_scene.game_id),
            "score": run_result.score,
            "duration_seconds": run_result.duration_seconds,
            "metadata": metadata,
            "is_new_best_score": is_new_best_score,
            "leaderboard_rank": leaderboard_rank,
            "stat_highlights": stat_highlights,
            "profile_name": self.app.save_data.get_active_profile_name(),
            "challenge_id": metadata.get("challenge_id"),
            "challenge_mode": metadata.get("challenge_mode"),
            "challenge_title": metadata.get("challenge_title"),
            "challenge_date": metadata.get("challenge_date"),
            "seed": metadata.get("seed"),
        }

    def _prepare_scene(self, scene: SceneBase) -> None:
        launch_context = getattr(scene, "launch_context", None)
        if isinstance(launch_context, dict):
            seed = launch_context.get("seed")
            if isinstance(seed, int):
                random.seed(seed)

    def go_to(self, scene: SceneBase) -> None:
        if self.current_scene is not None:
            if isinstance(self.current_scene, GameBase):
                payload = self.current_scene.get_persistence_payload()
                run_result = self.current_scene.build_run_result()
                payload = {**payload, "duration_seconds": run_result.duration_seconds}
                self.app.save_data.record_game_session(self.current_scene.game_id, payload)

                summary = self._build_summary(self.current_scene, payload, run_result)
                self.app.save_data.store_last_run_summary(summary)
                if summary.get("challenge_id") and summary.get("challenge_mode") == "daily":
                    self.app.save_data.record_daily_challenge_result(summary)

                from arcade_app.scenes.run_summary_scene import RunSummaryScene

                if not isinstance(scene, RunSummaryScene) and self.current_scene.should_show_run_summary():
                    self.current_scene.exit()
                    self.current_scene = RunSummaryScene(self.app, summary=summary, next_scene=scene)
                    self._prepare_scene(self.current_scene)
                    self.current_scene.enter()
                    return
            self.current_scene.exit()

        self.current_scene = scene
        self._prepare_scene(self.current_scene)
        self.current_scene.enter()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_events(events)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        if self.current_scene is not None:
            self.current_scene.render(screen)
