from src.commentary_actions import group_commentary_actions
from src.commentary_events import CommentarySubEvent
from src.commentary_interpretation import interpret_action
from src.commentary_narrative import (
    generate_narrative,
    generate_narratives,
)


def make_event(
    sub_id: int,
    category: str,
    player_one_id: int = 10,
    player_two_id: int | None = None,
) -> CommentarySubEvent:
    return CommentarySubEvent(
        comm_sub_event_id=sub_id,
        comm_event_id=100,
        category=category,
        time=5,
        player_one_id=player_one_id,
        player_two_id=player_two_id,
        club_one_id=30,
        player_one_name="Player A",
        player_two_name="Player B" if player_two_id else None,
        club_one_name="Club",
    )


def make_action(category: str, player_two_id: int | None = None):
    events = [make_event(1, category, player_two_id=player_two_id)]
    action = group_commentary_actions(events)[0]
    return interpret_action(action)


def test_goal_narrative():
    narrative = generate_narrative(make_action("GOAL"))

    assert narrative.minute == 5
    assert narrative.text == "⚽ Gol di Player A."
    assert narrative.source_action_id == 100


def test_save_narrative():
    narrative = generate_narrative(make_action("SAVE"))

    assert narrative.text == "🧤 Parata di Player A."


def test_shot_narrative():
    narrative = generate_narrative(make_action("SHOT"))

    assert narrative.text == "🎯 Conclusione di Player A."


def test_offtarget_narrative():
    narrative = generate_narrative(make_action("OFFTARGET"))

    assert narrative.text == "Conclusione di Player A fuori bersaglio."


def test_tackle_narrative():
    narrative = generate_narrative(make_action("TACKLE"))

    assert narrative.text == "Contrasto di Player A."


def test_chance_with_second_player():
    narrative = generate_narrative(
        make_action("ASSISTEDCHANCE", player_two_id=20)
    )

    assert narrative.text == "Occasione: Player A serve Player B."


def test_chance_without_second_player():
    narrative = generate_narrative(make_action("CHANCE"))

    assert narrative.text == "Occasione per Player A."


def test_substitution_without_second_player():
    narrative = generate_narrative(make_action("SUB"))

    assert narrative.text == "Sostituzione."


def test_unknown_action():
    narrative = generate_narrative(make_action("UNKNOWN"))

    assert narrative.text == "Azione al 5° minuto."


def test_generate_multiple_narratives():
    first = interpret_action(
        group_commentary_actions([make_event(1, "GOAL")])[0]
    )
    second_event = CommentarySubEvent(
        comm_sub_event_id=2,
        comm_event_id=200,
        category="SHOT",
        time=12,
        player_one_id=10,
        player_two_id=None,
        club_one_id=30,
        player_one_name="Player A",
        player_two_name=None,
        club_one_name="Club",
    )
    second = interpret_action(
        group_commentary_actions([second_event])[0]
    )

    narratives = generate_narratives((first, second))

    assert len(narratives) == 2
    assert narratives[0].source_action_id == 100
    assert narratives[1].source_action_id == 200
