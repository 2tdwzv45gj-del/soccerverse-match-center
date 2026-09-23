from src.commentary_actions import group_commentary_actions
from src.commentary_events import CommentarySubEvent
from src.commentary_interpretation import (
    ActionKind,
    interpret_action,
    interpret_actions,
)


def make_event(
    sub_id: int,
    event_id: int,
    minute: int,
    category: str,
    player_one_id: int = 10,
    player_two_id: int | None = 20,
) -> CommentarySubEvent:
    return CommentarySubEvent(
        comm_sub_event_id=sub_id,
        comm_event_id=event_id,
        category=category,
        time=minute,
        player_one_id=player_one_id,
        player_two_id=player_two_id,
        club_one_id=30,
        player_one_name="Player A",
        player_two_name="Player B" if player_two_id else None,
        club_one_name="Club",
    )


def make_action(*categories: str):
    events = [
        make_event(i + 1, 100, 5, category)
        for i, category in enumerate(categories)
    ]
    return group_commentary_actions(events)[0]


def test_goal_is_goal():
    result = interpret_action(make_action("GOAL"))

    assert result.kind == ActionKind.GOAL


def test_assisted_chance_is_chance():
    result = interpret_action(make_action("ASSISTEDCHANCE"))

    assert result.kind == ActionKind.CHANCE


def test_shot_is_shot():
    result = interpret_action(make_action("SHOT"))

    assert result.kind == ActionKind.SHOT


def test_save_is_save():
    result = interpret_action(make_action("SAVE"))

    assert result.kind == ActionKind.SAVE


def test_offtarget_is_offtarget():
    result = interpret_action(make_action("OFFTARGET"))

    assert result.kind == ActionKind.OFFTARGET


def test_tackle_is_tackle():
    result = interpret_action(make_action("TACKLE"))

    assert result.kind == ActionKind.TACKLE


def test_sub_is_substitution():
    result = interpret_action(make_action("SUB"))

    assert result.kind == ActionKind.SUBSTITUTION


def test_goal_takes_precedence():
    result = interpret_action(
        make_action("ASSISTEDCHANCE", "SHOT", "GOAL")
    )

    assert result.kind == ActionKind.GOAL


def test_unknown_category_is_other():
    result = interpret_action(make_action("UNKNOWN_CATEGORY"))

    assert result.kind == ActionKind.OTHER


def test_players_are_preserved():
    result = interpret_action(make_action("ASSISTEDCHANCE"))

    assert result.primary_player_id == 10
    assert result.secondary_player_id == 20


def test_multiple_actions_are_interpreted():
    actions = group_commentary_actions(
        [
            make_event(1, 100, 5, "CHANCE"),
            make_event(2, 200, 12, "SHOT"),
        ]
    )

    results = interpret_actions(actions)

    assert [result.kind for result in results] == [
        ActionKind.CHANCE,
        ActionKind.SHOT,
    ]
