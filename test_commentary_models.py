import json
from pathlib import Path

from src.commentary_models import Fixture


def test_fixture_model_from_real_data():
    data = json.loads(
        Path("data/raw/club_605_formation_history.json").read_text()
    )

    fixture = Fixture.from_dict(data[0]["fixture"])

    assert fixture.fixture_id == 334152
    assert fixture.home_club_id == 2256
    assert fixture.away_club_id == 605
    assert fixture.home_club_name == "Laç"
    assert fixture.away_club_name == "Korçë"
    assert fixture.stadium_id == 3
    assert fixture.comp_name == "ALB Division 1"
    assert fixture.league_name == "ALB Division 1"
    assert fixture.home_goals == 2
    assert fixture.away_goals == 1
    assert fixture.played is True
