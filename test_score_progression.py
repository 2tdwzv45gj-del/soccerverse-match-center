from src.score_progression import ScoreProgressionEngine, ScoreSnapshot


FIXTURE = {
    "fixture_id": 334228,
    "home_club": 3340,
    "away_club": 605,
    "home_club_name": "Vora",
    "away_club_name": "Korçë",
}


def test_score_progression_starts_zero_zero():
    engine = ScoreProgressionEngine(FIXTURE, [])

    assert engine.score_at(1) == ScoreSnapshot(1, 0, 0)


def test_home_goal_updates_score():
    events = [
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 76,
        }
    ]

    engine = ScoreProgressionEngine(FIXTURE, events)

    assert engine.score_at(75) == ScoreSnapshot(75, 0, 0)
    assert engine.score_at(76) == ScoreSnapshot(76, 1, 0)
    assert engine.score_at(90) == ScoreSnapshot(90, 1, 0)


def test_away_goal_updates_score():
    events = [
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 605,
            "time": 12,
        }
    ]

    engine = ScoreProgressionEngine(FIXTURE, events)

    assert engine.score_at(11) == ScoreSnapshot(11, 0, 0)
    assert engine.score_at(12) == ScoreSnapshot(12, 0, 1)


def test_multiple_goals_are_ordered_by_match_minute():
    events = [
        {
            "match_event_id": 3,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 76,
        },
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 605,
            "time": 20,
        },
        {
            "match_event_id": 2,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 45,
        },
    ]

    engine = ScoreProgressionEngine(FIXTURE, events)

    assert engine.snapshots() == (
        ScoreSnapshot(20, 0, 1),
        ScoreSnapshot(45, 1, 1),
        ScoreSnapshot(76, 2, 1),
    )


def test_non_goal_events_do_not_change_score():
    events = [
        {
            "match_event_id": 1,
            "event_type": "SHOT",
            "club_id": 3340,
            "time": 30,
        },
        {
            "match_event_id": 2,
            "event_type": "GOAL",
            "club_id": 3340,
            "time": 76,
        },
    ]

    engine = ScoreProgressionEngine(FIXTURE, events)

    assert engine.score_at(60) == ScoreSnapshot(60, 0, 0)
    assert engine.score_at(76) == ScoreSnapshot(76, 1, 0)


def test_unknown_goal_club_is_rejected():
    events = [
        {
            "match_event_id": 1,
            "event_type": "GOAL",
            "club_id": 999999,
            "time": 10,
        }
    ]

    engine = ScoreProgressionEngine(FIXTURE, events)

    try:
        engine.snapshots()
    except ValueError as exc:
        assert "unknown club" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
