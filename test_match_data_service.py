from src.match_data_service import MatchData, MatchDataService


class FakeMCP:
    def get_fixture(self, fixture_id):
        assert fixture_id == 334228
        return {
            "fixture_id": 334228,
            "home_club": 3340,
            "away_club": 605,
            "home_club_name": "Vora",
            "away_club_name": "Korçë",
            "home_goals": 1,
            "away_goals": 0,
        }

    def get_match_events(self, fixture_id):
        assert fixture_id == 334228
        return [
            {"match_event_id": 114831229, "event_type": "GOAL", "time": 76}
        ]

    def get_match_commentary(self, fixture_id):
        assert fixture_id == 334228
        return {
            "fixture_id": 334228,
            "commentary": [
                {"comm_sub_event_id": 1, "category": "CHANCE", "time": 76},
                {"comm_sub_event_id": 2, "category": "SHOT", "time": 76},
            ],
            "count": 2,
            "total": 2,
        }

    def get_match_subs(self, fixture_id):
        assert fixture_id == 334228
        return [
            {"club_id": 3340, "player_on_name": "Segerso Geci", "time": 60}
        ]


def test_load_returns_complete_match_data():
    data = MatchDataService(FakeMCP()).load(334228)

    assert isinstance(data, MatchData)
    assert data.fixture_id == 334228
    assert data.fixture["home_club_name"] == "Vora"
    assert len(data.events) == 1
    assert len(data.commentary) == 2
    assert len(data.substitutions) == 1


def test_load_normalizes_commentary_wrapper():
    data = MatchDataService(FakeMCP()).load(334228)

    assert data.commentary[0]["category"] == "CHANCE"
    assert data.commentary[1]["category"] == "SHOT"


def test_load_preserves_official_data_without_transformation():
    data = MatchDataService(FakeMCP()).load(334228)

    assert data.events[0]["event_type"] == "GOAL"
    assert data.events[0]["time"] == 76
    assert data.substitutions[0]["player_on_name"] == "Segerso Geci"


def test_load_rejects_invalid_fixture_id():
    try:
        MatchDataService(FakeMCP()).load(0)
    except ValueError as exc:
        assert str(exc) == "Fixture ID must be positive"
    else:
        raise AssertionError("Expected ValueError")
