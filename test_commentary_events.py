from src.commentary_events import MatchEvent, CommentarySubEvent


def test_match_event_from_verified_mcp_shape():
    data = {
        "match_event_id": 114831229,
        "event_type": "GOAL",
        "player_id": 298011,
        "club_id": 3340,
        "time": 76,
        "goal_type": "OPEN_PLAY",
        "season_id": 4,
        "player_name": "Segerso Geci",
        "club_name": "Vora",
        "time_minutes": "76'",
        "time_display": "76 minutes",
    }

    event = MatchEvent.from_dict(data)

    assert event.match_event_id == 114831229
    assert event.event_type == "GOAL"
    assert event.player_id == 298011
    assert event.club_id == 3340
    assert event.time == 76
    assert event.goal_type == "OPEN_PLAY"
    assert event.player_name == "Segerso Geci"


def test_commentary_sub_event_from_verified_mcp_shape():
    data = {
        "comm_sub_event_id": 123,
        "comm_event_id": 456,
        "category": "ASSISTEDCHANCE",
        "time": 5,
        "player_one_id": 111,
        "player_two_id": 222,
        "club_one_id": 333,
        "player_one_name": "Player A",
        "player_two_name": "Player B",
        "club_one_name": "Club",
    }

    event = CommentarySubEvent.from_dict(data)

    assert event.comm_sub_event_id == 123
    assert event.comm_event_id == 456
    assert event.category == "ASSISTEDCHANCE"
    assert event.time == 5
    assert event.player_one_name == "Player A"
    assert event.player_two_name == "Player B"


def test_optional_fields():
    data = {
        "match_event_id": 1,
        "event_type": "GOAL",
        "player_id": None,
        "club_id": None,
        "time": 90,
        "goal_type": None,
        "season_id": None,
        "player_name": None,
        "club_name": None,
        "time_minutes": None,
        "time_display": None,
    }

    event = MatchEvent.from_dict(data)

    assert event.player_id is None
    assert event.goal_type is None


def test_real_commentary_sub_event_without_club():
    data = {
        "comm_sub_event_id": 114830947,
        "category": "TACKLE",
        "player_one_id": 3789,
        "comm_event_id": 114830945,
        "time": 2,
        "player_one_name": "Jurgen Vrapi",
        "time_minutes": "2'",
    }

    event = CommentarySubEvent.from_dict(data)

    assert event.category == "TACKLE"
    assert event.player_one_id == 3789
    assert event.player_two_id is None
    assert event.club_one_id is None
    assert event.player_one_name == "Jurgen Vrapi"
