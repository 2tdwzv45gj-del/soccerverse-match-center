from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchAudioEvent:
    kind: str


class MatchAudioEngine:
    """Minimal audio policy for the Match Center.

    Crowd size and home/away are intentionally ignored.
    Audio is used only as a discreet event cue.
    """

    _INTENSITIES = {
        "start_whistle": 1.0,
        "goal": 0.75,
        "red_card": 0.85,
        "substitution": 0.55,
        "final_whistle": 1.0,
    }

    def __init__(
        self,
        attendance: int = 0,
        home_club_id: int | None = None,
        away_club_id: int | None = None,
    ) -> None:
        # Kept for backward compatibility with the current GUI.
        self.attendance = attendance
        self.home_club_id = home_club_id
        self.away_club_id = away_club_id

    def intensity(self, kind: str) -> float:
        return self._INTENSITIES.get(kind, 0.0)

    def goal_intensity(self, is_home: bool) -> float:
        return self.intensity("goal")

    def red_card_intensity(self) -> float:
        return self.intensity("red_card")

    def substitution_intensity(self) -> float:
        return self.intensity("substitution")

    def start_whistle_intensity(self) -> float:
        return self.intensity("start_whistle")

    def final_whistle_intensity(self) -> float:
        return self.intensity("final_whistle")

    def resolve(self, event: MatchAudioEvent) -> float:
        return self.intensity(event.kind)
