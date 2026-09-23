from typing import List

from src.models.team import Player, Team


def create_player(data: dict | Player) -> Player:
    if isinstance(data, Player):
        return data

    return Player(
        player_id=data["player_id"],
        position_main=data["position_main"],
        positions=data.get("positions", []),
        rating=data.get("rating", 0),
        rating_gk=data.get("rating_gk", 0),
        rating_tackling=data.get("rating_tackling", 0),
        rating_passing=data.get("rating_passing", 0),
        rating_shooting=data.get("rating_shooting", 0),
        rating_stamina=data.get("rating_stamina", 0),
        rating_aggression=data.get("rating_aggression", 0),
        fitness=data.get("fitness", 0),
        morale=data.get("morale", 0),
        concerns=data.get("concerns", 0),
        form=data.get("form", ""),
        injured=data.get("injured", 0),
        banned=data.get("banned", 0),
        age=data.get("age", 0),
    )


def create_team(
    club_id: int,
    name: str,
    players_data: List[dict]
) -> Team:

    players = [
        create_player(player)
        for player in players_data
    ]

    return Team(
        club_id=club_id,
        name=name,
        players=players,
    )
