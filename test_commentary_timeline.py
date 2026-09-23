from src.commentary_events import CommentarySubEvent, MatchEvent
from src.commentary_timeline import CommentaryTimeline


def make_match_event(event_id: int, minute: int) -> MatchEvent:
    return MatchEvent(
        match_event_id=event_id,
        event_type="GOAL",
        player_id=10,
        club_id=20,
        time=minute,
        goal_type="OPEN_PLAY",
        season_id=4,
        player_name="Player",
        club_name="Club",
        time_minutes=f"{minute}'",
        time_display=f"{minute} minutes",
    )


def make_commentary(
    sub_id: int,
    event_id: int,
    minute: int,
    category: str,
) -> CommentarySubEvent:
    return CommentarySubEvent(
        comm_sub_event_id=sub_id,
        comm_event_id=event_id,
        category=category,
        time=minute,
        player_one_id=10,
        player_two_id=None,
        club_one_id=20,
        player_one_name="Player",
        player_two_name=None,
        club_one_name="Club",
    )


def test_timeline_is_chronological():
    timeline = CommentaryTimeline(
        match_events=[
            make_match_event(3, 76),
            make_match_event(1, 5),
        ],
        commentary_events=[
            make_commentary(2, 100, 12, "SHOT"),
            make_commentary(1, 99, 5, "CHANCE"),
        ],
    )

    minutes = timeline.minutes()

    assert [item.minute for item in minutes] == [5, 12, 76]


def test_events_are_grouped_by_minute():
    timeline = CommentaryTimeline(
        match_events=[make_match_event(1, 5)],
        commentary_events=[
            make_commentary(2, 100, 5, "SHOT"),
            make_commentary(1, 99, 5, "CHANCE"),
        ],
    )

    item = timeline.minute(5)

    assert item is not None
    assert len(item.match_events) == 1
    assert len(item.commentary_events) == 2
    assert [event.comm_sub_event_id for event in item.commentary_events] == [1, 2]


def test_missing_minute_returns_none():
    timeline = CommentaryTimeline(
        match_events=[make_match_event(1, 5)]
    )

    assert timeline.minute(6) is None


def test_range_is_inclusive():
    timeline = CommentaryTimeline(
        match_events=[
            make_match_event(1, 5),
            make_match_event(2, 12),
            make_match_event(3, 20),
        ]
    )

    items = timeline.minutes_in_range(5, 12)

    assert [item.minute for item in items] == [5, 12]


def test_empty_timeline():
    timeline = CommentaryTimeline()

    assert timeline.minutes() == ()
