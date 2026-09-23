from src.commentary_replay import (
    ReplayMode,
    ReplayScene,
    ReplayScheduleItem,
)
from src.replay_state import ReplayState, ReplayStateEngine


FIXTURE = {
    "fixture_id": 334228,
    "home_club": 3340,
    "away_club": 605,
    "home_club_name": "Vora",
    "away_club_name": "Korçë",
}


def scene(action_id, minute, kind):
    return ReplayScheduleItem(
        scene=ReplayScene(
            action_id=action_id,
            match_minute=minute,
            kind=kind,
        ),
        replay_seconds=float(action_id),
    )


def test_before_first_scene_has_zero_score():
    schedule = [
        scene(10, 20, "chance"),
        scene(20, 76, "goal"),
    ]

    events = [
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 76,
        }
    ]

    engine = ReplayStateEngine(
        FIXTURE,
        events,
        schedule,
        ReplayMode.M3,
    )

    state = engine.state_at(5)

    assert isinstance(state, ReplayState)
    assert state.current_scene is None
    assert state.visible_scenes == ()
    assert state.match_minute == 0
    assert state.home_score == 0
    assert state.away_score == 0


def test_score_changes_when_goal_scene_is_revealed():
    schedule = [
        scene(10, 20, "chance"),
        scene(20, 76, "goal"),
    ]

    events = [
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 76,
        }
    ]

    engine = ReplayStateEngine(
        FIXTURE,
        events,
        schedule,
        ReplayMode.M3,
    )

    before = engine.state_at(15)
    after = engine.state_at(20)

    assert before.match_minute == 20
    assert before.home_score == 0
    assert before.away_score == 0

    assert after.match_minute == 76
    assert after.home_score == 1
    assert after.away_score == 0


def test_visible_scenes_grow_monotonically():
    schedule = [
        scene(10, 20, "chance"),
        scene(20, 76, "goal"),
        scene(30, 84, "chance_saved"),
    ]

    engine = ReplayStateEngine(
        FIXTURE,
        [],
        schedule,
        ReplayMode.M6,
    )

    state_1 = engine.state_at(10)
    state_2 = engine.state_at(20)
    state_3 = engine.state_at(30)

    assert len(state_1.visible_scenes) == 1
    assert len(state_2.visible_scenes) == 2
    assert len(state_3.visible_scenes) == 3


def test_current_scene_is_latest_revealed_scene():
    schedule = [
        scene(10, 20, "chance"),
        scene(20, 76, "goal"),
    ]

    engine = ReplayStateEngine(
        FIXTURE,
        [],
        schedule,
        ReplayMode.M12,
    )

    state = engine.state_at(20)

    assert state.current_scene is schedule[1]


def test_negative_replay_time_is_rejected():
    engine = ReplayStateEngine(
        FIXTURE,
        [],
        [],
        ReplayMode.M3,
    )

    try:
        engine.state_at(-1)
    except ValueError as exc:
        assert str(exc) == "Replay time cannot be negative"
    else:
        raise AssertionError("Expected ValueError")
