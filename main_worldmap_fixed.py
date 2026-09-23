from __future__ import annotations

import sys
import subprocess

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QScrollArea,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.commentary_mcp import SoccerverseMCPClient
from src.match_data_service import MatchDataService
from src.datapack_resolver import DatapackResolver
from src.commentary_replay import ReplayMode
from src.match_search import MatchSearchService

from app_match_center.replay_controller import MatchReplayController
from app_match_center.audio_player import MatchAudioPlayer
from src.match_audio import MatchAudioEngine


def load_image(url: str, size: int) -> QPixmap:
    try:
        result = subprocess.run(
            ["curl", "-L", "-s", "--fail", url],
            capture_output=True,
            timeout=10,
            check=True,
        )
        pixmap = QPixmap()
        if not pixmap.loadFromData(result.stdout):
            return QPixmap()
        return pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    except Exception:
        return QPixmap()


def rgb(value):
    return f"rgb({value[0]}, {value[1]}, {value[2]})"


class SearchWindow(QWidget):
    match_selected = Signal(int)

    MCP_URL = "https://mcp.soccerverse.io/mcp"

    def __init__(self, mcp: SoccerverseMCPClient, datapack: DatapackResolver) -> None:
        super().__init__()

        self.mcp = mcp
        self.datapack = datapack
        self.search_service = MatchSearchService(mcp, datapack)

        self._matches = []
        self._countries = []
        self._country = None
        self._leagues = []

        self._build_ui()

    def _mcp_call(self, tool_name: str, arguments: dict) -> dict:
        import requests

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        response = requests.post(
            self.MCP_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        result = data.get("result", {})
        content = result.get("content", [])
        if not content:
            raise RuntimeError(f"MCP: risposta vuota per {tool_name}")

        raw = content[0].get("text", "")
        if isinstance(raw, str):
            import json
            return json.loads(raw)

        return raw

    @staticmethod
    def _country_rows(data: dict) -> list[dict]:
        for key in ("countries", "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return []

    @staticmethod
    def _league_rows(data: dict) -> list[dict]:
        value = data.get("leagues")
        if isinstance(value, list):
            return value
        return []

    @staticmethod
    def _club_rows(data: object) -> list[dict]:
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if not isinstance(data, dict):
            return []

        for key in ("clubs", "teams", "table", "standings", "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return []

    def _load_countries(self) -> list[dict]:
        countries = []
        page = 1

        while page <= 20:
            data = self._mcp_call(
                "get_countries",
                {"page": page},
            )
            rows = self._country_rows(data)
            countries.extend(rows)

            pagination = data.get("pagination") or {}
            total_pages = int(pagination.get("total_pages") or page)

            if page >= total_pages or not rows:
                break

            page += 1

        return countries

    def _load_leagues(self, country_id: str) -> list[dict]:
        data = self._mcp_call(
            "get_leagues",
            {"country_id": country_id},
        )
        return self._league_rows(data)

    def _load_clubs(self, country_id: str, division: int) -> list[dict]:
        data = self._mcp_call(
            "get_league_tables",
            {
                "country_id": country_id,
                "league_id": league_id,
            },
        )
        return self._club_rows(data)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 36, 48, 36)
        root.setSpacing(14)

        self.setObjectName("searchRoot")

        header = QHBoxLayout()

        brand_box = QVBoxLayout()
        brand_box.setSpacing(2)

        brand = QLabel("SOCCERVERSE")
        brand.setObjectName("searchBrand")

        subtitle = QLabel("WORLD MAP  •  MATCH CENTER")
        subtitle.setObjectName("searchSubtitle")

        brand_box.addWidget(brand)
        brand_box.addWidget(subtitle)

        header.addLayout(brand_box)
        header.addStretch()

        self.breadcrumb = QLabel("WORLD")
        self.breadcrumb.setObjectName("worldBreadcrumb")
        header.addWidget(self.breadcrumb)

        root.addLayout(header)

        self.status = QLabel("")
        self.status.setObjectName("searchStatus")
        root.addWidget(self.status)

        # WORLD / COUNTRY / LEAGUE / CLUB navigation stack
        self.navigation_stack = QStackedWidget()
        self.navigation_stack.setObjectName("worldStack")
        root.addWidget(self.navigation_stack, 1)

        # ---------------- WORLD MAP ----------------
        world_page = QWidget()
        world_layout = QVBoxLayout(world_page)
        world_layout.setContentsMargins(0, 6, 0, 0)
        world_layout.setSpacing(12)

        intro = QLabel("WORLD MAP")
        intro.setObjectName("worldTitle")
        world_layout.addWidget(intro)

        description = QLabel(
            "Seleziona un paese per entrare nelle sue divisioni e raggiungere direttamente i club."
        )
        description.setObjectName("worldDescription")
        description.setWordWrap(True)
        world_layout.addWidget(description)

        country_search_row = QHBoxLayout()
        country_search_row.setSpacing(10)

        self.country_search = QLineEdit()
        self.country_search.setPlaceholderText("Filtra paesi…")
        self.country_search.setObjectName("countrySearch")
        self.country_search.textChanged.connect(self._filter_countries)
        country_search_row.addWidget(self.country_search, 1)

        refresh = QPushButton("↻  AGGIORNA")
        refresh.setObjectName("worldButton")
        refresh.clicked.connect(self.load_world)
        country_search_row.addWidget(refresh)

        world_layout.addLayout(country_search_row)

        self.country_list = QListWidget()
        self.country_list.setObjectName("countryList")
        self.country_list.itemClicked.connect(self._country_clicked)
        world_layout.addWidget(self.country_list, 1)

        self.navigation_stack.addWidget(world_page)

        # ---------------- COUNTRY / LEAGUES ----------------
        league_page = QWidget()
        league_layout = QVBoxLayout(league_page)
        league_layout.setContentsMargins(0, 6, 0, 0)
        league_layout.setSpacing(12)

        league_header = QHBoxLayout()

        self.country_title = QLabel("")
        self.country_title.setObjectName("worldTitle")
        league_header.addWidget(self.country_title)

        league_header.addStretch()

        back_world = QPushButton("←  WORLD")
        back_world.setObjectName("worldButton")
        back_world.clicked.connect(self.show_world)
        league_header.addWidget(back_world)

        league_layout.addLayout(league_header)

        self.league_list = QListWidget()
        self.league_list.setObjectName("leagueList")
        self.league_list.itemClicked.connect(self._league_clicked)
        league_layout.addWidget(self.league_list, 1)

        self.navigation_stack.addWidget(league_page)

        # ---------------- LEAGUE / CLUBS ----------------
        clubs_page = QWidget()
        clubs_layout = QVBoxLayout(clubs_page)
        clubs_layout.setContentsMargins(0, 6, 0, 0)
        clubs_layout.setSpacing(12)

        clubs_header = QHBoxLayout()

        self.league_title = QLabel("")
        self.league_title.setObjectName("worldTitle")
        clubs_header.addWidget(self.league_title)

        clubs_header.addStretch()

        back_country = QPushButton("←  DIVISIONI")
        back_country.setObjectName("worldButton")
        back_country.clicked.connect(self.show_leagues)
        clubs_header.addWidget(back_country)

        clubs_layout.addLayout(clubs_header)

        self.club_list = QListWidget()
        self.club_list.setObjectName("clubList")
        self.club_list.itemClicked.connect(self._club_clicked)
        clubs_layout.addWidget(self.club_list, 1)

        self.navigation_stack.addWidget(clubs_page)

        # ---------------- EXISTING MATCH LIST ----------------
        matches_page = QWidget()
        matches_layout = QVBoxLayout(matches_page)
        matches_layout.setContentsMargins(0, 6, 0, 0)
        matches_layout.setSpacing(10)

        matches_header = QHBoxLayout()

        self.results_title = QLabel("PARTITE")
        self.results_title.setObjectName("resultsTitle")
        matches_header.addWidget(self.results_title)

        matches_header.addStretch()

        back_club = QPushButton("←  CLUB")
        back_club.setObjectName("worldButton")
        back_club.clicked.connect(self.show_clubs)
        matches_header.addWidget(back_club)

        matches_layout.addLayout(matches_header)

        self.club_identity = QFrame()
        self.club_identity.setObjectName("clubIdentity")
        self.club_identity.setVisible(False)

        identity_layout = QHBoxLayout(self.club_identity)
        identity_layout.setContentsMargins(12, 10, 12, 10)
        identity_layout.setSpacing(12)

        self.club_logo = QLabel()
        self.club_logo.setObjectName("clubLogo")
        self.club_logo.setFixedSize(56, 56)
        self.club_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        identity_layout.addWidget(self.club_logo)

        identity_text = QVBoxLayout()
        identity_text.setSpacing(2)

        self.club_name_label = QLabel()
        self.club_name_label.setObjectName("clubName")
        identity_text.addWidget(self.club_name_label)

        self.club_id_label = QLabel()
        self.club_id_label.setObjectName("clubId")
        identity_text.addWidget(self.club_id_label)

        identity_layout.addLayout(identity_text, 1)
        matches_layout.addWidget(self.club_identity)

        self.matches_list = QListWidget()
        self.matches_list.setObjectName("matchesList")
        self.matches_list.itemDoubleClicked.connect(self.open_match)
        matches_layout.addWidget(self.matches_list, 1)

        hint = QLabel("Doppio clic su una partita per aprire il Match Center.")
        hint.setObjectName("searchHint")
        matches_layout.addWidget(hint)

        self.navigation_stack.addWidget(matches_page)

        # ---------------- QUICK SEARCH ----------------
        quick = QFrame()
        quick.setObjectName("quickSearchCard")
        quick_layout = QVBoxLayout(quick)
        quick_layout.setContentsMargins(14, 12, 14, 12)
        quick_layout.setSpacing(8)

        quick_title = QLabel("QUICK SEARCH")
        quick_title.setObjectName("quickTitle")
        quick_layout.addWidget(quick_title)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca direttamente una squadra…")
        self.search_input.setObjectName("searchInput")
        self.search_input.returnPressed.connect(self.search)

        search_button = QPushButton("CERCA")
        search_button.setObjectName("searchButton")
        search_button.clicked.connect(self.search)

        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(search_button)

        quick_layout.addLayout(search_row)
        root.addWidget(quick)

        self.load_world()

    def load_world(self) -> None:
        self.status.setText("CARICAMENTO WORLD MAP…")
        QApplication.processEvents()

        try:
            self._countries = self._load_countries()
        except Exception as exc:
            self.status.setText(f"World Map non disponibile: {exc}")
            self._countries = []
            return

        self._filter_countries()
        self.navigation_stack.setCurrentIndex(0)
        self.breadcrumb.setText("WORLD")
        self.status.setText(f"{len(self._countries)} PAESI DISPONIBILI")

    def _filter_countries(self) -> None:
        query = self.country_search.text().strip().lower()
        self.country_list.clear()

        rows = []
        for country in self._countries:
            country_id = str(
                country.get("country_id")
                or country.get("id")
                or ""
            ).upper()
            name = str(
                country.get("country_name")
                or country.get("name")
                or country.get("country")
                or country_id
            )

            if query and query not in name.lower() and query not in country_id.lower():
                continue

            rows.append((name, country_id, country))

        rows.sort(key=lambda item: item[0].lower())

        for name, country_id, country in rows:
            clubs = country.get("num_clubs") or country.get("total_clubs") or country.get("clubs") or ""
            leagues = country.get("num_leagues") or country.get("total_leagues") or country.get("leagues") or ""

            item = QListWidgetItem(
                f"{name.upper()}    {country_id}"
                f"\n{clubs} CLUBS   •   {leagues} DIVISIONI"
                if clubs or leagues
                else f"{name.upper()}    {country_id}"
            )
            item.setData(Qt.ItemDataRole.UserRole, country)
            self.country_list.addItem(item)

    def _country_clicked(self, item: QListWidgetItem) -> None:
        country = item.data(Qt.ItemDataRole.UserRole) or {}
        country_id = str(
            country.get("country_id")
            or country.get("id")
            or ""
        ).upper()

        if not country_id:
            return

        name = str(
            country.get("country_name")
            or country.get("name")
            or country.get("country")
            or country_id
        )

        self.status.setText(f"CARICAMENTO {name.upper()}…")
        QApplication.processEvents()

        try:
            self._leagues = self._load_leagues(country_id)
        except Exception as exc:
            self.status.setText(f"Errore caricando le divisioni: {exc}")
            return

        self._country = {
            "id": country_id,
            "name": name,
        }

        self.country_title.setText(name.upper())
        self.league_list.clear()

        self._leagues.sort(
            key=lambda league: int(league.get("division") or 999)
        )

        for league in self._leagues:
            division = int(league.get("division") or 0)
            league_id = league.get("league_id") or league.get("id") or "—"
            league_name = league.get("league_name") or f"Division {division}"
            teams = league.get("num_teams") or league.get("total_clubs") or ""

            item = QListWidgetItem(
                f"DIVISION {division}    •    {league_name.upper()}"
                f"\nLEAGUE ID {league_id}"
                + (f"   •   {teams} CLUBS" if teams else "")
            )
            item.setData(Qt.ItemDataRole.UserRole, league)
            self.league_list.addItem(item)

        self.breadcrumb.setText(f"WORLD  /  {country_id}")
        self.navigation_stack.setCurrentIndex(1)
        self.status.setText(f"{len(self._leagues)} DIVISIONI")

    def _league_clicked(self, item: QListWidgetItem) -> None:
        league = item.data(Qt.ItemDataRole.UserRole) or {}
        division = int(league.get("division") or 0)

        if not self._country or division <= 0:
            return

        country_id = self._country["id"]
        league_name = str(
            league.get("league_name")
            or f"Division {division}"
        )
        league_id = league.get("league_id") or league.get("id")

        self.status.setText(f"CARICAMENTO CLUB — {league_name.upper()}…")
        QApplication.processEvents()

        try:
            clubs = self._load_clubs(country_id, int(league_id))
        except Exception as exc:
            self.status.setText(f"Errore caricando i club: {exc}")
            return

        self.club_list.clear()
        self.league_title.setText(league_name.upper())

        clubs.sort(
            key=lambda club: int(
                club.get("new_position")
                or club.get("position")
                or club.get("club_ix")
                or 9999
            )
        )

        for club in clubs:
            club_id = club.get("club_id") or club.get("id")
            club_name = str(
                club.get("club_name")
                or club.get("name")
                or f"CLUB {club_id}"
            )

            position = (
                club.get("new_position")
                or club.get("position")
                or club.get("club_ix")
            )
            manager = club.get("manager_name") or ""

            line2 = f"CLUB ID {club_id}"
            if position is not None:
                line2 += f"   •   POS {position}"
            if manager:
                line2 += f"   •   MANAGER {manager}"

            item = QListWidgetItem(
                f"{club_name.upper()}\n{line2}"
            )
            item.setData(
                Qt.ItemDataRole.UserRole,
                {
                    "club_id": club_id,
                    "club_name": club_name,
                    "league": league,
                },
            )
            self.club_list.addItem(item)

        self.breadcrumb.setText(
            f"WORLD  /  {country_id}  /  DIV {division}"
        )
        self.navigation_stack.setCurrentIndex(2)
        self.status.setText(
            f"{len(clubs)} CLUBS  •  LEAGUE {league_id}"
        )

    def _club_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole) or {}
        club_id = data.get("club_id")
        club_name = str(data.get("club_name") or "")

        if club_id is None or not club_name:
            return

        self._open_club_matches(int(club_id), club_name)

    def _open_club_matches(self, club_id: int, fallback_name: str) -> None:
        self.status.setText(
            f"CARICAMENTO PARTITE — {fallback_name.upper()}…"
        )
        QApplication.processEvents()

        try:
            response = self.search_service.search(fallback_name)
        except Exception as exc:
            self.status.setText(f"Errore: {exc}")
            return

        # Club ID remains the primary identity. If name resolution lands
        # on another club, do not silently show the wrong club's matches.
        if int(response.club_id) != int(club_id):
            self.status.setText(
                f"Il nome {fallback_name.upper()} non ha risolto il CLUB ID {club_id}."
            )
            return

        self._matches = list(response.matches)

        club_logo = self.datapack.get_club_logo(club_id)
        club_colors = self.datapack.get_club_colors(club_id)

        self.club_name_label.setText(response.club_name.upper())
        self.club_id_label.setText(f"CLUB ID {club_id}")

        self.club_logo.clear()
        if club_logo:
            pixmap = load_image(club_logo, 52)
            if not pixmap.isNull():
                self.club_logo.setPixmap(pixmap)

        if club_colors:
            color = rgb(club_colors)
            self.results_title.setStyleSheet(f"color: {color};")
            self.club_identity.setStyleSheet(
                f"""
                QFrame#clubIdentity {{
                    border: 1px solid {color};
                    border-radius: 12px;
                    background: rgba(
                        {club_colors[0]},
                        {club_colors[1]},
                        {club_colors[2]},
                        28
                    );
                }}
                """
            )

        self.club_identity.setVisible(True)
        self.matches_list.clear()

        for match in self._matches:
            state = "CONCLUSA" if match.played else "PROGRAMMATA"
            text = (
                f"{match.home_team.upper()}  —  "
                f"{match.away_team.upper()}\n"
                f"{match.datetime}   •   "
                f"{match.competition or 'COMPETIZIONE'}   •   {state}"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, match.fixture_id)
            self.matches_list.addItem(item)

        self.breadcrumb.setText(
            f"WORLD  /  {self._country['id']}  /  CLUB {club_id}"
            if self._country
            else f"CLUB {club_id}"
        )
        self.navigation_stack.setCurrentIndex(3)

        if self._matches:
            self.status.setText(
                f"{response.club_name.upper()} — "
                f"{len(self._matches)} PARTITE"
            )
        else:
            self.status.setText(
                f"{response.club_name.upper()} — NESSUNA PARTITA"
            )

    def show_world(self) -> None:
        self.navigation_stack.setCurrentIndex(0)
        self.breadcrumb.setText("WORLD")
        self.status.setText(f"{len(self._countries)} PAESI DISPONIBILI")

    def show_leagues(self) -> None:
        self.navigation_stack.setCurrentIndex(1)
        if self._country:
            self.breadcrumb.setText(
                f"WORLD  /  {self._country['id']}"
            )

    def show_clubs(self) -> None:
        self.navigation_stack.setCurrentIndex(2)
        if self._country:
            self.breadcrumb.setText(
                f"WORLD  /  {self._country['id']}  /  CLUBS"
            )

    def search(self) -> None:
        name = self.search_input.text().strip()

        if not name:
            self.status.setText("Inserisci il nome di una squadra.")
            return

        self.status.setText("RICERCA IN CORSO…")
        QApplication.processEvents()

        try:
            response = self.search_service.search(name)
        except Exception as exc:
            self.status.setText(f"Errore: {exc}")
            return

        self._matches = list(response.matches)

        club_logo = self.datapack.get_club_logo(response.club_id)
        club_colors = self.datapack.get_club_colors(response.club_id)

        self.club_name_label.setText(response.club_name.upper())
        self.club_id_label.setText(f"CLUB ID {response.club_id}")

        self.club_logo.clear()
        if club_logo:
            pixmap = load_image(club_logo, 52)
            if not pixmap.isNull():
                self.club_logo.setPixmap(pixmap)

        if club_colors:
            color = rgb(club_colors)
            self.results_title.setStyleSheet(f"color: {color};")
            self.club_identity.setStyleSheet(
                f"""
                QFrame#clubIdentity {{
                    border: 1px solid {color};
                    border-radius: 12px;
                    background: rgba(
                        {club_colors[0]},
                        {club_colors[1]},
                        {club_colors[2]},
                        28
                    );
                }}
                """
            )

        self.club_identity.setVisible(True)
        self.matches_list.clear()

        for match in self._matches:
            state = "CONCLUSA" if match.played else "PROGRAMMATA"
            text = (
                f"{match.home_team.upper()}  —  "
                f"{match.away_team.upper()}\n"
                f"{match.datetime}   •   "
                f"{match.competition or 'COMPETIZIONE'}   •   {state}"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, match.fixture_id)
            self.matches_list.addItem(item)

        self.breadcrumb.setText(f"QUICK SEARCH  /  CLUB {response.club_id}")
        self.navigation_stack.setCurrentIndex(3)

        if not self._matches:
            self.status.setText(
                f"{response.club_name.upper()} — NESSUNA PARTITA"
            )
            return

        self.status.setText(
            f"{response.club_name.upper()} — "
            f"{len(self._matches)} PARTITE TROVATE"
        )

    def open_match(self, item: QListWidgetItem) -> None:
        fixture_id = int(item.data(Qt.ItemDataRole.UserRole))
        self.match_selected.emit(fixture_id)


class MatchCenterWindow(QMainWindow):
    def __init__(self, fixture_id: int, back_callback=None) -> None:
        super().__init__()

        self.fixture_id = fixture_id
        self.back_callback = back_callback

        self.setWindowTitle("Soccerverse Match Center")
        self.resize(1280, 860)

        mcp = SoccerverseMCPClient()
        self.match_data = MatchDataService(mcp).load(fixture_id)

        fixture = self.match_data.fixture
        attendance = int(fixture.get("attendance") or 0)

        self.datapack = DatapackResolver()

        home_club_id = int(fixture["home_club"])
        away_club_id = int(fixture["away_club"])

        home_pack = self.datapack.get_club(home_club_id)
        away_pack = self.datapack.get_club(away_club_id)

        self.home_name = (
            home_pack["n"]
            if home_pack
            else fixture["home_club_name"]
        )
        self.away_name = (
            away_pack["n"]
            if away_pack
            else fixture["away_club_name"]
        )

        self.home_logo = (
            self.datapack.get_club_logo(home_club_id)
            or ""
        )
        self.away_logo = (
            self.datapack.get_club_logo(away_club_id)
            or ""
        )

        self.home_rgb = self._club_rgb(home_club_id, (255, 255, 255))
        self.away_rgb = self._club_rgb(away_club_id, (255, 0, 0))

        self.stadium_image = ""
        self.stadium_name = "SOCCERVERSE STADIUM"

        stadium_id = fixture.get("stadium_id") or fixture.get("stadium")

        if stadium_id:
            stadium_pack = self.datapack.get_stadium(stadium_id)

            if stadium_pack:
                self.stadium_name = (
                    stadium_pack.get("n")
                    or stadium_pack.get("name")
                    or fixture.get("stadium_name")
                    or "SOCCERVERSE STADIUM"
                )

                self.stadium_image = (
                    self.datapack.get_stadium_image(stadium_id)
                    or ""
                )
            else:
                self.stadium_name = (
                    fixture.get("stadium_name")
                    or "SOCCERVERSE STADIUM"
                )
        else:
            self.stadium_name = (
                fixture.get("stadium_name")
                or "SOCCERVERSE STADIUM"
            )

        self.audio_engine = MatchAudioEngine(
            attendance=attendance,
            home_club_id=home_club_id,
            away_club_id=away_club_id,
        )

        self.audio_player = MatchAudioPlayer()
        self._last_audio_action_id: int | None = None
        self._audio_started = False
        self._audio_finished = False

        self.replay = MatchReplayController(
            self.match_data,
            ReplayMode.M3,
        )

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)

        self._build_ui()
        self._apply_style()
        self.reset_replay()

    def _club_rgb(self, club_id: int, fallback):
        colors = self.datapack.get_club_colors(club_id)

        if colors:
            try:
                return tuple(int(x) for x in colors[:3])
            except Exception:
                pass

        return fallback

    def _official_event_rows(self):
        """Build the official match event table from normalized MatchData."""
        rows = []

        events = sorted(
            self.match_data.events,
            key=lambda event: (
                int(event.get("time", 0)),
                int(event.get("match_event_id", 0)),
            ),
        )

        home_id = int(self.match_data.fixture["home_club"])
        away_id = int(self.match_data.fixture["away_club"])

        for event in events:
            event_type = str(
                event.get("event_type", "")
            ).upper()

            minute = int(event.get("time", 0) or 0)
            player = (
                event.get("player_name")
                or event.get("player")
                or ""
            )

            club_id = event.get("club_id")
            club_id = int(club_id) if club_id is not None else None

            if club_id == home_id:
                club = self.home_name
            elif club_id == away_id:
                club = self.away_name
            else:
                club = event.get("club_name") or ""

            if event_type == "GOAL":
                rows.append(("⚽", "GOAL", minute, club, player))

            elif event_type in {"YELLOWCARD", "YELLOW_CARD"}:
                rows.append(("🟨", "YELLOW", minute, club, player))

            elif event_type in {"REDCARD", "RED_CARD"}:
                rows.append(("🟥", "RED", minute, club, player))

            elif event_type in {"INJURY", "INJURED"}:
                rows.append(("🩹", "INJURY", minute, club, player))

        # Substitutions come from the dedicated official endpoint.
        for sub in self.match_data.substitutions:
            minute = int(
                sub.get("time")
                or sub.get("minute")
                or 0
            )

            club_id = sub.get("club_id")
            club_id = int(club_id) if club_id is not None else None

            if club_id == home_id:
                club = self.home_name
            elif club_id == away_id:
                club = self.away_name
            else:
                club = sub.get("club_name") or ""

            player_on = (
                sub.get("player_on_name")
                or sub.get("player_on")
                or ""
            )
            player_off = (
                sub.get("player_off_name")
                or sub.get("player_off")
                or ""
            )

            if player_on or player_off:
                if player_on and player_off:
                    player = f"{player_on}  ↔  {player_off}"
                else:
                    player = player_on or player_off

                rows.append(
                    ("🔄", "SUBSTITUTION", minute, club, player)
                )

        rows.sort(key=lambda row: row[2])
        return rows

    def _build_scorers(self):
        """Build team-separated scorer lists from official normalized goals."""
        home_id = int(self.match_data.fixture["home_club"])
        away_id = int(self.match_data.fixture["away_club"])

        home = []
        away = []

        for event in sorted(
            self.match_data.events,
            key=lambda event: (
                int(event.get("time", 0)),
                int(event.get("match_event_id", 0)),
            ),
        ):
            if str(event.get("event_type", "")).upper() != "GOAL":
                continue

            minute = int(event.get("time", 0) or 0)
            name = (
                event.get("player_name")
                or event.get("player")
                or "Azione di squadra"
            )

            club_id = event.get("club_id")
            if club_id is None:
                continue

            club_id = int(club_id)

            item = (minute, name)

            if club_id == home_id:
                home.append(item)
            elif club_id == away_id:
                away.append(item)

        return home, away

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")

        main = QVBoxLayout(root)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(14)

        top = QHBoxLayout()

        brand = QLabel("SOCCERVERSE")
        brand.setObjectName("brand")

        competition_name = (
            self.match_data.fixture.get("comp_name")
            or self.match_data.fixture.get("league_name")
            or "MATCH CENTER"
        )

        competition = QLabel(
            f"{competition_name.upper()}  •  MATCH {self.fixture_id}"
        )
        competition.setObjectName("competition")

        live = QLabel("●  MATCH CENTER")
        live.setObjectName("live")

        top.addWidget(brand)
        top.addStretch()
        top.addWidget(competition)
        top.addSpacing(24)
        top.addWidget(live)

        main.addLayout(top)

        if self.back_callback is not None:
            back = QPushButton("←  CERCA UN'ALTRA PARTITA")
            back.setObjectName("backButton")
            back.clicked.connect(self._go_back)
            main.addWidget(back)


        scoreboard = QFrame()
        scoreboard.setObjectName("scoreboard")

        score_layout = QHBoxLayout(scoreboard)
        score_layout.setContentsMargins(32, 22, 32, 22)

        home_column = QVBoxLayout()
        home_column.setAlignment(Qt.AlignmentFlag.AlignCenter)

        home_logo = QLabel()

        if self.home_logo:
            home_logo.setPixmap(load_image(self.home_logo, 78))

        home_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.home_label = QLabel(self.home_name.upper())
        self.home_label.setObjectName("teamHome")
        self.home_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        home_column.addWidget(home_logo)
        home_column.addWidget(self.home_label)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("READY")
        self.status.setObjectName("status")

        # Match Center always starts from the unrevealed state.
        # The official score is revealed only by replay progression.
        self.score = QLabel("0  —  0")
        self.score.setObjectName("score")
        self.score.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scorer = QLabel("")
        self.scorer.setObjectName("scorer")
        self.scorer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.minute = QLabel("0'")
        self.minute.setObjectName("minute")
        self.minute.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center.addWidget(self.status)
        center.addWidget(self.score)
        center.addWidget(self.minute)
        center.addWidget(self.scorer)

        away_column = QVBoxLayout()
        away_column.setAlignment(Qt.AlignmentFlag.AlignCenter)

        away_logo = QLabel()

        if self.away_logo:
            away_logo.setPixmap(load_image(self.away_logo, 78))

        away_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.away_label = QLabel(self.away_name.upper())
        self.away_label.setObjectName("teamAway")
        self.away_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        away_column.addWidget(away_logo)
        away_column.addWidget(self.away_label)

        score_layout.addLayout(home_column, 1)
        score_layout.addLayout(center, 1)
        score_layout.addLayout(away_column, 1)

        main.addWidget(scoreboard)

        # ----------------------------------------------------
        # OFFICIAL SCORERS
        # ----------------------------------------------------
        # MANAGERS
        managers_card = QFrame()
        managers_card.setObjectName("managersCard")

        managers_layout = QHBoxLayout(managers_card)
        managers_layout.setContentsMargins(18, 10, 18, 10)
        managers_layout.setSpacing(18)

        home_manager = str(
            self.match_data.fixture.get("home_manager") or "—"
        )
        away_manager = str(
            self.match_data.fixture.get("away_manager") or "—"
        )

        home_manager_label = QLabel(
            f"{self.home_name.upper()}   •   MANAGER  {home_manager}"
        )
        home_manager_label.setObjectName("managerHome")
        home_manager_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        away_manager_label = QLabel(
            f"MANAGER  {away_manager}   •   {self.away_name.upper()}"
        )
        away_manager_label.setObjectName("managerAway")
        away_manager_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        managers_layout.addWidget(home_manager_label, 1)
        managers_layout.addWidget(away_manager_label, 1)

        main.addWidget(managers_card)

        scorers_card = QFrame()
        scorers_card.setObjectName("scorersCard")

        scorers_layout = QHBoxLayout(scorers_card)
        scorers_layout.setContentsMargins(18, 12, 18, 12)
        scorers_layout.setSpacing(18)

        self.home_scorers_label = QLabel(
            self.home_name.upper()
        )
        self.home_scorers_label.setObjectName("scorersHome")
        self.home_scorers_label.setWordWrap(True)

        self.away_scorers_label = QLabel(
            self.away_name.upper()
        )
        self.away_scorers_label.setObjectName("scorersAway")
        self.away_scorers_label.setWordWrap(True)

        scorers_layout.addWidget(self.home_scorers_label, 1)
        scorers_layout.addWidget(self.away_scorers_label, 1)

        main.addWidget(scorers_card)

        # ----------------------------------------------------
        # OFFICIAL MATCH EVENTS
        # ----------------------------------------------------
        official_card = QFrame()
        official_card.setObjectName("officialEvents")

        official_layout = QVBoxLayout(official_card)
        official_layout.setContentsMargins(18, 14, 18, 14)
        official_layout.setSpacing(8)

        official_title = QLabel("MATCH EVENTS")
        official_title.setObjectName("section")
        official_layout.addWidget(official_title)

        # Keep the official event list compact so the replay
        # controls remain visible. The list itself is scrollable.
        official_scroll = QScrollArea()
        official_scroll.setObjectName("officialEventsScroll")
        official_scroll.setWidgetResizable(True)
        official_scroll.setFrameShape(QFrame.Shape.NoFrame)
        official_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        official_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        official_scroll.setMaximumHeight(250)

        official_body = QWidget()
        self.official_body_layout = QVBoxLayout(official_body)
        self.official_body_layout.setContentsMargins(0, 0, 0, 0)
        self.official_body_layout.setSpacing(5)

        # IMPORTANT:
        # Official events are revealed by replay progression.
        # Nothing is shown before PLAY.
        empty = QLabel("NESSUN EVENTO")
        empty.setObjectName("officialEventEmpty")
        self.official_body_layout.addWidget(empty)
        self.official_body_layout.addStretch()

        official_scroll.setWidget(official_body)

        official_layout.addWidget(official_scroll)
        main.addWidget(official_card)

        content = QHBoxLayout()
        content.setSpacing(14)

        stadium_card = QFrame()
        stadium_card.setObjectName("stadiumCard")

        stadium_card_layout = QVBoxLayout(stadium_card)
        stadium_card_layout.setContentsMargins(14, 14, 14, 14)
        stadium_card_layout.setSpacing(8)

        stadium_thumb = QLabel()
        stadium_thumb.setObjectName("stadiumThumb")
        stadium_thumb.setFixedSize(360, 150)
        stadium_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stadium_pixmap = (
            load_image(self.stadium_image, 360)
            if self.stadium_image
            else QPixmap()
        )

        if not stadium_pixmap.isNull():
            stadium_thumb.setPixmap(stadium_pixmap)
        else:
            stadium_thumb.setText("STADIO")

        stadium_card_layout.addWidget(stadium_thumb)

        stadium_card_name = QLabel(self.stadium_name.upper())
        stadium_card_name.setObjectName("stadiumCardName")
        stadium_card_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stadium_card_name.setWordWrap(True)

        stadium_card_layout.addWidget(stadium_card_name)

        stadium_card_attendance = QLabel(
            f"{int(self.match_data.fixture.get('attendance') or 0):,} PRESENTI"
        )
        stadium_card_attendance.setObjectName("stadiumCardAttendance")
        stadium_card_attendance.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stadium_card_layout.addWidget(stadium_card_attendance)

        content.addWidget(stadium_card, 0)

        commentary = QFrame()
        commentary.setObjectName("commentary")

        commentary_layout = QVBoxLayout(commentary)
        commentary_layout.setContentsMargins(24, 20, 24, 20)

        commentary_title = QLabel("MATCH TIMELINE")
        commentary_title.setObjectName("section")

        commentary_layout.addWidget(commentary_title)

        self.feed_layout = QVBoxLayout()
        commentary_layout.addLayout(self.feed_layout)
        commentary_layout.addStretch()

        content.addWidget(commentary, 2)

        main.addLayout(content, 1)

        controls = QFrame()
        controls.setObjectName("controls")

        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(18, 12, 18, 12)

        replay_label = QLabel("REPLAY")
        replay_label.setObjectName("replayLabel")

        controls_layout.addWidget(replay_label)
        controls_layout.addSpacing(12)

        self.play_button = QPushButton("▶  PLAY")
        self.play_button.setObjectName("play")
        self.play_button.clicked.connect(self.toggle_play)

        controls_layout.addWidget(self.play_button)

        reset = QPushButton("↺")
        reset.clicked.connect(self.reset_replay)
        controls_layout.addWidget(reset)

        for text, mode in (
            ("2'", ReplayMode.M2),
            ("3'", ReplayMode.M3),
            ("5'", ReplayMode.M5),
            ("10'", ReplayMode.M10),
        ):
            button = QPushButton(text)
            button.clicked.connect(
                lambda checked=False, selected=mode: self.change_mode(selected)
            )
            controls_layout.addWidget(button)

        controls_layout.addStretch()

        self.replay_status = QLabel("0.0s")
        self.replay_status.setObjectName("replayStatus")

        controls_layout.addWidget(self.replay_status)

        main.addWidget(controls)

        self.setCentralWidget(root)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#root {{
                background: #07090d;
                color: #f4f5f7;
            }}

            QLabel#brand {{
                color: #ffffff;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 3px;
            }}

            QLabel#competition {{
                color: #858d9c;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1.5px;
            }}

            QLabel#live {{
                color: #ff4d5a;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
            }}

            QPushButton#backButton {{
                padding: 8px 14px;
                max-width: 230px;
            }}

            QFrame#scoreboard {{
                background: #10141b;
                border: 1px solid #282f3b;
                border-radius: 18px;
            }}

            QLabel#teamHome {{
                color: {rgb(self.home_rgb)};
                font-size: 27px;
                font-weight: 900;
                letter-spacing: 3px;
            }}

            QLabel#teamAway {{
                color: {rgb(self.away_rgb)};
                font-size: 27px;
                font-weight: 900;
                letter-spacing: 3px;
            }}

            QLabel#status {{
                color: #737d8d;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 2px;
            }}

            QLabel#score {{
                color: #ffffff;
                font-size: 58px;
                font-weight: 950;
            }}

            QLabel#minute {{
                color: #aeb6c2;
                font-size: 16px;
                font-weight: 900;
            }}

            QLabel#scorer {{
                color: #9ba4b3;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            QFrame#managersCard {{
                background: #10151d;
                border: 1px solid #252c37;
                border-radius: 10px;
            }}

            QLabel#managerHome,
            QLabel#managerAway {{
                color: #8f9aaa;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}

            QFrame#scorersCard {{
                background: rgba(255,255,255,0.035);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }}

            QLabel#scorersHome,
            QLabel#scorersAway {{
                font-size: 12px;
                font-weight: 700;
                line-height: 1.45;
            }}

            QLabel#scorersHome {{
                padding-right: 12px;
            }}

            QLabel#scorersAway {{
                padding-left: 12px;
            }}

            QScrollArea#officialEventsScroll {{
                background: transparent;
                border: none;
            }}

            QScrollArea#officialEventsScroll QWidget {{
                background: transparent;
            }}

            QFrame#officialEvents {{
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 12px;
                padding: 2px;
            }}

            QLabel#officialEvent {{
                font-size: 11px;
                font-weight: 600;
                padding: 3px 6px;
            }}

            QLabel#officialEventEmpty {{
                font-size: 11px;
                opacity: 0.55;
                padding: 4px 6px;
            }}

            QFrame#stadiumCard,
            QFrame#commentary {{
                background: #0d1219;
                border: 1px solid #222a35;
                border-radius: 15px;
            }}

            QLabel#stadiumCardName {{
                color: #ffffff;
                font-size: 13px;
                font-weight: 900;
            }}

            QLabel#stadiumCardAttendance {{
                color: #737d8d;
                font-size: 11px;
                font-weight: 800;
            }}

            QLabel#section {{
                color: #697486;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 2px;
            }}

            QLabel#feedItem {{
                color: #c1c7d0;
                font-size: 14px;
                padding: 4px 0;
            }}

            QFrame#controls {{
                background: #10141b;
                border: 1px solid #252c37;
                border-radius: 13px;
            }}

            QLabel#replayLabel {{
                color: #778294;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 1.5px;
            }}

            QLabel#replayStatus {{
                color: #697486;
                font-size: 11px;
                font-weight: 700;
            }}

            QPushButton {{
                background: #171c25;
                color: #e9ecf1;
                border: 1px solid #303846;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background: #242b36;
            }}

            QPushButton#play {{
                padding-left: 22px;
                padding-right: 22px;
            }}

            /* WORLD MAP / SEARCH */
            QWidget#searchRoot {{
                background: #07090d;
            }}

            QLabel#searchBrand {{
                color: #ffffff;
                font-size: 34px;
                font-weight: 950;
                letter-spacing: 6px;
            }}

            QLabel#searchSubtitle {{
                color: #697486;
                font-size: 13px;
                font-weight: 900;
                letter-spacing: 3px;
            }}

            QLabel#worldBreadcrumb {{
                color: #8f9aaa;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 1.5px;
            }}

            QLabel#worldTitle {{
                color: #ffffff;
                font-size: 22px;
                font-weight: 900;
                letter-spacing: 1px;
            }}

            QLabel#worldDescription {{
                color: #7f8999;
                font-size: 13px;
            }}

            QLineEdit#countrySearch {{
                background: #10141b;
                color: #ffffff;
                border: 1px solid #303846;
                border-radius: 10px;
                padding: 12px 14px;
                font-size: 14px;
            }}

            QListWidget#countryList,
            QListWidget#leagueList,
            QListWidget#clubList {{
                background: #0d1219;
                color: #e9ecf1;
                border: 1px solid #222a35;
                border-radius: 14px;
                padding: 8px;
                outline: none;
            }}

            QListWidget#countryList::item,
            QListWidget#leagueList::item,
            QListWidget#clubList::item {{
                padding: 14px 12px;
                border-bottom: 1px solid #222a35;
            }}

            QListWidget#countryList::item:hover,
            QListWidget#leagueList::item:hover,
            QListWidget#clubList::item:hover {{
                background: #171c25;
            }}

            QListWidget#countryList::item:selected,
            QListWidget#leagueList::item:selected,
            QListWidget#clubList::item:selected {{
                background: #1b222d;
                border: 1px solid #3b4556;
            }}

            QPushButton#worldButton {{
                padding: 9px 14px;
            }}

            QFrame#quickSearchCard {{
                background: #0d1219;
                border: 1px solid #222a35;
                border-radius: 14px;
            }}

            QLabel#quickTitle {{
                color: #697486;
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 2px;
            }}

            /* SEARCH */

            QWidget#searchRoot {{
                background: #07090d;
            }}

            QLabel#searchBrand {{
                color: #ffffff;
                font-size: 34px;
                font-weight: 950;
                letter-spacing: 6px;
            }}

            QLabel#searchSubtitle {{
                color: #697486;
                font-size: 13px;
                font-weight: 900;
                letter-spacing: 3px;
            }}

            QLabel#searchIntro {{
                color: #c1c7d0;
                font-size: 17px;
                margin-top: 18px;
                margin-bottom: 4px;
            }}

            QLineEdit#searchInput {{
                background: #10141b;
                color: #ffffff;
                border: 1px solid #303846;
                border-radius: 10px;
                padding: 14px 16px;
                font-size: 16px;
            }}

            QLineEdit#searchInput:focus {{
                border: 1px solid #697486;
            }}

            QPushButton#searchButton {{
                padding: 14px 24px;
            }}

            QLabel#searchStatus {{
                color: #858d9c;
                font-size: 12px;
                font-weight: 800;
                min-height: 20px;
            }}

            QFrame#clubIdentity {{
                border-radius: 12px;
                padding: 4px;
            }}

            QLabel#clubLogo {{
                background: transparent;
            }}

            QLabel#clubName {{
                font-size: 28px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            QLabel#clubId {{
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
                opacity: 0.70;
            }}

            QLabel#resultsTitle {{
                color: #697486;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 2px;
                margin-top: 10px;
            }}

            QListWidget#matchesList {{
                background: #0d1219;
                color: #e9ecf1;
                border: 1px solid #222a35;
                border-radius: 14px;
                padding: 8px;
                font-size: 14px;
                outline: none;
            }}

            QListWidget#matchesList::item {{
                padding: 15px 12px;
                border-bottom: 1px solid #222a35;
            }}

            QListWidget#matchesList::item:selected {{
                background: #171c25;
                border: 1px solid #303846;
            }}

            QLabel#searchHint {{
                color: #586273;
                font-size: 11px;
                font-weight: 700;
            }}
            """
        )

    def _go_back(self) -> None:
        self.timer.stop()
        if self.back_callback:
            self.back_callback()

    def toggle_play(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
            self.play_button.setText("▶  PLAY")
            self.status.setText("PAUSED")
        else:
            if self.replay.elapsed_seconds >= self.replay.duration_seconds:
                self.reset_replay()

            if not self._audio_started:
                self.audio_player.start_whistle()
                self._audio_started = True

            self.timer.start()
            self.play_button.setText("Ⅱ  PAUSE")
            self.status.setText("LIVE")

    def tick(self) -> None:
        state = self.replay.advance(0.1)

        self.score.setText(
            f"{state.home_score}  —  {state.away_score}"
        )
        self.minute.setText(f"{state.match_minute}'")

        # Official events are revealed only when the replay reaches them.
        self._update_official_events(state.match_minute)

        current_scene = (
            state.visible_scenes[-1].scene
            if state.visible_scenes
            else None
        )

        if current_scene is not None:
            self.scorer.setText(
                f"{current_scene.match_minute}'  "
                f"{(current_scene.player_name or 'Azione di squadra').upper()}"
                if current_scene.kind == "goal"
                else ""
            )
        else:
            self.scorer.setText("")

        # Audio: one trigger per official action.
        # Normal events remain silent.
        if current_scene is not None:
            action_id = int(current_scene.action_id)

            if action_id != self._last_audio_action_id:
                intensity = 1.0

                if current_scene.kind == "goal":
                    intensity = self.audio_engine.goal_intensity(
                        current_scene.club_name == self.home_name
                    )
                    self.audio_player.goal(action_id, intensity)

                elif current_scene.kind == "red_card":
                    intensity = self.audio_engine.red_card_intensity()
                    self.audio_player.red_card(action_id, intensity)

                elif current_scene.kind == "substitution":
                    intensity = self.audio_engine.substitution_intensity()
                    self.audio_player.substitution(action_id, intensity)

                self._last_audio_action_id = action_id

        self.replay_status.setText(
            f"{state.elapsed_seconds:05.1f} / "
            f"{self.replay.duration_seconds:.1f}s"
        )

        while self.feed_layout.count():
            item = self.feed_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

        event_labels = {
            "goal": "GOL",
            "substitution": "SOSTITUZIONE",
            "chance_saved": "PARATA",
            "chance_offtarget": "TIRO FUORI",
            "chance_tackled": "CONTRASTO",
            "chance": "OCCASIONE",
            "shot": "TIRO",
            "save": "PARATA",
            "tackle": "CONTRASTO",
            "offtarget": "TIRO FUORI",
        }

        for visible in state.visible_scenes[-12:]:
            scene = visible.scene
            player = scene.player_name or "Azione di squadra"
            club = scene.club_name or "MATCH"
            event_type = event_labels.get(scene.kind, "AZIONE")

            label = QLabel(
                f"{scene.match_minute}'   "
                f"{club.upper()}   •   "
                f"{event_type}   •   "
                f"{player}"
            )
            label.setObjectName("feedItem")
            self.feed_layout.addWidget(label)

        if state.current_kind == "goal":
            self.status.setText("GOAL")

        if self.replay.elapsed_seconds >= self.replay.duration_seconds:
            if not self._audio_finished:
                self.audio_player.final_whistle()
                self._audio_finished = True

            self.timer.stop()
            self.play_button.setText("↻  REPLAY")
            self.status.setText("FINAL")

    def _clear_live_match_panels(self) -> None:
        """Return official GUI panels to their unrevealed state."""
        if not hasattr(self, "official_body_layout"):
            return
        if not hasattr(self, "home_scorers_label"):
            return
        if not hasattr(self, "away_scorers_label"):
            return

        self.home_scorers_label.setText(
            self.home_name.upper()
        )
        self.away_scorers_label.setText(
            self.away_name.upper()
        )

        while self.official_body_layout.count():
            item = self.official_body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        empty = QLabel("NESSUN EVENTO")
        empty.setObjectName("officialEventEmpty")
        self.official_body_layout.addWidget(empty)
        self.official_body_layout.addStretch()

    def _update_official_events(self, match_minute: int) -> None:
        """Reveal official match events progressively with the replay clock."""
        if not hasattr(self, "official_body_layout"):
            return

        rows = self._official_event_rows()
        visible_rows = [
            row for row in rows
            if int(row[2]) <= int(match_minute)
        ]

        while self.official_body_layout.count():
            item = self.official_body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not visible_rows:
            empty = QLabel("NESSUN EVENTO")
            empty.setObjectName("officialEventEmpty")
            self.official_body_layout.addWidget(empty)
            self.official_body_layout.addStretch()
            return

        for icon, kind, minute, club, player in visible_rows:
            if kind == "SUBSTITUTION":
                substitution_text = player
            else:
                substitution_text = player

            label = QLabel(
                f"{icon}  {minute}'   {club.upper()}   •   {substitution_text}"
            )
            label.setObjectName("officialEventItem")
            label.setWordWrap(True)
            self.official_body_layout.addWidget(label)

        self.official_body_layout.addStretch()

        scroll = getattr(self, "official_scroll", None)
        if scroll is not None:
            QTimer.singleShot(
                0,
                lambda: scroll.verticalScrollBar().setValue(
                    scroll.verticalScrollBar().maximum()
                ),
            )

    def reset_replay(self) -> None:
        self._clear_live_match_panels()
        self.timer.stop()

        self.audio_player.reset()
        self._last_audio_action_id = None
        self._audio_started = False
        self._audio_finished = False

        state = self.replay.reset()

        self.play_button.setText("▶  PLAY")
        self.status.setText("READY")
        self.score.setText(
            f"{state.home_score}  —  {state.away_score}"
        )
        self.minute.setText(f"{state.match_minute}'")
        self.scorer.setText("")
        self.replay_status.setText(
            f"0.0 / {self.replay.duration_seconds:.1f}s"
        )

    def change_mode(self, mode: ReplayMode) -> None:
        self.timer.stop()

        self.replay = MatchReplayController(
            self.replay.match_data,
            mode,
        )

        self.reset_replay()


class AppWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Soccerverse")
        self.resize(1280, 860)

        self.mcp = SoccerverseMCPClient()
        self.datapack = DatapackResolver()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.datapack = DatapackResolver()
        self.search_page = SearchWindow(self.mcp, self.datapack)
        self.search_page.match_selected.connect(self.open_match)

        self.stack.addWidget(self.search_page)

        self.match_window: MatchCenterWindow | None = None

        self.setStyleSheet(
            """
            QWidget {
                background: #07090d;
                color: #f4f5f7;
            }

            QLabel {
                color: #f4f5f7;
            }

            QPushButton {
                color: #ffffff;
                background: #222a36;
                border: 1px solid #647087;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 900;
            }

            QLineEdit {
                color: #ffffff;
                background: #10141b;
                border: 1px solid #566176;
                border-radius: 10px;
                padding: 12px;
            }

            QListWidget {
                color: #f4f5f7;
                background: #10141b;
            }
            """
        )

    def open_match(self, fixture_id: int) -> None:
        try:
            match = MatchCenterWindow(
                fixture_id,
                back_callback=self.show_search,
            )
        except Exception as exc:
            self.search_page.status.setText(
                f"Impossibile aprire la partita: {exc}"
            )
            return

        if self.match_window is not None:
            self.stack.removeWidget(self.match_window)
            self.match_window.deleteLater()

        self.match_window = match
        self.stack.addWidget(match)
        self.stack.setCurrentWidget(match)

    def show_search(self) -> None:
        if self.match_window is not None:
            self.stack.setCurrentWidget(self.search_page)


app = QApplication(sys.argv)
app.setFont(QFont("Arial", 10))

window = AppWindow()
window.show()

sys.exit(app.exec())
