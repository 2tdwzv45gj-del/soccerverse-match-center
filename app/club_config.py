from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClubConfig:
    slot: int
    club_id: Optional[int] = None
    formation_id: Optional[int] = None
    play_style: str = "Normal"
    team_name: str = ""
    result: Optional[dict] = field(default=None)

    @property
    def is_configured(self) -> bool:
        return self.club_id is not None


def create_default_configs() -> list[ClubConfig]:
    return [
        ClubConfig(slot=index)
        for index in range(1, 6)
    ]
