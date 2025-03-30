from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QTabWidget, QDialog, QFormLayout, QComboBox, QSpinBox,
    QDateTimeEdit, QMessageBox, QLabel, QLineEdit
)
from PyQt6.QtCore import QDateTime

from ...services.match_service import MatchService
from ...services.activity_service import ActivityService
from ...core.database import SessionLocal
from ...models.base import Match, Tournament, Team, TournamentTeam
from datetime import datetime

class CreateMatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer un nouveau match")
        self.db = SessionLocal()
        self.match_service = MatchService(self.db)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Sélection du tournoi
        self.tournament_combo = QComboBox()
        self.tournament_combo.currentIndexChanged.connect(self.on_tournament_changed)
        layout.addRow("Tournoi:", self.tournament_combo)
        
        # Sélection des équipes
        self.team1_combo = QComboBox()
        self.team2_combo = QComboBox()
        layout.addRow("Équipe 1:", self.team1_combo)
        layout.addRow("Équipe 2:", self.team2_combo)
        
        # Round
        self.round_spin = QSpinBox()
        self.round_spin.setMinimum(1)
        layout.addRow("Round:", self.round_spin)
        
        # Date et heure prévues
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        layout.addRow("Date et heure:", self.datetime_edit)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Créer")
        self.cancel_button = QPushButton("Annuler")
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addRow(buttons_layout)
        
        # Connexions
        self.create_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def load_data(self):
        """Charge les données dans les combos"""
        try:
            # Charger les tournois actifs
            tournaments = self.db.query(Tournament)\
                .order_by(Tournament.start_date.desc())\
                .all()
            
            self.tournament_combo.clear()
            for tournament in tournaments:
                self.tournament_combo.addItem(tournament.title, tournament.id)
            
            # Mettre à jour les équipes si un tournoi est sélectionné
            if self.tournament_combo.count() > 0:
                self.on_tournament_changed()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données : {str(e)}")
            
    def on_tournament_changed(self):
        """Met à jour les équipes quand le tournoi change"""
        try:
            tournament_id = self.tournament_combo.currentData()
            if tournament_id is None:
                return
            
            # Récupérer uniquement les équipes inscrites au tournoi
            teams = self.db.query(Team)\
                .join(TournamentTeam, Team.id == TournamentTeam.team_id)\
                .filter(TournamentTeam.tournament_id == tournament_id)\
                .order_by(Team.name)\
                .all()
            
            # Mettre à jour les combos d'équipes
            self.team1_combo.clear()
            self.team2_combo.clear()
            
            for team in teams:
                self.team1_combo.addItem(team.name, team.id)
                self.team2_combo.addItem(team.name, team.id)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour des équipes : {str(e)}")
            
    def get_data(self):
        """Récupère les données du formulaire"""
        return {
            'tournament_id': self.tournament_combo.currentData(),
            'team1_id': self.team1_combo.currentData(),
            'team2_id': self.team2_combo.currentData(),
            'round': self.round_spin.value(),
            'scheduled_time': self.datetime_edit.dateTime().toPyDateTime()
        }
        
    def closeEvent(self, event):
        """Ferme la connexion à la base de données"""
        self.db.close()
        event.accept()

class UpdateScoreDialog(QDialog):
    def __init__(self, match, parent=None):
        super().__init__(parent)
        self.match = match
        self.db = SessionLocal()
        self.match_service = MatchService(self.db)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Mettre à jour le score")
        layout = QFormLayout(self)
        
        # Informations du match
        layout.addRow(QLabel(f"Tournoi: {self.match.tournament.title}"))
        layout.addRow(QLabel(f"Round: {self.match.round}"))
        
        # Score
        score_layout = QHBoxLayout()
        self.team1_score = QSpinBox()
        self.team2_score = QSpinBox()
        self.team1_score.setMinimum(0)
        self.team2_score.setMinimum(0)
        
        score_layout.addWidget(QLabel(self.match.team1.name))
        score_layout.addWidget(self.team1_score)
        score_layout.addWidget(QLabel(" - "))
        score_layout.addWidget(self.team2_score)
        score_layout.addWidget(QLabel(self.match.team2.name))
        
        layout.addRow("Score:", score_layout)
        
        # Vainqueur
        self.winner_combo = QComboBox()
        self.winner_combo.addItem("Sélectionner le vainqueur", None)
        self.winner_combo.addItem(self.match.team1.name, self.match.team1.id)
        self.winner_combo.addItem(self.match.team2.name, self.match.team2.id)
        layout.addRow("Vainqueur:", self.winner_combo)
        
        # Boutons
        buttons = QHBoxLayout()
        self.save_button = QPushButton("Enregistrer")
        self.cancel_button = QPushButton("Annuler")
        
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)
        layout.addRow(buttons)
        
        # Connexions
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Si le match a déjà un score, le charger
        if self.match.score:
            try:
                team1_score, team2_score = map(int, self.match.score.split('-'))
                self.team1_score.setValue(team1_score)
                self.team2_score.setValue(team2_score)
            except:
                pass
                
        # Si le match a déjà un vainqueur, le sélectionner
        if self.match.winner_id:
            index = self.winner_combo.findData(self.match.winner_id)
            if index >= 0:
                self.winner_combo.setCurrentIndex(index)
                
    def get_data(self):
        """Récupère les données du formulaire"""
        return {
            'score': f"{self.team1_score.value()}-{self.team2_score.value()}",
            'winner_id': self.winner_combo.currentData(),
            'status': "COMPLETED" if self.winner_combo.currentData() else "IN_PROGRESS"
        }
        
    def closeEvent(self, event):
        """Ferme la connexion à la base de données"""
        self.db.close()
        event.accept()

class MatchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SessionLocal()
        self.match_service = MatchService(self.db)
        self.activity_service = ActivityService(self.db)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Création des onglets
        self.tabs = QTabWidget()
        
        # Onglet des matchs en cours
        self.current_matches_widget = QWidget()
        current_matches_layout = QVBoxLayout(self.current_matches_widget)
        
        # Boutons d'action pour les matchs en cours
        actions_layout = QHBoxLayout()
        
        # Groupe des boutons principaux à gauche
        left_buttons = QHBoxLayout()
        self.create_match_button = QPushButton("Créer un match")
        self.update_score_button = QPushButton("Mettre à jour le score")
        left_buttons.addWidget(self.create_match_button)
        left_buttons.addWidget(self.update_score_button)
        
        # Bouton de suppression à droite
        self.delete_match_button = QPushButton("Supprimer le match")
        self.delete_match_button.setStyleSheet("background-color: #d9534f; color: white;")
        
        actions_layout.addLayout(left_buttons)
        actions_layout.addStretch()
        actions_layout.addWidget(self.delete_match_button)
        
        # Table des matchs en cours
        self.matches_table = self.create_table(
            ["ID", "Tournoi", "Round", "Équipe 1", "Équipe 2", "Score", "Statut", "Date prévue"]
        )
        
        current_matches_layout.addLayout(actions_layout)
        current_matches_layout.addWidget(self.matches_table)
        
        self.tabs.addTab(self.current_matches_widget, "Matchs")
        
        # Onglet de l'historique des matchs
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        self.match_history_table = self.create_table(
            ["Date", "Tournoi", "Équipe 1", "Équipe 2", "Score", "Statut", "Vainqueur"]
        )
        history_layout.addWidget(self.match_history_table)
        
        self.tabs.addTab(history_widget, "Historique des matchs")
        
        # Ajout des onglets au layout principal
        layout.addWidget(self.tabs)
        
        # Connexions
        self.create_match_button.clicked.connect(self.create_match)
        self.update_score_button.clicked.connect(self.update_match_score)
        self.delete_match_button.clicked.connect(self.delete_match)
        
    def create_table(self, headers):
        """Crée une table avec les en-têtes spécifiés"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        return table
    
    def load_data(self):
        """Charge toutes les données"""
        self.load_matches()
        self.load_match_history()
        
    def load_matches(self):
        """Charge les matchs dans la table"""
        try:
            self.matches_table.setRowCount(0)
            matches = self.match_service.get_current_matches()
            
            for match in matches:
                row = self.matches_table.rowCount()
                self.matches_table.insertRow(row)
                self.matches_table.setItem(row, 0, QTableWidgetItem(str(match.id)))
                self.matches_table.setItem(row, 1, QTableWidgetItem(match.tournament.title))
                self.matches_table.setItem(row, 2, QTableWidgetItem(str(match.round)))
                self.matches_table.setItem(row, 3, QTableWidgetItem(match.team1.name))
                self.matches_table.setItem(row, 4, QTableWidgetItem(match.team2.name))
                self.matches_table.setItem(row, 5, QTableWidgetItem(match.score or ""))
                self.matches_table.setItem(row, 6, QTableWidgetItem(match.status))
                self.matches_table.setItem(row, 7, QTableWidgetItem(
                    match.scheduled_time.strftime("%d/%m/%Y %H:%M") if match.scheduled_time else "Non définie"
                ))
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des matchs : {str(e)}")
            
    def load_match_history(self):
        """Charge l'historique des matchs"""
        try:
            self.match_history_table.setRowCount(0)
            matches = self.activity_service.get_match_history()
            
            for match in matches:
                row = self.match_history_table.rowCount()
                self.match_history_table.insertRow(row)
                self.match_history_table.setItem(row, 0, QTableWidgetItem(
                    match.completed_time.strftime("%d/%m/%Y %H:%M") if match.completed_time else "Non définie"
                ))
                self.match_history_table.setItem(row, 1, QTableWidgetItem(match.tournament.title))
                self.match_history_table.setItem(row, 2, QTableWidgetItem(match.team1.name))
                self.match_history_table.setItem(row, 3, QTableWidgetItem(match.team2.name))
                self.match_history_table.setItem(row, 4, QTableWidgetItem(match.score or ""))
                self.match_history_table.setItem(row, 5, QTableWidgetItem(match.status))
                self.match_history_table.setItem(row, 6, QTableWidgetItem(match.winner_name))
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de l'historique des matchs : {str(e)}")
            
    def create_match(self):
        """Ouvre le dialogue de création de match"""
        dialog = CreateMatchDialog(self)
        if dialog.exec():
            try:
                data = dialog.get_data()
                # Vérifier que deux équipes différentes sont sélectionnées
                if data['team1_id'] == data['team2_id']:
                    QMessageBox.warning(self, "Erreur", "Les deux équipes doivent être différentes")
                    return
                    
                # Créer le match
                self.match_service.create_match(
                    tournament_id=data['tournament_id'],
                    team1_id=data['team1_id'],
                    team2_id=data['team2_id'],
                    round=data['round'],
                    scheduled_time=data['scheduled_time']
                )
                
                # Rafraîchir les données
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le match : {str(e)}")
            
    def update_match_score(self):
        """Met à jour le score du match sélectionné"""
        # Vérifier qu'un match est sélectionné
        selected_items = self.matches_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un match")
            return
            
        match_id = int(selected_items[0].text())
        match = self.match_service.get_match(match_id)
        
        dialog = UpdateScoreDialog(match, self)
        if dialog.exec():
            try:
                data = dialog.get_data()
                
                # Demander confirmation
                confirmation_message = f"Êtes-vous sûr de vouloir mettre à jour le score ?\n\n"
                confirmation_message += f"Score : {data['score']}\n"
                if data['winner_id']:
                    winner = match.team1 if data['winner_id'] == match.team1.id else match.team2
                    confirmation_message += f"Vainqueur : {winner.name}"
                
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    confirmation_message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.match_service.update_match_score(match_id, data['score'], data['winner_id'], data['status'])
                    # Rafraîchir les données
                    self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de mettre à jour le score : {str(e)}")
            
    def delete_match(self):
        """Supprime le match sélectionné"""
        # Vérifier qu'un match est sélectionné
        selected_items = self.matches_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un match")
            return
            
        match_id = int(selected_items[0].text())
        
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce match ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.match_service.delete_match(match_id)
                
                # Rafraîchir les données
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le match : {str(e)}")
            
    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture du widget"""
        self.db.close()
        super().closeEvent(event)
