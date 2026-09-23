from __future__ import annotations

from dataclasses import dataclass

from .commentary_events import CommentarySubEvent


@dataclass(frozen=True)
class CommentaryAction:
    comm_event_id: int
    time: int
    club_one_id: int | None
    club_one_name: str | None
    sub_events: tuple[CommentarySubEvent, ...]

    @property
    def categories(self) -> tuple[str, ...]:
        return tuple(event.category for event in self.sub_events)

    @property
    def player_ids(self) -> tuple[int, ...]:
        ids: list[int] = []

        for event in self.sub_events:
            if event.player_one_id is not None:
                ids.append(event.player_one_id)
            if event.player_two_id is not None:
                ids.append(event.player_two_id)

        return tuple(dict.fromkeys(ids))


def group_commentary_actions(
    events: list[CommentarySubEvent] | tuple[CommentarySubEvent, ...],
) -> tuple[CommentaryAction, ...]:
    groups: dict[int, list[CommentarySubEvent]] = {}

    for event in events:
        groups.setdefault(event.comm_event_id, []).append(event)

    actions: list[CommentaryAction] = []

    for comm_event_id, sub_events in groups.items():
        ordered = tuple(
            sorted(
                sub_events,
                key=lambda event: event.comm_sub_event_id,
            )
        )

        first = ordered[0]

        actions.append(
            CommentaryAction(
                comm_event_id=comm_event_id,
                time=first.time,
                club_one_id=first.club_one_id,
                club_one_name=first.club_one_name,
                sub_events=ordered,
            )
        )

    return tuple(
        sorted(
            actions,
            key=lambda action: (action.time, action.comm_event_id),
        )
    )
