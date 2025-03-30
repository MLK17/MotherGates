from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from ...core.database import SessionLocal
from ...services.activity_service import ActivityService
from ...services.user_service import UserService
from ...models.base import Team, TeamMember, TournamentTeam, TeamJoinRequest, User

class TeamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.activity_service = ActivityService(self.db)
        self.user_service = UserService(self.db)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Création des onglets
        self.tabs = QTabWidget()
        
        # Onglet des nouvelles équipes
        new_teams_widget = QWidget()
        new_teams_layout = QVBoxLayout(new_teams_widget)
        
        # Actions pour les équipes
        actions_layout = QHBoxLayout()
        
        # Bouton de suppression à droite
        self.delete_team_button = QPushButton("Supprimer l'équipe")
        self.delete_team_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_team_button.clicked.connect(self.delete_team)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.delete_team_button)
        new_teams_layout.addLayout(actions_layout)
        
        # Table des équipes
        self.new_teams_table = QTableWidget()
        self.new_teams_table.setColumnCount(5)
        self.new_teams_table.setHorizontalHeaderLabels([
            "Date de création", "Nom", "Capitaine", "École", "Statut"
        ])
        # Configuration en lecture seule
        self.new_teams_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Sélection par ligne
        self.new_teams_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.new_teams_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        # Couleurs alternées
        self.new_teams_table.setAlternatingRowColors(True)
        
        # Définir des largeurs proportionnelles pour chaque colonne
        header = self.new_teams_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Nom
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # Capitaine
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)      # École
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Statut
        # Largeurs minimales
        self.new_teams_table.setColumnWidth(0, 150)  # Date
        self.new_teams_table.setColumnWidth(4, 100)  # Statut
        new_teams_layout.addWidget(self.new_teams_table)
        
        # Onglet des joueurs
        players_widget = QWidget()
        players_layout = QVBoxLayout(players_widget)
        
        # Actions pour les joueurs
        actions_layout = QHBoxLayout()
        
        # Bouton de suppression à droite
        self.delete_player_button = QPushButton("Supprimer le joueur")
        self.delete_player_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_player_button.clicked.connect(self.delete_player)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.delete_player_button)
        players_layout.addLayout(actions_layout)
        
        # Filtres
        filters_layout = QHBoxLayout()
        
        # Recherche pseudo/email
        search_layout = QHBoxLayout()
        search_label = QLabel("Rechercher:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Pseudo ou email...")
        self.search_edit.textChanged.connect(self.filter_players)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        filters_layout.addLayout(search_layout)
        
        # Filtre par école
        school_layout = QHBoxLayout()
        school_label = QLabel("École:")
        self.school_combo = QComboBox()
        self.school_combo.currentIndexChanged.connect(self.filter_players)
        school_layout.addWidget(school_label)
        school_layout.addWidget(self.school_combo)
        filters_layout.addLayout(school_layout)

        # Filtre par équipe
        team_layout = QHBoxLayout()
        team_label = QLabel("Équipe:")
        self.team_combo = QComboBox()
        self.team_combo.currentIndexChanged.connect(self.filter_players)
        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_combo)
        filters_layout.addLayout(team_layout)

        # Filtre par date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date depuis:")
        self.date_combo = QComboBox()
        self.date_combo.addItems(["Tout", "Aujourd'hui", "7 derniers jours", "30 derniers jours", "Cette année"])
        self.date_combo.currentIndexChanged.connect(self.filter_players)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_combo)
        filters_layout.addLayout(date_layout)
        
        players_layout.addLayout(filters_layout)
        
        # Table des joueurs
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(5)  # Ajout d'une colonne pour la date
        self.players_table.setHorizontalHeaderLabels([
            "Date de création", "Pseudo", "Email", "École(s)", "Équipe(s)"
        ])
        # Configuration en lecture seule
        self.players_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Sélection par ligne
        self.players_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.players_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        # Couleurs alternées
        self.players_table.setAlternatingRowColors(True)
        
        # Définir des largeurs proportionnelles pour chaque colonne
        header = self.players_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Pseudo
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # Email
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)      # École(s)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)      # Équipe(s)
        # Largeur minimale pour la date
        self.players_table.setColumnWidth(0, 150)
        players_layout.addWidget(self.players_table)
        
        # Ajout des onglets
        self.tabs.addTab(new_teams_widget, "Équipes")
        self.tabs.addTab(players_widget, "Joueurs")
        
        layout.addWidget(self.tabs)
        
    def load_data(self):
        """Charge les données dans les tableaux"""
        self.load_new_teams()
        self.load_schools()
        self.load_teams()
        self.filter_players()
        
    def load_new_teams(self):
        """Charge les nouvelles équipes"""
        teams = self.activity_service.get_new_teams()
        self.new_teams_table.setRowCount(0)
        
        for row, team in enumerate(teams):
            self.new_teams_table.insertRow(row)
            
            # Formatage de la date
            date_str = team.created_at.strftime("%Y-%m-%d %H:%M") if team.created_at else "Non définie"
            
            # Stocker l'ID de l'équipe dans la première colonne (invisible)
            id_item = QTableWidgetItem(str(team.id))
            self.new_teams_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.new_teams_table.setItem(row, 1, QTableWidgetItem(team.name))
            self.new_teams_table.setItem(row, 2, QTableWidgetItem(team.captain.pseudo))
            self.new_teams_table.setItem(row, 3, QTableWidgetItem(team.school.name if team.school else "Sans école"))
            self.new_teams_table.setItem(row, 4, QTableWidgetItem("Active"))
            
    def load_schools(self):
        """Charge la liste des écoles dans le combo"""
        self.school_combo.clear()
        self.school_combo.addItem("Toutes les écoles")
        self.school_combo.addItem("Sans école", "no_school")
        schools = self.user_service.get_all_schools()
        for school in schools:
            self.school_combo.addItem(school.name, school.id)

    def load_teams(self):
        """Charge la liste des équipes dans le combo"""
        self.team_combo.clear()
        self.team_combo.addItem("Toutes les équipes")
        self.team_combo.addItem("Sans équipe", "no_team")
        teams = self.user_service.get_all_teams()
        for team in teams:
            self.team_combo.addItem(team.name, team.id)

    def filter_players(self):
        """Filtre et affiche les joueurs selon les critères"""
        search_text = self.search_edit.text().lower()
        school_id = self.school_combo.currentData()
        team_id = self.team_combo.currentData()
        date_filter = self.date_combo.currentText()

        # Récupérer tous les utilisateurs avec leurs relations
        users = self.user_service.get_all_users_with_relations()
        
        # Appliquer les filtres
        filtered_users = []
        for user in users:
            # Filtre de recherche
            if search_text and search_text not in user.pseudo.lower() and search_text not in (user.email or "").lower():
                continue
                
            # Filtre d'école
            if school_id:
                user_schools = set(member.team.school.id for member in user.team_memberships)
                if school_id == "no_school":
                    if user_schools:  # Si l'utilisateur a des écoles, on le skip
                        continue
                elif school_id not in user_schools:
                    continue
                
            # Filtre d'équipe
            if team_id:
                user_teams = set(member.team.id for member in user.team_memberships)
                if team_id == "no_team":
                    if user_teams:  # Si l'utilisateur a des équipes, on le skip
                        continue
                elif team_id not in user_teams:
                    continue
                
            # Filtre de date
            if date_filter != "Tout":
                from datetime import datetime, timedelta
                now = datetime.now()
                created_at = user.created_at
                
                if date_filter == "Aujourd'hui" and created_at.date() != now.date():
                    continue
                elif date_filter == "7 derniers jours" and (now - created_at) > timedelta(days=7):
                    continue
                elif date_filter == "30 derniers jours" and (now - created_at) > timedelta(days=30):
                    continue
                elif date_filter == "Cette année" and created_at.year != now.year:
                    continue
                    
            filtered_users.append(user)

        # Mettre à jour le tableau
        self.players_table.setRowCount(len(filtered_users))
        for row, user in enumerate(filtered_users):
            # Date de création
            date_item = QTableWidgetItem(user.created_at.strftime("%d/%m/%Y %H:%M"))
            self.players_table.setItem(row, 0, date_item)
            
            # Pseudo
            pseudo_item = QTableWidgetItem(user.pseudo)
            self.players_table.setItem(row, 1, pseudo_item)
            
            # Email
            email_item = QTableWidgetItem(user.email or "")
            self.players_table.setItem(row, 2, email_item)
            
            # Écoles
            schools = set(member.team.school.name for member in user.team_memberships)
            schools_text = ", ".join(schools) if schools else "Sans école"
            schools_item = QTableWidgetItem(schools_text)
            self.players_table.setItem(row, 3, schools_item)
            
            # Équipes
            teams = set(member.team.name for member in user.team_memberships)
            teams_text = ", ".join(teams) if teams else "Sans équipe"
            teams_item = QTableWidgetItem(teams_text)
            self.players_table.setItem(row, 4, teams_item)

    def delete_team(self):
        """Supprime l'équipe sélectionnée"""
        from ...models.base import Team, TeamMember, TournamentTeam, TeamJoinRequest
        
        # Vérifier qu'une équipe est sélectionnée
        selected_items = self.new_teams_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une équipe")
            return
            
        # Récupérer les informations de l'équipe sélectionnée
        row = self.new_teams_table.row(selected_items[0])
        team_name = self.new_teams_table.item(row, 1).text()
        
        # Récupérer l'équipe depuis la base de données
        team = self.db.query(Team).filter(Team.name == team_name).first()
        if not team:
            QMessageBox.critical(self, "Erreur", "Équipe non trouvée.")
            return
            
        # Vérifier s'il y a des demandes en attente
        pending_requests = self.db.query(TeamJoinRequest)\
            .filter(TeamJoinRequest.team_id == team.id)\
            .filter(TeamJoinRequest.status == "PENDING")\
            .count()
            
        if pending_requests > 0:
            reply = QMessageBox.question(
                self,
                "Attention",
                f"L'équipe '{team.name}' a {pending_requests} demande(s) d'adhésion en attente.\n"
                "Voulez-vous quand même la supprimer ?\n\n"
                "ATTENTION : Cette action supprimera également :\n"
                "- Tous les membres de l'équipe\n"
                "- Toutes les inscriptions aux tournois\n"
                "- Toutes les demandes de rejoindre l'équipe (y compris celles en attente)\n"
                "Cette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Voulez-vous vraiment supprimer l'équipe '{team.name}' ?\n\n"
                "ATTENTION : Cette action supprimera également :\n"
                "- Tous les membres de l'équipe\n"
                "- Toutes les inscriptions aux tournois\n"
                "- Toutes les demandes de rejoindre l'équipe\n"
                "Cette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Supprimer les inscriptions aux tournois
                self.db.query(TournamentTeam).filter(TournamentTeam.team_id == team.id).delete()
                
                # Supprimer les demandes de rejoindre l'équipe
                self.db.query(TeamJoinRequest).filter(TeamJoinRequest.team_id == team.id).delete()
                
                # Supprimer les membres de l'équipe
                self.db.query(TeamMember).filter(TeamMember.team_id == team.id).delete()
                
                # Supprimer l'équipe
                self.db.delete(team)
                self.db.commit()
                
                # Rafraîchir les données
                self.load_data()
                
                QMessageBox.information(self, "Succès", "L'équipe a été supprimée avec succès!")
                
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def delete_player(self):
        """Supprime le joueur sélectionné"""
        from ...models.base import User, TeamMember, TeamJoinRequest
        
        # Vérifier qu'un joueur est sélectionné
        selected_items = self.players_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un joueur")
            return
            
        # Récupérer les informations du joueur sélectionné
        row = self.players_table.row(selected_items[0])
        pseudo = self.players_table.item(row, 1).text()
        
        # Récupérer le joueur depuis la base de données
        user = self.db.query(User).filter(User.pseudo == pseudo).first()
        if not user:
            QMessageBox.critical(self, "Erreur", "Joueur non trouvé.")
            return
            
        # Vérifier s'il y a des demandes en attente
        pending_requests = self.db.query(TeamJoinRequest)\
            .filter(TeamJoinRequest.user_id == user.id)\
            .filter(TeamJoinRequest.status == "PENDING")\
            .count()
            
        if pending_requests > 0:
            reply = QMessageBox.question(
                self,
                "Attention",
                f"Le joueur '{user.pseudo}' a {pending_requests} demande(s) d'adhésion en attente.\n"
                "Voulez-vous quand même le supprimer ?\n\n"
                "ATTENTION : Cette action supprimera également :\n"
                "- Toutes ses appartenances aux équipes\n"
                "- Toutes ses demandes d'adhésion\n"
                "Cette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Voulez-vous vraiment supprimer le joueur '{user.pseudo}' ?\n\n"
                "ATTENTION : Cette action supprimera également :\n"
                "- Toutes ses appartenances aux équipes\n"
                "- Toutes ses demandes d'adhésion\n"
                "Cette action est irréversible.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Supprimer les demandes d'adhésion
                self.db.query(TeamJoinRequest).filter(TeamJoinRequest.user_id == user.id).delete()
                
                # Supprimer les appartenances aux équipes
                self.db.query(TeamMember).filter(TeamMember.user_id == user.id).delete()
                
                # Supprimer le joueur
                self.db.delete(user)
                self.db.commit()
                
                # Rafraîchir les données
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Le joueur a été supprimé avec succès!")
                
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture du widget"""
        self.db.close()
        event.accept()
