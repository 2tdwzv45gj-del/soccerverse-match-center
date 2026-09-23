from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.commentary_replay import ReplayMode, ReplayScheduleItem
from src.score_progression import ScoreProgressionEngine


@dataclass(frozen=True)
class ReplayState:
    replay_mode: ReplayMode
    elapsed_seconds: float
    match_minute: int
    current_scene: ReplayScheduleItem | None
    visible_scenes: tuple[ReplayScheduleItem, ...]
    home_score: int
    away_score: int


class ReplayStateEngine:
    """Builds the spectator-facing state at any replay timestamp."""

    def __init__(
        self,
        fixture: dict[str, Any],
        events: tuple[dict[str, Any], ...] | list[dict[str, Any]],
        schedule: tuple[ReplayScheduleItem, ...] | list[ReplayScheduleItem],
        replay_mode: ReplayMode,
    ) -> None:
        self.schedule = tuple(schedule)
        self.replay_mode = replay_mode
        self.score_engine = ScoreProgressionEngine(fixture, events)

        # The replay clock represents continuous match time.
        # Keep at least a regulation 90-minute match, while allowing
        # official stoppage-time events (e.g. 92') to extend the clock.
        scene_minutes = tuple(
            item.scene.match_minute
            for item in self.schedule
            if item.scene.match_minute >= 0
        )
        self.match_duration_minutes = max(
            90,
            max(scene_minutes, default=90),
        )

    def state_at(self, elapsed_seconds: float) -> ReplayState:
        if elapsed_seconds < 0:
            raise ValueError("Replay time cannot be negative")

        elapsed_seconds = min(
            float(elapsed_seconds),
            float(self.replay_mode.total_seconds),
        )

        visible: list[ReplayScheduleItem] = []

        for item in self.schedule:
            if item.replay_seconds <= elapsed_seconds:
                visible.append(item)
            else:
                break

        current_scene = visible[-1] if visible else None

        # Continuous match clock:
        # every real match minute has the same replay duration.
        progress = (
            elapsed_seconds / float(self.replay_mode.total_seconds)
            if self.replay_mode.total_seconds > 0
            else 0.0
        )

        match_minute = min(
            self.match_duration_minutes,
            int(progress * self.match_duration_minutes),
        )

        score = self.score_engine.score_at(match_minute)

        return ReplayState(
            replay_mode=self.replay_mode,
            elapsed_seconds=elapsed_seconds,
            match_minute=match_minute,
            current_scene=current_scene,
            visible_scenes=tuple(visible),
            home_score=score.home_score,
            away_score=score.away_score,
        )
