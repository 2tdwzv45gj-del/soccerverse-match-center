from src.datapack_resolver import DatapackResolver


def test_pack_loads():
    resolver = DatapackResolver()
    assert resolver.get_club("33")["n"] == "Manchester United"
    assert resolver.get_club_colors("33") == (217, 2, 13)


def test_club_asset_resolution():
    resolver = DatapackResolver()
    assert resolver.get_club_logo("33").endswith("/33.png")


def test_stadium_asset_resolution():
    resolver = DatapackResolver()
    stadium = resolver.get_stadium("1")
    assert stadium["n"] == "Stadiumi Gjirokastra"
    assert resolver.get_stadium_image("1").endswith("/1.png")


def test_league_asset_resolution():
    resolver = DatapackResolver()
    league = resolver.get_league("1")
    assert league["n"] == "Kategoria Superiore"
    assert resolver.get_league_image("1").endswith("/ALB1.png")


def test_cup_asset_resolution():
    resolver = DatapackResolver()
    cup = resolver.get_cup("AFR")
    assert cup["n"] == "CAF Champions League"
    assert resolver.get_cup_image("AFR").endswith("/AFR.png")


def test_missing_ids_are_safe():
    resolver = DatapackResolver()
    assert resolver.get_club("999999999") is None
    assert resolver.get_club_logo("999999999") is None
    assert resolver.get_stadium("999999999") is None
    assert resolver.get_league("999999999") is None
    assert resolver.get_cup("__missing__") is None
