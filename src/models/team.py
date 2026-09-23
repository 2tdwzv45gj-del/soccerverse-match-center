from dataclasses import dataclass
from typing import List


@dataclass
class Player:
    player_id: int
    position_main: str
    positions: List[str]
    rating: int
    rating_gk: int
    rating_tackling: int
    rating_passing: int
    rating_shooting: int
    rating_stamina: int
    rating_aggression: int
    fitness: int
    morale: int
    concerns: int
    form: str
    injured: int
    banned: int
    age: int

    def can_play(self, position: str) -> bool:
        return position in self.positions

    @property
    def is_injured(self) -> bool:
        if not self.injured:
            return False

        # Soccerverse restituisce `injured` come Unix timestamp
        # fino al quale il giocatore è considerato infortunato.
        import time
        return self.injured > int(time.time())

    @property
    def is_banned(self) -> bool:
        return self.banned != 0

    @property
    def is_available(self) -> bool:
        return not self.is_injured and not self.is_banned


@dataclass
class Team:
    club_id: int
    name: str
    players: List[Player]

    @property
    def available_players(self) -> List[Player]:
        return [
            player
            for player in self.players
            if player.is_available
        ]

    @property
    def injured_players(self) -> List[Player]:
        return [
            player
            for player in self.players
            if player.is_injured
        ]

    @property
    def banned_players(self) -> List[Player]:
        return [
            player
            for player in self.players
            if player.is_banned
        ]
