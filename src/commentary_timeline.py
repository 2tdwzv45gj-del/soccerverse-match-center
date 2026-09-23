from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from .commentary_events import CommentarySubEvent, MatchEvent


@dataclass(frozen=True)
class TimelineMinute:
    minute: int
    match_events: tuple[MatchEvent, ...]
    commentary_events: tuple[CommentarySubEvent, ...]


class CommentaryTimeline:
    """
    Normalized chronological view of official match data.

    No narrative is generated here.
    The original event records remain intact.
    """

    def __init__(
        self,
        match_events: Iterable[MatchEvent] = (),
        commentary_events: Iterable[CommentarySubEvent] = (),
    ) -> None:
        self._match_events = tuple(match_events)
        self._commentary_events = tuple(commentary_events)

    def minutes(self) -> tuple[TimelineMinute, ...]:
        match_by_minute: dict[int, list[MatchEvent]] = defaultdict(list)
        commentary_by_minute: dict[int, list[CommentarySubEvent]] = defaultdict(list)

        for event in self._match_events:
            match_by_minute[event.time].append(event)

        for event in self._commentary_events:
            commentary_by_minute[event.time].append(event)

        all_minutes = sorted(
            set(match_by_minute) | set(commentary_by_minute)
        )

        return tuple(
            TimelineMinute(
                minute=minute,
                match_events=tuple(
                    sorted(
                        match_by_minute[minute],
                        key=lambda event: event.match_event_id,
                    )
                ),
                commentary_events=tuple(
                    sorted(
                        commentary_by_minute[minute],
                        key=lambda event: (
                            event.comm_event_id,
                            event.comm_sub_event_id,
                        ),
                    )
                ),
            )
            for minute in all_minutes
        )

    def minute(self, minute: int) -> TimelineMinute | None:
        for item in self.minutes():
            if item.minute == minute:
                return item
        return None

    def minutes_in_range(
        self,
        start: int,
        end: int,
    ) -> tuple[TimelineMinute, ...]:
        return tuple(
            item
            for item in self.minutes()
            if start <= item.minute <= end
        )
