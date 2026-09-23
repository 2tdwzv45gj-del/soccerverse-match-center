import pytest

from src.commentary_parser import parse_match_commentary_response


def make_row(
    sub_id: int,
    event_id: int,
    minute: int,
    category: str,
):
    return {
        "comm_sub_event_id": sub_id,
        "category": category,
        "player_one_id": 10,
        "player_two_id": 20,
        "club_one_id": 30,
        "comm_event_id": event_id,
        "time": minute,
        "player_one_name": "Player A",
        "player_two_name": "Player B",
        "club_one_name": "Club",
        "time_minutes": f"{minute}'",
    }


def test_parse_commentary_envelope():
    response = {
        "fixture_id": 334228,
        "season_id": 4,
        "commentary": [
            make_row(1, 100, 2, "ASSISTEDCHANCE"),
            make_row(2, 100, 2, "TACKLE"),
        ],
        "count": 2,
        "total": 2,
    }

    result = parse_match_commentary_response(response)

    assert len(result) == 2
    assert result[0].category == "ASSISTEDCHANCE"
    assert result[1].category == "TACKLE"


def test_empty_commentary_is_valid():
    response = {
        "fixture_id": 334228,
        "season_id": 4,
        "commentary": [],
        "count": 0,
        "total": 0,
    }

    assert parse_match_commentary_response(response) == ()


def test_missing_commentary_field():
    with pytest.raises(ValueError, match="commentary"):
        parse_match_commentary_response({
            "fixture_id": 334228,
            "season_id": 4,
        })


def test_invalid_commentary_type():
    with pytest.raises(TypeError, match="commentary"):
        parse_match_commentary_response({
            "fixture_id": 334228,
            "season_id": 4,
            "commentary": {},
        })


def test_invalid_response_type():
    with pytest.raises(TypeError):
        parse_match_commentary_response([])


def test_real_optional_fields_are_supported():
    response = {
        "fixture_id": 334228,
        "season_id": 4,
        "commentary": [
            {
                "comm_sub_event_id": 114830947,
                "category": "TACKLE",
                "player_one_id": 3789,
                "comm_event_id": 114830945,
                "time": 2,
                "player_one_name": "Jurgen Vrapi",
                "time_minutes": "2'",
            }
        ],
        "count": 1,
        "total": 1,
    }

    result = parse_match_commentary_response(response)

    assert len(result) == 1
    assert result[0].club_one_id is None
    assert result[0].player_two_id is None
