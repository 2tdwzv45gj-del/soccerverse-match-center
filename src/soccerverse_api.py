import time

import requests


class SoccerverseAPI:
    GSP_BASE_URL = "https://play.soccerverse.com/gsp/v1/graph"

    BASE_URL = "https://services.soccerverse.com/api"
    PACK_URL = (
        "https://downloads.soccerverse.com/"
        "svpack/packv2/default.json"
    )

    def __init__(self):
        self.session = requests.Session()
        self._pack = None

    def gsp_call(self, method, params=None):
        """Single GSP JSON-RPC request.

        GSP is rate-limited: deliberately NO automatic retries.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
        }

        response = self.session.post(
            self.GSP_BASE_URL,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"GSP error: {data['error']}"
            )

        return data["result"]

    def get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"

        retry_delays = [0, 2, 4, 8]

        for attempt, delay in enumerate(retry_delays, start=1):
            if delay:
                time.sleep(delay)

            response = self.session.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code == 503:
                if attempt < len(retry_delays):
                    continue

            response.raise_for_status()

            return response.json()

        raise RuntimeError(
            f"API unavailable after "
            f"{len(retry_delays)} attempts: {url}"
        )

    def get_players(
        self,
        page=1,
        per_page=20,
        club_id=None
    ):
        params = {
            "page": page,
            "per_page": per_page
        }

        if club_id is not None:
            params["club_id"] = club_id

        return self.get(
            "players/detailed",
            params=params
        )

    def get_club(self, club_id):
        return self.get(
            "clubs/detailed",
            params={
                "club_id": club_id,
                "per_page": 5
            }
        )

    def get_pack(self):
        if self._pack is None:
            response = self.session.get(
                self.PACK_URL,
                timeout=30
            )

            response.raise_for_status()

            self._pack = response.json()["PackData"]

        return self._pack

    def get_club_name(self, club_id: int) -> str:
        pack = self.get_pack()

        clubs = pack["ClubData"]["C"]

        club_id_str = str(club_id)

        for club in clubs:
            if str(club.get("id")) == club_id_str:
                return club.get(
                    "n",
                    f"Club {club_id}"
                )

        return f"Club {club_id}"
