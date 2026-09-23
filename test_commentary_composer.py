from src.commentary_actions import CommentaryAction
from src.commentary_composer import NarrativeIntent, compose_action, compose_actions
from src.commentary_events import CommentarySubEvent


def se(
    sub_id,
    event_id,
    category,
    time,
    p1=None,
    p2=None,
    club_id=10,
    club_name="Club",
):
    return CommentarySubEvent(
        comm_sub_event_id=sub_id,
        comm_event_id=event_id,
        category=category,
        time=time,
        player_one_id=None,
        player_two_id=None,
        club_one_id=club_id,
        player_one_name=p1,
        player_two_name=p2,
        club_one_name=club_name,
    )


def action(*events, event_id=100, time=5):
    return CommentaryAction(
        comm_event_id=event_id,
        time=time,
        club_one_id=10,
        club_one_name="Club",
        sub_events=tuple(events),
    )


def test_saved_chance():
    result = compose_action(
        action(
            se(1, 100, "ASSISTEDCHANCE", 5, "Assistente", "Tiratore"),
            se(2, 100, "SHOT", 5, "Tiratore"),
            se(3, 100, "SAVE", 5, "Portiere"),
        )
    )

    assert result.kind == "chance_saved"
    assert result.creator_player == "Assistente"
    assert result.shooter_player == "Tiratore"
    assert result.defender_player is None
    assert result.goalkeeper == "Portiere"


def test_offtarget_chance():
    result = compose_action(
        action(
            se(1, 100, "ASSISTEDCHANCE", 5, "Assistente", "Tiratore"),
            se(2, 100, "SHOT", 5, "Tiratore"),
            se(3, 100, "OFFTARGET", 5, "Tiratore"),
        )
    )

    assert result.kind == "chance_offtarget"
    assert result.creator_player == "Assistente"
    assert result.shooter_player == "Tiratore"
    assert result.goalkeeper is None


def test_goal():
    result = compose_action(
        action(
            se(1, 100, "CHANCE", 5, "Marcatore"),
            se(2, 100, "SHOT", 5, "Marcatore"),
            se(3, 100, "GOAL", 5, "Marcatore"),
        )
    )

    assert result.kind == "goal"
    assert result.creator_player == "Marcatore"
    assert result.shooter_player == "Marcatore"


def test_tackle():
    result = compose_action(
        action(
            se(1, 100, "ASSISTEDCHANCE", 5, "Assistente", "Attaccante"),
            se(2, 100, "TACKLE", 5, "Difensore"),
        )
    )

    assert result.kind == "chance_tackled"
    assert result.creator_player == "Assistente"
    assert result.shooter_player == "Attaccante"
    assert result.defender_player == "Difensore"


def test_substitution():
    result = compose_action(
        action(
            se(1, 100, "SUB", 60, "Player In", "Player Out"),
            event_id=200,
            time=60,
        )
    )

    assert result.kind == "substitution"
    assert result.substitute_on == "Player In"
    assert result.substitute_off == "Player Out"
    assert result.creator_player is None
    assert result.shooter_player is None


def test_actions_preserve_order():
    actions = (
        action(
            se(1, 100, "SHOT", 5, "Primo"),
            event_id=100,
            time=5,
        ),
        action(
            se(2, 200, "SHOT", 10, "Secondo"),
            event_id=200,
            time=10,
        ),
    )

    results = compose_actions(actions)

    assert [r.minute for r in results] == [5, 10]
    assert [r.shooter_player for r in results] == ["Primo", "Secondo"]
