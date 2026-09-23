from src.match_search import MatchSearchResult, MatchSearchService


class FakeMCP:
    def resolve_club_name(self, name):
        return [
            {"id": 3340, "name": "Vora", "confidence": 1.0},
            {"id": 3317, "name": "Vlorë", "confidence": 0.66},
        ]

    def get_club_schedule(self, club_id):
        assert club_id == 3340
        return [
            {
                "fixture_id": 334228,
                "home_club": 3340,
                "away_club": 605,
                "home_club_name": "Vora",
                "away_club_name": "Korçë",
                "home_goals": 1,
                "away_goals": 0,
                "played": 1,
                "datetime": "2026-09-09 18:00",
                "league_name": "ALB Division 1",
                "comp_name": "ALB Division 1",
            },
            {
                "fixture_id": 334245,
                "home_club": 3340,
                "away_club": 3325,
                "home_club_name": "Vora",
                "away_club_name": "Ballsh",
                "home_goals": 0,
                "away_goals": 0,
                "played": 0,
                "datetime": "2026-09-19 18:00",
                "league_name": "ALB Division 1",
                "comp_name": "ALB Division 1",
            },
        ]


def test_search_returns_resolved_club_and_matches():
    service = MatchSearchService(FakeMCP())

    result = service.search("Vora")

    assert result.club_id == 3340
    assert result.club_name == "Vora"
    assert len(result.matches) == 2


def test_match_result_contains_human_friendly_fields():
    service = MatchSearchService(FakeMCP())

    result = service.search("Vora")
    match = result.matches[0]

    assert isinstance(match, MatchSearchResult)
    assert match.fixture_id == 334228
    assert match.home_team == "Vora"
    assert match.away_team == "Korçë"
    assert match.score == "1-0"
    assert match.played is True


def test_search_preserves_upcoming_matches():
    service = MatchSearchService(FakeMCP())

    result = service.search("Vora")

    assert result.matches[1].fixture_id == 334245
    assert result.matches[1].played is False

def test_search_orders_matches_chronologically():
    class FakeMCPUnsorted(FakeMCP):
        def get_club_schedule(self, club_id):
            return [
                {
                    "fixture_id": 2,
                    "home_club": 3340,
                    "away_club": 605,
                    "home_club_name": "Vora",
                    "away_club_name": "Korçë",
                    "home_goals": 1,
                    "away_goals": 0,
                    "played": 1,
                    "datetime": "2026-09-09 18:00",
                    "comp_name": "ALB Division 1",
                },
                {
                    "fixture_id": 1,
                    "home_club": 3340,
                    "away_club": 3325,
                    "home_club_name": "Vora",
                    "away_club_name": "Ballsh",
                    "home_goals": 0,
                    "away_goals": 0,
                    "played": 0,
                    "datetime": "2026-09-19 18:00",
                    "comp_name": "ALB Division 1",
                },
            ]

    result = MatchSearchService(FakeMCPUnsorted()).search("Vora")

    assert [m.fixture_id for m in result.matches] == [2, 1]


def test_search_rejects_empty_team_name():
    service = MatchSearchService(FakeMCP())

    try:
        service.search("   ")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_match_result_exposes_competition():
    result = MatchSearchService(FakeMCP()).search("Vora")

    assert result.matches[0].competition == "ALB Division 1"
