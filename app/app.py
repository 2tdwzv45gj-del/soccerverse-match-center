import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.formation_engine_v2 import analyze_formations
from src.soccerverse_api import SoccerverseAPI
from src.team_loader import create_team

from app.club_config import ClubConfig
from app.pack_manager import PackManager
from app.config_store import load_configs, save_configs


STYLES = [
    "Normal",
    "Defensive",
    "Attacking",
    "Passing",
    "Counter",
    "Long Ball",
]

FORMATION_IDS = [7, 11, 12, 13, 15, 18, 20]


class ClubPanel(QWidget):
    def __init__(self, api, club_number, team_cache=None):
        super().__init__()

        self.api = api
        self.club_number = club_number
        self.team_cache = (
            team_cache
            if team_cache is not None
            else {}
        )
        self.config = ClubConfig(slot=club_number)
        self.team = None
        self.pack_manager = PackManager()
        self.results = None

        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)

        title = QLabel(
            f"CLUB {self.club_number}"
        )
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        root.addWidget(title)

        # Club ID
        club_row = QHBoxLayout()

        self.club_input = QLineEdit()
        self.club_input.setPlaceholderText(
            "Inserisci Club ID"
        )

        self.load_button = QPushButton(
            "CARICA SQUADRA"
        )
        self.load_button.clicked.connect(
            self.load_team
        )

        club_row.addWidget(
            QLabel("Club ID:")
        )
        club_row.addWidget(
            self.club_input
        )
        club_row.addWidget(
            self.load_button
        )

        root.addLayout(club_row)

        self.team_status = QLabel(
            "Nessuna squadra caricata."
        )

        root.addWidget(
            self.team_status
        )

        root.addSpacing(10)

        # Configuration
        form = QFormLayout()

        self.formation = QComboBox()

        formation_names = {
            7: "5-3-2",
            11: "4-1-4-1",
            12: "4-2-3-1",
            13: "4-1-2-2-1v2",
            15: "4-3-1-2",
            18: "1-4-3-2v2",
            20: "4-2-2-2",
        }

        for formation_id in FORMATION_IDS:
            self.formation.addItem(
                formation_names[formation_id],
                formation_id,
            )

        self.style = QComboBox()
        self.style.addItems(STYLES)

        form.addRow(
            "Formazione:",
            self.formation,
        )

        form.addRow(
            "Play Style:",
            self.style,
        )

        root.addLayout(form)

        self.generate_button = QPushButton(
            "GENERA XI"
        )
        self.generate_button.clicked.connect(
            self.generate_xi
        )

        root.addWidget(
            self.generate_button
        )

        root.addSpacing(10)

        self.result = QLabel(
            "Nessun risultato."
        )
        self.result.setWordWrap(True)

        root.addWidget(
            self.result
        )
        root.addStretch()

    def load_team(self):
        text = self.club_input.text().strip()

        if not text.isdigit():
            QMessageBox.warning(
                self,
                "Club ID",
                "Il Club ID deve essere numerico.",
            )
            return

        club_id = int(text)
        self.config.club_id = club_id

        self.team_status.setText(
            "Caricamento squadra via GSP..."
        )

        QApplication.processEvents()

        try:
            if club_id in self.team_cache:
                self.team = self.team_cache[club_id]

                self.team_status.setText(
                    f"{self.team.name} | "
                    f"Rosa: {len(self.team.players)} | "
                    f"Disponibili: "
                    f"{len(self.team.available_players)} | "
                    f"Infortunati: "
                    f"{len(self.team.injured_players)} | "
                    f"Squalificati: "
                    f"{len(self.team.banned_players)} "
                    "(CACHE)"
                )
                return

            result = self.api.gsp_call(
                "get_squad",
                {"club_id": club_id},
            )

            from src.gsp_squad_mapper import gsp_squad_to_players

            players = gsp_squad_to_players(
                result,
                club_id=club_id,
            )

            if not players:
                self.team = None

                self.team_status.setText(
                    "Nessun giocatore trovato."
                )
                return

            pack_name = self.pack_manager.get_club_name(club_id)
            team_name = pack_name or f"Club {club_id}"

            self.team = create_team(
                club_id=club_id,
                name=team_name,
                players_data=players,
            )

            self.team_cache[club_id] = self.team

            self.team_status.setText(
                f"{self.team.name} | "
                f"Rosa: {len(self.team.players)} | "
                f"Disponibili: "
                f"{len(self.team.available_players)} | "
                f"Infortunati: "
                f"{len(self.team.injured_players)} | "
                f"Squalificati: "
                f"{len(self.team.banned_players)}"
            )

        except Exception as exc:
            self.team = None

            QMessageBox.critical(
                self,
                "Errore GSP",
                f"Impossibile caricare la squadra via GSP:\n{exc}",
            )

            self.team_status.setText(
                "Errore caricamento squadra."
            )

    def generate_xi(self):
        if self.team is None:
            QMessageBox.warning(
                self,
                "Squadra",
                "Carica prima questa squadra.",
            )
            return

        style = self.style.currentText()
        self.config.formation_id = self.formation.currentData()
        self.config.play_style = style

        engine_style = (
            None
            if style == "Normal"
            else style
        )

        try:
            self.results = analyze_formations(
                self.team,
                style=engine_style,
            )

            selected_id = (
                self.formation.currentData()
            )

            selected = next(
                (
                    result
                    for result in self.results
                    if result.get("formation_id")
                    == selected_id
                ),
                None,
            )

            if selected is None:
                selected = self.results[0]

            lineup = selected["lineup"]

            lines = [
                f"Modulo: "
                f"{selected.get('name', selected_id)}",
                f"Score: "
                f"{selected['score']:.2f}",
                f"Copertura: "
                f"{lineup['positions_filled']}/11",
                f"Adattamenti: "
                f"{lineup['adaptations']}",
                f"Posizioni scoperte: "
                f"{lineup['missing_positions']}",
                f"Verdetto: "
                f"{lineup['verdict']}",
                "",
                "XI:",
            ]

            for assignment in (
                lineup["assignments"]
            ):
                player = assignment["player"]
                position = assignment["position"]

                if player is None:
                    lines.append(
                        f"{position}: "
                        "NESSUN GIOCATORE"
                    )
                else:
                    player_name = (
                        self.pack_manager.get_player_name(
                            player.player_id
                        )
                        or f"Player {player.player_id}"
                    )

                    lines.append(
                        f"{position}: "
                        f"{player_name} "
                        f"[ID {player.player_id}] "
                        f"(Rating "
                        f"{player.rating}, "
                        f"Fitness "
                        f"{player.fitness})"
                    )

            self.config.result = selected

            self.result.setText(
                "\n".join(lines)
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Errore motore",
                f"Errore durante l'analisi:\n{exc}",
            )


class TacticalAdvisorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Soccerverse Tactical Advisor"
        )

        self.resize(
            1150,
            750,
        )

        self.api = SoccerverseAPI()
        self.configs = []
        self.team_cache = {}

        self.build_ui()
        self.load_saved_configs()

    def save_current_configs(self):
        try:
            save_configs(self.configs)

            self.save_status.setText(
                "Configurazioni salvate."
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Salvataggio",
                f"Impossibile salvare le configurazioni:\n{exc}",
            )

    def load_saved_configs(self):
        try:
            configs = load_configs()

            if len(configs) != 5:
                raise ValueError(
                    "Il file di configurazione deve "
                    "contenere 5 slot."
                )

            self.configs = configs

            # I pannelli GUI vengono riallineati ai dati caricati.
            for index, config in enumerate(configs):
                panel = self.tabs.widget(index)

                panel.config = config

                if config.club_id is None:
                    panel.club_input.clear()
                    panel.team = None
                    panel.team_status.setText(
                        "Nessuna squadra caricata."
                    )
                else:
                    panel.club_input.setText(
                        str(config.club_id)
                    )

                if config.formation_id is not None:
                    position = panel.formation.findData(
                        config.formation_id
                    )

                    if position >= 0:
                        panel.formation.setCurrentIndex(
                            position
                        )

                style_position = panel.style.findText(
                    config.play_style
                )

                if style_position >= 0:
                    panel.style.setCurrentIndex(
                        style_position
                    )

            self.save_status.setText(
                "Configurazioni caricate."
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Caricamento",
                f"Impossibile caricare le configurazioni:\n{exc}",
            )

    def build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)

        title = QLabel(
            "SOCCERVERSE TACTICAL ADVISOR"
        )

        title.setStyleSheet(
            "font-size: 26px; "
            "font-weight: bold;"
        )

        subtitle = QLabel(
            "PHASE B — 5 CLUB FORMATION MANAGER"
        )

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(10)

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "SALVA CONFIGURAZIONI"
        )
        save_button.clicked.connect(
            self.save_current_configs
        )

        load_button = QPushButton(
            "CARICA CONFIGURAZIONI"
        )
        load_button.clicked.connect(
            self.load_saved_configs
        )

        buttons.addWidget(save_button)
        buttons.addWidget(load_button)
        buttons.addStretch()

        root.addLayout(buttons)
        root.addSpacing(5)

        self.save_status = QLabel(
            "Configurazioni non ancora salvate."
        )

        root.addWidget(
            self.save_status
        )

        self.tabs = QTabWidget()

        for club_number in range(1, 6):
            panel = ClubPanel(
                self.api,
                club_number,
                self.team_cache,
            )

            self.configs.append(panel.config)

            self.tabs.addTab(
                panel,
                f"CLUB {club_number}",
            )

        root.addWidget(
            self.tabs
        )

        self.setCentralWidget(
            central
        )


def main():
    app = QApplication(sys.argv)

    window = TacticalAdvisorWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
