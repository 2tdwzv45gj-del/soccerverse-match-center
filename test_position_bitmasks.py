from src.soccerverse_api import SoccerverseAPI


EXPECTED = {
    "GK": 1,
    "LB": 2,
    "CB": 4,
    "RB": 8,
    "DML": 16,
    "DMC": 32,
    "DMR": 64,
    "LM": 128,
    "CM": 256,
    "RM": 512,
    "AML": 1024,
    "AMC": 2048,
    "AMR": 4096,
    "FL": 8192,
    "FC": 16384,
    "FR": 32768,
}


api = SoccerverseAPI()

data = api.get_players(
    page=1,
    per_page=100,
    club_id=22855,
)

observed = {}

for player in data["items"]:
    observed[player["position_main"]] = player["position"]


print("SOCCERVERSE POSITION BITMASK TEST")
print("-----------------------------------")

for position, expected_bitmask in EXPECTED.items():

    observed_bitmask = observed.get(position)

    if observed_bitmask is None:
        print(
            f"{position:<4} | "
            f"expected={expected_bitmask:<5} | "
            f"observed=NON PRESENTE"
        )
        continue

    print(
        f"{position:<4} | "
        f"expected={expected_bitmask:<5} | "
        f"observed={observed_bitmask:<5}"
    )

    assert observed_bitmask == expected_bitmask


print()
print("OK - Position bitmasks")
