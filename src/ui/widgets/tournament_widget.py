from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QTabWidget, QLabel, QHeaderView,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateTimeEdit, QFormLayout,
                             QMessageBox)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from ...services.activity_service import ActivityService
from ...core.database import SessionLocal
from ...models.base import Tournament, Team, TournamentTeam
from datetime import datetime

class TournamentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SessionLocal()
        self.activity_service = ActivityService(self.db)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Créer les onglets
        self.tabs = QTabWidget()
        
        # Onglet des inscriptions aux tournois
        registrations_widget = QWidget()
        registrations_layout = QVBoxLayout(registrations_widget)
        
        # Boutons d'action pour les inscriptions
        reg_actions_layout = QHBoxLayout()
        self.delete_registration_button = QPushButton("Supprimer l'inscription")
        self.delete_registration_button.setStyleSheet("background-color: #d9534f; color: white;")
        reg_actions_layout.addStretch()
        reg_actions_layout.addWidget(self.delete_registration_button)
        registrations_layout.addLayout(reg_actions_layout)
        
        self.registrations_table = self.create_table(
            ["Date", "Tournoi", "Équipe", "Statut"]
        )
        registrations_layout.addWidget(self.registrations_table)
        registrations_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(registrations_widget, "Inscriptions aux tournois")
        
        # Onglet des places disponibles
        available_slots_widget = QWidget()
        available_slots_layout = QVBoxLayout(available_slots_widget)
        
        self.slots_table = self.create_table(
            ["Tournoi", "Places max", "Places prises", "Places restantes"]
        )
        available_slots_layout.addWidget(self.slots_table)
        available_slots_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(available_slots_widget, "Places disponibles")
        
        # Onglet de gestion des tournois
        manage_tournaments_widget = QWidget()
        manage_tournaments_layout = QVBoxLayout(manage_tournaments_widget)
        
        # Boutons d'action pour les tournois
        tourn_actions_layout = QHBoxLayout()
        self.delete_tournament_button = QPushButton("Supprimer le tournoi")
        self.delete_tournament_button.setStyleSheet("background-color: #d9534f; color: white;")
        tourn_actions_layout.addStretch()
        tourn_actions_layout.addWidget(self.delete_tournament_button)
        manage_tournaments_layout.addLayout(tourn_actions_layout)
        
        # Table des tournois
        self.tournaments_table = self.create_table(
            ["ID", "Nom", "Jeu", "Date de début", "Status"]
        )
        manage_tournaments_layout.addWidget(self.tournaments_table)
        manage_tournaments_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(manage_tournaments_widget, "Gérer les tournois")
        
        # Onglet de création de tournoi
        create_tournament_widget = QWidget()
        create_tournament_layout = QFormLayout(create_tournament_widget)
        
        # Champs du formulaire
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Nom du tournoi")
        
        self.game_edit = QLineEdit()
        self.game_edit.setPlaceholderText("Jeu")
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Description du tournoi")
        self.description_edit.setMinimumHeight(100)
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("elimination")
        self.format_combo.setCurrentText("elimination")
        
        self.max_players_spin = QSpinBox()
        self.max_players_spin.setMinimum(2)
        self.max_players_spin.setMaximum(64)
        self.max_players_spin.setValue(8)
        
        self.players_per_team_spin = QSpinBox()
        self.players_per_team_spin.setMinimum(1)
        self.players_per_team_spin.setMaximum(10)
        self.players_per_team_spin.setValue(5)
        
        self.start_date_edit = QDateTimeEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateTime(QDateTime.currentDateTime())
        
        # Bouton de création
        self.create_button = QPushButton("Créer le tournoi")
        self.create_button.clicked.connect(self.create_tournament)
        
        # Ajouter les champs au layout
        create_tournament_layout.addRow("Nom*:", self.title_edit)
        create_tournament_layout.addRow("Jeu*:", self.game_edit)
        create_tournament_layout.addRow("Description*:", self.description_edit)
        create_tournament_layout.addRow("Format:", self.format_combo)
        create_tournament_layout.addRow("Nombre max d'équipes*:", self.max_players_spin)
        create_tournament_layout.addRow("Joueurs par équipe*:", self.players_per_team_spin)
        create_tournament_layout.addRow("Date de début*:", self.start_date_edit)
        create_tournament_layout.addRow(self.create_button)
        
        # Ajouter l'onglet
        self.tabs.addTab(create_tournament_widget, "Créer un tournoi")
        
        # Ajouter les onglets au layout principal
        layout.addWidget(self.tabs)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Connexions
        self.delete_registration_button.clicked.connect(self.delete_registration)
        self.delete_tournament_button.clicked.connect(self.delete_tournament)
        
    def create_table(self, headers):
        """Crée une table avec les en-têtes spécifiés"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        
        # Faire en sorte que la table prenne tout l'espace disponible
        table.horizontalHeader().setStretchLastSection(False)
        table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        
        header = table.horizontalHeader()
        
        # Ajustements spécifiques pour la table des inscriptions
        if "Statut" in headers:
            # Par défaut, toutes les colonnes sont en mode Fixed
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            
            # La colonne Tournoi est en mode Stretch
            tournament_column = headers.index("Tournoi")
            header.setSectionResizeMode(tournament_column, QHeaderView.ResizeMode.Stretch)
            
            # Définir les largeurs fixes
            date_column = headers.index("Date")
            status_column = headers.index("Statut")
            table.setColumnWidth(date_column, 130)
            table.setColumnWidth(status_column, 80)
            
        # Ajustements spécifiques pour la table des places disponibles
        elif "Places max" in headers:
            # Par défaut, toutes les colonnes sont en mode Fixed
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            
            # La colonne Tournoi est en mode Stretch
            tournament_column = headers.index("Tournoi")
            header.setSectionResizeMode(tournament_column, QHeaderView.ResizeMode.Stretch)
            
            # Définir les largeurs fixes pour les colonnes de places
            table.setColumnWidth(1, 100)  # Places max
            table.setColumnWidth(2, 100)  # Places prises
            table.setColumnWidth(3, 100)  # Places restantes
            
        # Ajustements spécifiques pour la table des tournois
        elif "Actions" not in headers:
            # Par défaut, toutes les colonnes sont en mode Fixed
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            
            # La colonne Nom est en mode Stretch
            name_column = headers.index("Nom")
            header.setSectionResizeMode(name_column, QHeaderView.ResizeMode.Stretch)
            
            # Définir les largeurs fixes
            id_column = headers.index("ID")
            game_column = headers.index("Jeu")
            start_date_column = headers.index("Date de début")
            status_column = headers.index("Status")
            table.setColumnWidth(id_column, 50)
            table.setColumnWidth(game_column, 100)
            table.setColumnWidth(start_date_column, 150)
            table.setColumnWidth(status_column, 80)
            
        return table
    
    def load_data(self):
        """Charge les données des tournois"""
        self.load_registrations()
        self.load_slots()
        self.load_tournaments()
        
    def load_registrations(self):
        """Charge les inscriptions aux tournois"""
        registrations = self.activity_service.get_tournament_registrations()
        self.registrations_table.setRowCount(0)
        
        for row, registration in enumerate(registrations):
            self.registrations_table.insertRow(row)
            
            # Formatage de la date
            date_str = registration.registered_at.strftime("%Y-%m-%d %H:%M") if registration.registered_at else "Non définie"
            
            # Récupération des informations via les relations
            tournament = registration.tournament
            team = registration.team
            
            self.registrations_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.registrations_table.setItem(row, 1, QTableWidgetItem(tournament.title))
            self.registrations_table.setItem(row, 2, QTableWidgetItem(team.name))
            self.registrations_table.setItem(row, 3, QTableWidgetItem("Inscrite"))
            
            # Stocker les IDs dans les données des items
            self.registrations_table.item(row, 1).setData(Qt.ItemDataRole.UserRole, tournament.id)
            self.registrations_table.item(row, 2).setData(Qt.ItemDataRole.UserRole, team.id)
            
    def load_slots(self):
        """Charge les places disponibles dans les tournois"""
        self.slots_table.setRowCount(0)
        tournaments = self.activity_service.get_tournament_slots()
        
        for tournament in tournaments:
            row = self.slots_table.rowCount()
            self.slots_table.insertRow(row)
            
            # Créer les items
            title_item = QTableWidgetItem(tournament['title'])
            max_players_item = QTableWidgetItem(str(tournament['max_players']))
            registered_players_item = QTableWidgetItem(str(tournament['registered_players']))
            available_slots_item = QTableWidgetItem(str(tournament['available_slots']))
            
            # Définir les items dans la table
            self.slots_table.setItem(row, 0, title_item)
            self.slots_table.setItem(row, 1, max_players_item)
            self.slots_table.setItem(row, 2, registered_players_item)
            self.slots_table.setItem(row, 3, available_slots_item)
            
            # Si plus de places disponibles, colorer la ligne en vert
            if tournament['available_slots'] == 0:
                green_color = QColor(144, 238, 144)  # Vert clair
                for col in range(4):
                    self.slots_table.item(row, col).setBackground(green_color)
                    
    def load_tournaments(self):
        """Charge la liste des tournois"""
        tournaments = self.db.query(Tournament).order_by(Tournament.start_date.desc()).all()
        self.tournaments_table.setRowCount(0)
        
        for row, tournament in enumerate(tournaments):
            self.tournaments_table.insertRow(row)
            
            # Formatage de la date
            date_str = tournament.start_date.strftime("%Y-%m-%d %H:%M") if tournament.start_date else "Non définie"
            
            self.tournaments_table.setItem(row, 0, QTableWidgetItem(str(tournament.id)))
            self.tournaments_table.setItem(row, 1, QTableWidgetItem(tournament.title))
            self.tournaments_table.setItem(row, 2, QTableWidgetItem(tournament.game))
            self.tournaments_table.setItem(row, 3, QTableWidgetItem(date_str))
            self.tournaments_table.setItem(row, 4, QTableWidgetItem(tournament.status))
            
    def create_tournament(self):
        """Crée un nouveau tournoi avec les données du formulaire"""
        # Vérifier chaque champ obligatoire
        missing_fields = []
        
        if not self.title_edit.text().strip():
            missing_fields.append("Nom du tournoi")
            
        if not self.game_edit.text().strip():
            missing_fields.append("Jeu")
            
        if not self.description_edit.toPlainText().strip():
            missing_fields.append("Description")
            
        if self.max_players_spin.value() < 2:
            missing_fields.append("Nombre max d'équipes (minimum 2)")
            
        if self.players_per_team_spin.value() < 1:
            missing_fields.append("Joueurs par équipe (minimum 1)")
            
        # Si des champs sont manquants, afficher un message d'erreur
        if missing_fields:
            error_message = "Les champs suivants sont obligatoires :\n- " + "\n- ".join(missing_fields)
            QMessageBox.warning(self, "Champs manquants", error_message)
            return
            
        try:
            # Créer le nouveau tournoi
            tournament = Tournament(
                title=self.title_edit.text().strip(),
                game=self.game_edit.text().strip(),
                description=self.description_edit.toPlainText().strip(),
                format=self.format_combo.currentText(),
                max_players=self.max_players_spin.value(),
                players_per_team=self.players_per_team_spin.value(),
                start_date=self.start_date_edit.dateTime().toPyDateTime(),
                status="PENDING",
                is_online=True,  # Par défaut en ligne
                creator_id=1  # TODO: Utiliser l'ID de l'utilisateur connecté
            )
            
            # Ajouter à la base de données
            self.db.add(tournament)
            self.db.commit()
            
            # Réinitialiser le formulaire
            self.title_edit.clear()
            self.game_edit.clear()
            self.description_edit.clear()
            self.max_players_spin.setValue(8)
            self.players_per_team_spin.setValue(5)
            self.start_date_edit.setDateTime(QDateTime.currentDateTime())
            
            # Rafraîchir les données
            self.load_data()
            
            QMessageBox.information(self, "Succès", "Le tournoi a été créé avec succès!")
            
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue lors de la création du tournoi : {str(e)}")
            
    def delete_registration(self):
        """Supprime une inscription au tournoi"""
        # Vérifier qu'une inscription est sélectionnée
        selected_items = self.registrations_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une inscription")
            return
            
        # Récupérer les informations de l'inscription
        row = self.registrations_table.currentRow()
        tournament_id = self.registrations_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
        team_id = self.registrations_table.item(row, 2).data(Qt.ItemDataRole.UserRole)
        tournament_name = self.registrations_table.item(row, 1).text()
        team_name = self.registrations_table.item(row, 2).text()
        
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer l'inscription de l'équipe {team_name} au tournoi {tournament_name} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Supprimer l'inscription directement avec les IDs
                tournament_team = self.db.query(TournamentTeam).filter(
                    TournamentTeam.tournament_id == tournament_id,
                    TournamentTeam.team_id == team_id
                ).first()
                
                if tournament_team:
                    self.db.delete(tournament_team)
                    self.db.commit()
                    
                    # Rafraîchir les données
                    self.load_data()
                    
                    QMessageBox.information(self, "Succès", "L'inscription a été supprimée avec succès!")
                else:
                    raise ValueError("Inscription non trouvée")
                    
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")
                
    def delete_tournament(self):
        """Supprime un tournoi"""
        # Vérifier qu'un tournoi est sélectionné
        selected_items = self.tournaments_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un tournoi")
            return
            
        tournament_id = int(selected_items[0].text())
        tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            QMessageBox.critical(self, "Erreur", "Tournoi non trouvé.")
            return
            
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer le tournoi '{tournament.title}' ?\n\n"
            "ATTENTION : Cette action supprimera également toutes les inscriptions associées.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Supprimer d'abord les inscriptions
                self.db.query(TournamentTeam).filter(TournamentTeam.tournament_id == tournament_id).delete()
                
                # Puis supprimer le tournoi
                self.db.delete(tournament)
                self.db.commit()
                
                # Rafraîchir les données
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Le tournoi a été supprimé avec succès!")
                
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")
                
    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture du widget"""
        self.db.close()
        super().closeEvent(event)
