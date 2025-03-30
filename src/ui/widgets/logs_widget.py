from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QScrollArea, QSizePolicy, QGridLayout
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.services.stats_service import StatsService

class LogsWidget(QWidget):
    def __init__(self, parent=None, stats_service: StatsService = None):
        super().__init__(parent)
        self.stats_service = stats_service
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Création du widget d'onglets
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Création des sous-onglets
        self.logs_admin_tab = QWidget()
        self.stats_tab = QScrollArea()
        self.stats_content = QWidget()
        self.stats_tab.setWidget(self.stats_content)
        self.stats_tab.setWidgetResizable(True)
        
        # Définir une taille minimale pour la page de stats
        self.stats_content.setMinimumHeight(1300)

        # Ajout des sous-onglets au widget d'onglets
        self.tab_widget.addTab(self.logs_admin_tab, "Logs Admin")
        self.tab_widget.addTab(self.stats_tab, "Stats")

        # Configuration du layout pour les sous-onglets
        self.logs_admin_layout = QVBoxLayout()
        self.stats_layout = QGridLayout()
        
        self.logs_admin_tab.setLayout(self.logs_admin_layout)
        self.stats_content.setLayout(self.stats_layout)

        # Pour l'instant, le sous-onglet logs admin reste vide
        # On déplace les graphiques/diagrammes existants dans le sous-onglet Stats
        self.setup_stats_tab()

    def setup_stats_tab(self):
        if not self.stats_service:
            return

        # 1. Croissance des utilisateurs (position 0,0)
        user_growth_canvas = self.create_line_chart(
            self.stats_service.get_user_growth(),
            "Croissance des Utilisateurs",
            "",  # Label x vide
            "Nombre d'Utilisateurs"
        )
        container1 = QWidget()
        layout1 = QVBoxLayout(container1)
        layout1.setContentsMargins(0, 20, 0, 0)
        layout1.addWidget(user_growth_canvas)
        self.stats_layout.addWidget(container1, 0, 0)

        # 2. Croissance des équipes (position 0,1)
        team_growth_canvas = self.create_line_chart(
            self.stats_service.get_team_growth(),
            "Croissance des Équipes",
            "",  # Label x vide
            "Nombre d'Équipes"
        )
        container2 = QWidget()
        layout2 = QVBoxLayout(container2)
        layout2.setContentsMargins(0, 20, 0, 0)
        layout2.addWidget(team_growth_canvas)
        self.stats_layout.addWidget(container2, 0, 1)

        # 3. Joueurs par équipe (position 1,0)
        players_per_team_canvas = self.create_bar_chart(
            self.stats_service.get_players_per_team(),
            "Nombre de Joueurs par Équipe",
            "",
            "Nombre de Joueurs"
        )
        container3 = QWidget()
        layout3 = QVBoxLayout(container3)
        layout3.setContentsMargins(0, 20, 0, 0)
        layout3.addWidget(players_per_team_canvas)
        self.stats_layout.addWidget(container3, 1, 0)

        # 4. Inscriptions aux tournois par école (position 1,1)
        tournament_reg_canvas = self.create_bar_chart(
            self.stats_service.get_tournament_registrations_per_school(),
            "Inscriptions aux Tournois par École",
            "",
            "Nombre d'Inscriptions"
        )
        container4 = QWidget()
        layout4 = QVBoxLayout(container4)
        layout4.setContentsMargins(0, 20, 0, 0)
        layout4.addWidget(tournament_reg_canvas)
        self.stats_layout.addWidget(container4, 1, 1)

        # Configuration des espaces entre les graphiques
        self.stats_layout.setSpacing(0)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)

    def create_line_chart(self, data, title, xlabel, ylabel):
        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(500, 400)
        
        ax = fig.add_subplot(111)
        
        if data:
            dates, values = zip(*data)
            ax.plot(dates, values)
            ax.set_title(title, pad=15, fontsize=12)  
            ax.set_xlabel(xlabel, labelpad=10, fontsize=10)
            ax.set_ylabel(ylabel, labelpad=10, fontsize=10)
            fig.autofmt_xdate()
            ax.tick_params(axis='both', which='major', labelsize=9)
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ajustement des marges avec plus d'espace en haut
        fig.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.15, wspace=0.3, hspace=0.3)  
        return canvas

    def create_bar_chart(self, data, title, xlabel, ylabel):
        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        canvas.setMinimumSize(500, 400)
        
        ax = fig.add_subplot(111)
        
        if data:
            labels, values = zip(*data)
            ax.bar(labels, values)
            ax.set_title(title, pad=15, fontsize=12)  
            ax.set_xlabel(xlabel, labelpad=10, fontsize=10)
            ax.set_ylabel(ylabel, labelpad=10, fontsize=10)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
            ax.tick_params(axis='y', which='major', labelsize=9)
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Ajustement des marges avec plus d'espace en haut
        fig.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.2, wspace=0.3, hspace=0.3)  
        return canvas