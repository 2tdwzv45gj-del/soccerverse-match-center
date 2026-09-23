import json
from dataclasses import asdict
from pathlib import Path

from app.club_config import ClubConfig


CONFIG_PATH = Path.home() / ".soccerverse_tactical_advisor.json"


def save_configs(
    configs: list[ClubConfig],
    path: Path = CONFIG_PATH,
) -> None:
    data = [
        {
            "slot": config.slot,
            "club_id": config.club_id,
            "formation_id": config.formation_id,
            "play_style": config.play_style,
        }
        for config in configs
    ]

    path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_configs(
    path: Path = CONFIG_PATH,
) -> list[ClubConfig]:
    if not path.exists():
        return [
            ClubConfig(slot=index)
            for index in range(1, 6)
        ]

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    configs = []

    for item in data:
        configs.append(
            ClubConfig(
                slot=int(item["slot"]),
                club_id=item.get("club_id"),
                formation_id=item.get(
                    "formation_id"
                ),
                play_style=item.get(
                    "play_style",
                    "Normal",
                ),
            )
        )

    while len(configs) < 5:
        configs.append(
            ClubConfig(
                slot=len(configs) + 1
            )
        )

    return configs[:5]
