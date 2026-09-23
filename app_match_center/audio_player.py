from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class MatchAudioPlayer:
    """Minimal event-based audio player for the Match Center."""

    def __init__(self, base_dir: str | Path = "assets/audio") -> None:
        self.base_dir = Path(base_dir)

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self._last_event_key: str | None = None

    def _play(
        self,
        filename: str,
        event_key: str,
        volume: float = 1.0,
    ) -> None:
        if event_key == self._last_event_key:
            return

        path = self.base_dir / filename
        if not path.exists():
            return

        self._last_event_key = event_key
        self.player.stop()
        self.audio_output.setVolume(max(0.0, min(1.0, volume)))
        self.player.setSource(
            QUrl.fromLocalFile(str(path.resolve()))
        )
        self.player.play()

    def start_whistle(self) -> None:
        # Match start: one short whistle.
        self._play("match_start.wav", "start", 1.0)

    def goal(self, event_id: int, intensity: float = 0.75) -> None:
        self._play("goal.wav", f"goal:{event_id}", intensity)

    def red_card(
        self,
        event_id: int,
        intensity: float = 0.85,
    ) -> None:
        self._play("red_card.wav", f"red:{event_id}", intensity)

    def substitution(
        self,
        event_id: int,
        intensity: float = 0.55,
    ) -> None:
        self._play(
            "substitution.wav",
            f"sub:{event_id}",
            intensity,
        )

    def final_whistle(self) -> None:
        if self._last_event_key == "final":
            return

        path = self.base_dir / "match_start.wav"
        if not path.exists():
            return

        self._last_event_key = "final"

        def play_whistle() -> None:
            self.player.stop()
            self.audio_output.setVolume(1.0)
            self.player.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self.player.play()

        # Final whistle: three short, separate whistles.
        play_whistle()
        QTimer.singleShot(850, play_whistle)
        QTimer.singleShot(1700, play_whistle)

    def reset(self) -> None:
        self.player.stop()
        self._last_event_key = None
        self.audio_output.setVolume(1.0)
