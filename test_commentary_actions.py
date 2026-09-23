from src.commentary_actions import group_commentary_actions
from src.commentary_events import CommentarySubEvent


def make_event(
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
        player_two_id=20,
        club_one_id=30,
        player_one_name="Player A",
        player_two_name="Player B",
        club_one_name="Club",
    )


def test_sub_events_are_grouped_into_actions():
    events = [
        make_event(3, 100, 5, "SAVE"),
        make_event(1, 100, 5, "ASSISTEDCHANCE"),
        make_event(2, 100, 5, "SHOT"),
    ]

    actions = group_commentary_actions(events)

    assert len(actions) == 1
    assert actions[0].comm_event_id == 100
    assert actions[0].categories == (
        "ASSISTEDCHANCE",
        "SHOT",
        "SAVE",
    )


def test_multiple_actions_are_chronological():
    events = [
        make_event(3, 200, 12, "SHOT"),
        make_event(1, 100, 5, "CHANCE"),
    ]

    actions = group_commentary_actions(events)

    assert [action.comm_event_id for action in actions] == [100, 200]
    assert [action.time for action in actions] == [5, 12]


def test_player_ids_are_unique_and_ordered():
    events = [
        make_event(1, 100, 5, "ASSISTEDCHANCE"),
        make_event(2, 100, 5, "SHOT"),
    ]

    actions = group_commentary_actions(events)

    assert actions[0].player_ids == (10, 20)


def test_empty_input():
    assert group_commentary_actions([]) == ()


def test_action_keeps_original_sub_events():
    events = [
        make_event(1, 100, 5, "CHANCE"),
        make_event(2, 100, 5, "SHOT"),
    ]

    actions = group_commentary_actions(events)

    assert len(actions[0].sub_events) == 2
    assert actions[0].sub_events[0].comm_sub_event_id == 1
