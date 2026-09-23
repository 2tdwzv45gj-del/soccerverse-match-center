from src.commentary_models import Fixture
from src.commentary_presentation import MatchPresentationBuilder


def make_fixture() -> Fixture:
    return Fixture(
        fixture_id=334152,
        home_club_id=2256,
        away_club_id=605,
        home_club_name="Laç",
        away_club_name="Korçë",
        stadium_id=3,
        comp_type=0,
        comp_type_name="National League",
        country_id="ALB",
        league_name="ALB Division 1",
        comp_name="ALB Division 1",
        turn_id=41695,
        datetime="2026-07-18 18:00",
        datetime_utc="2026-07-18 18:00:00 UTC",
        date_formatted="2026-07-18",
        day_of_week="Saturday",
        played=True,
        home_goals=2,
        away_goals=1,
        home_pen_score=0,
        away_pen_score=0,
        penalties=False,
        attendance=1119,
    )


def test_match_presentation_uses_fixture_data():
    presentation = MatchPresentationBuilder().build(make_fixture())

    assert presentation.fixture_id == 334152
    assert presentation.home.club_id == 2256
    assert presentation.away.club_id == 605
    assert presentation.home.name == "Laç"
    assert presentation.away.name == "Korçë"
    assert presentation.home_goals == 2
    assert presentation.away_goals == 1


def test_club_assets_are_resolved():
    presentation = MatchPresentationBuilder().build(make_fixture())

    assert presentation.home.logo_url is not None
    assert presentation.away.logo_url is not None
    assert presentation.home.colors is not None
    assert presentation.away.colors is not None


def test_stadium_asset_is_resolved():
    presentation = MatchPresentationBuilder().build(make_fixture())

    assert presentation.stadium_image_url is not None


def test_competition_name_is_preserved():
    presentation = MatchPresentationBuilder().build(make_fixture())

    assert presentation.competition.name == "ALB Division 1"


def test_competition_image_is_conservatively_unresolved():
    presentation = MatchPresentationBuilder().build(make_fixture())

    assert presentation.competition.image_url is None
