from src.models.team import Player, Team
from src.formation_engine_v2 import analyze_formations


players = [
    Player(
        player_id=1,
        position_main="GK",
        positions=["GK"],
        rating=70,
        rating_gk=75,
        rating_tackling=20,
        rating_passing=45,
        rating_shooting=10,
        rating_stamina=70,
        rating_aggression=40,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=28,
    ),
    Player(
        player_id=2,
        position_main="LB",
        positions=["LB"],
        rating=70,
        rating_gk=10,
        rating_tackling=70,
        rating_passing=60,
        rating_shooting=40,
        rating_stamina=80,
        rating_aggression=60,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=25,
    ),
    Player(
        player_id=3,
        position_main="CB",
        positions=["CB"],
        rating=72,
        rating_gk=10,
        rating_tackling=75,
        rating_passing=55,
        rating_shooting=30,
        rating_stamina=75,
        rating_aggression=70,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=27,
    ),
    Player(
        player_id=4,
        position_main="CB",
        positions=["CB"],
        rating=68,
        rating_gk=10,
        rating_tackling=70,
        rating_passing=50,
        rating_shooting=30,
        rating_stamina=70,
        rating_aggression=65,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=26,
    ),
    Player(
        player_id=5,
        position_main="RB",
        positions=["RB"],
        rating=69,
        rating_gk=10,
        rating_tackling=68,
        rating_passing=62,
        rating_shooting=40,
        rating_stamina=82,
        rating_aggression=60,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=24,
    ),
    Player(
        player_id=6,
        position_main="LM",
        positions=["LM"],
        rating=67,
        rating_gk=10,
        rating_tackling=35,
        rating_passing=70,
        rating_shooting=60,
        rating_stamina=85,
        rating_aggression=45,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=25,
    ),
    Player(
        player_id=7,
        position_main="CM",
        positions=["CM"],
        rating=71,
        rating_gk=10,
        rating_tackling=50,
        rating_passing=78,
        rating_shooting=55,
        rating_stamina=85,
        rating_aggression=50,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=26,
    ),
    Player(
        player_id=8,
        position_main="CM",
        positions=["CM"],
        rating=69,
        rating_gk=10,
        rating_tackling=55,
        rating_passing=74,
        rating_shooting=50,
        rating_stamina=82,
        rating_aggression=55,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=27,
    ),
    Player(
        player_id=9,
        position_main="RM",
        positions=["RM"],
        rating=66,
        rating_gk=10,
        rating_tackling=35,
        rating_passing=68,
        rating_shooting=62,
        rating_stamina=84,
        rating_aggression=45,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=24,
    ),
    Player(
        player_id=10,
        position_main="FC",
        positions=["FC"],
        rating=78,
        rating_gk=10,
        rating_tackling=30,
        rating_passing=55,
        rating_shooting=88,
        rating_stamina=78,
        rating_aggression=65,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=27,
    ),
    Player(
        player_id=11,
        position_main="FC",
        positions=["FC"],
        rating=75,
        rating_gk=10,
        rating_tackling=30,
        rating_passing=52,
        rating_shooting=84,
        rating_stamina=80,
        rating_aggression=60,
        fitness=100,
        morale=100,
        concerns=0,
        form="",
        injured=0,
        banned=0,
        age=26,
    ),
]


team = Team(
    club_id=99999,
    name="Test Team",
    players=players,
)


results = analyze_formations(team)


assert len(results) == 7

for result in results:
    assert "name" in result
    assert "score" in result
    assert "lineup" in result
    assert result["lineup"]["positions_filled"] >= 0
    assert result["lineup"]["positions_filled"] <= 11


best = results[0]


def test_formation_engine_v2_regression():
    assert len(results) == 7
    for result in results:
        assert "name" in result
        assert "score" in result
        assert "lineup" in result
        assert 0 <= result["lineup"]["positions_filled"] <= 11

print("FORMATION ENGINE V2")
print("-----------------------------------")
print(f"Miglior modulo: {best['name']}")
print(f"Score: {best['score']:.2f}")
print(
    f"Copertura: "
    f"{best['lineup']['positions_filled']}/11"
)
print(
    f"Adattamenti: "
    f"{best['lineup']['adaptations']}"
)

print()
print("OK - Formation Engine V2")
