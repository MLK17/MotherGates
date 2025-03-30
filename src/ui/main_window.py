from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from ..core.config import APP_NAME, APP_VERSION
from .widgets.match_widget import MatchWidget
from .widgets.logs_widget import LogsWidget
from .widgets.tournament_widget import TournamentWidget
from .widgets.team_widget import TeamWidget
from .widgets.school_widget import SchoolWidget
from .dialogs.create_admin_dialog import CreateAdminDialog
from src.services.stats_service import StatsService
from src.core.database import get_session

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Layout pour les boutons d'action
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # Bouton pour créer un administrateur
        self.create_admin_button = QPushButton("Créer un administrateur")
        self.create_admin_button.clicked.connect(self.create_admin)
        header_layout.addWidget(self.create_admin_button)
        
        # Bouton de rafraîchissement
        self.refresh_button = QPushButton("Rafraîchir tout")
        self.refresh_button.clicked.connect(self.refresh_all)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Créer le widget d'onglets
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Initialiser les onglets
        self.setup_tabs()
        
        # Raccourci clavier pour le rafraîchissement (Ctrl+R)
        self.refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self.tab_widget)
        self.refresh_shortcut.activated.connect(self.refresh_all)
        
    def create_shortcut(self, key_sequence, callback):
        """Crée un raccourci clavier
        Args:
            key_sequence: La combinaison de touches (Qt.Key)
            callback: La fonction à appeler quand le raccourci est activé
        Returns:
            QShortcut: Le raccourci créé
        """
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(callback)
        return shortcut
    
    def setup_tabs(self):
        """Initialise les différents onglets de l'interface"""
        # Onglet des matchs
        self.match_widget = MatchWidget()
        self.tab_widget.addTab(self.match_widget, "Matchs")
        
        # Onglet des tournois
        self.tournament_widget = TournamentWidget()
        self.tab_widget.addTab(self.tournament_widget, "Tournois")
        
        # Onglet des équipes
        self.team_widget = TeamWidget()
        self.tab_widget.addTab(self.team_widget, "Équipes et joueurs")
        
        # Onglet des écoles
        self.school_widget = SchoolWidget()
        self.tab_widget.addTab(self.school_widget, "Écoles")
        
        # Onglet des logs
        session = get_session()
        stats_service = StatsService(session)
        self.logs_widget = LogsWidget(stats_service=stats_service)
        self.tab_widget.addTab(self.logs_widget, "Logs")
        
        # TODO: Ajouter les autres onglets:
        # - Utilisateurs

    def refresh_all(self):
        """Rafraîchit tous les widgets"""
        self.tournament_widget.load_data()
        self.team_widget.load_data()
        self.match_widget.load_data()
        self.school_widget.load_data()
        # Pas besoin de rafraîchir les logs pour l'instant car ils sont vides

    def create_admin(self):
        """Ouvre le dialogue de création d'administrateur"""
        dialog = CreateAdminDialog(self)
        dialog.exec()
