from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .commentary_models import Fixture
from .datapack_resolver import DatapackResolver


@dataclass(frozen=True)
class ClubPresentation:
    club_id: int
    name: str
    logo_url: Optional[str]
    colors: Optional[tuple[int, int, int]]


@dataclass(frozen=True)
class CompetitionPresentation:
    name: Optional[str]
    image_url: Optional[str]


@dataclass(frozen=True)
class MatchPresentation:
    fixture_id: int
    home: ClubPresentation
    away: ClubPresentation
    stadium_image_url: Optional[str]
    competition: CompetitionPresentation
    home_goals: Optional[int]
    away_goals: Optional[int]


class MatchPresentationBuilder:
    def __init__(self, resolver: DatapackResolver | None = None) -> None:
        self.resolver = resolver or DatapackResolver()

    def build(self, fixture: Fixture) -> MatchPresentation:
        home = self.resolver.get_club(fixture.home_club_id)
        away = self.resolver.get_club(fixture.away_club_id)

        home_logo = self.resolver.get_club_logo(fixture.home_club_id)
        away_logo = self.resolver.get_club_logo(fixture.away_club_id)

        home_colors = self.resolver.get_club_colors(fixture.home_club_id)
        away_colors = self.resolver.get_club_colors(fixture.away_club_id)

        stadium_image = None
        if fixture.stadium_id is not None:
            stadium_image = self.resolver.get_stadium_image(
                fixture.stadium_id
            )

        competition_name = fixture.comp_name or fixture.league_name
        competition_image = None

        # League/cup IDs are not yet proven to be identical to comp IDs
        # across every fixture type. Therefore we only resolve an image
        # when the fixture explicitly identifies a matching league/cup
        # record in a future adapter.
        #
        # For now the name is safely exposed, while the image remains None.
        competition = CompetitionPresentation(
            name=competition_name,
            image_url=competition_image,
        )

        return MatchPresentation(
            fixture_id=fixture.fixture_id,
            home=ClubPresentation(
                club_id=fixture.home_club_id,
                name=fixture.home_club_name,
                logo_url=home_logo,
                colors=home_colors,
            ),
            away=ClubPresentation(
                club_id=fixture.away_club_id,
                name=fixture.away_club_name,
                logo_url=away_logo,
                colors=away_colors,
            ),
            stadium_image_url=stadium_image,
            competition=competition,
            home_goals=fixture.home_goals,
            away_goals=fixture.away_goals,
        )
