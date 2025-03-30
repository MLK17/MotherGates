from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QFormLayout, QLineEdit,
                             QMessageBox)
from PyQt6.QtCore import Qt
from ...services.user_service import UserService
from ...core.database import SessionLocal
from ...models.base import School

class SchoolWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SessionLocal()
        self.user_service = UserService(self.db)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Formulaire de création d'école
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        self.name_edit = QLineEdit()
        self.city_edit = QLineEdit()
        
        form_layout.addRow("Nom de l'école:", self.name_edit)
        form_layout.addRow("Ville:", self.city_edit)
        
        # Bouton de création
        create_button = QPushButton("Créer une école")
        create_button.clicked.connect(self.create_school)
        form_layout.addRow(create_button)
        
        layout.addWidget(form_widget)
        
        # Table des écoles
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Bouton de suppression
        delete_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer l'école")
        self.delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        delete_layout.addStretch()
        delete_layout.addWidget(self.delete_button)
        table_layout.addLayout(delete_layout)
        
        # Table
        self.schools_table = QTableWidget()
        self.schools_table.setColumnCount(3)
        self.schools_table.setHorizontalHeaderLabels(["ID", "Nom", "Ville"])
        self.schools_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.schools_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.schools_table.setAlternatingRowColors(True)
        
        # Ajuster les colonnes
        header = self.schools_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Fixed)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        self.schools_table.setColumnWidth(0, 50)
        
        table_layout.addWidget(self.schools_table)
        layout.addWidget(table_widget)
        
        # Connexion du bouton de suppression
        self.delete_button.clicked.connect(self.delete_school)
        
        # Pas de marges pour optimiser l'espace
        layout.setContentsMargins(0, 0, 0, 0)
        
    def load_data(self):
        """Charge la liste des écoles"""
        schools = self.db.query(School).order_by(School.name).all()
        self.schools_table.setRowCount(0)
        
        for row, school in enumerate(schools):
            self.schools_table.insertRow(row)
            self.schools_table.setItem(row, 0, QTableWidgetItem(str(school.id)))
            self.schools_table.setItem(row, 1, QTableWidgetItem(school.name))
            self.schools_table.setItem(row, 2, QTableWidgetItem(school.city))
            
    def create_school(self):
        """Crée une nouvelle école"""
        name = self.name_edit.text().strip()
        city = self.city_edit.text().strip()
        
        # Validation des champs
        if not name or not city:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires")
            return
            
        try:
            # Vérifier si une école avec le même nom existe déjà
            existing_school = self.db.query(School).filter(School.name == name).first()
            if existing_school:
                QMessageBox.warning(self, "Erreur", "Une école avec ce nom existe déjà")
                return
                
            # Créer la nouvelle école
            school = School(
                name=name,
                city=city
            )
            
            self.db.add(school)
            self.db.commit()
            
            # Réinitialiser le formulaire
            self.name_edit.clear()
            self.city_edit.clear()
            
            # Rafraîchir les données
            self.load_data()
            
            QMessageBox.information(self, "Succès", "L'école a été créée avec succès!")
            
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")
            
    def delete_school(self):
        """Supprime une école"""
        # Vérifier qu'une école est sélectionnée
        selected_items = self.schools_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une école")
            return
            
        school_id = int(selected_items[0].text())
        school = self.db.query(School).filter(School.id == school_id).first()
        if not school:
            QMessageBox.critical(self, "Erreur", "École non trouvée.")
            return
            
        # Vérifier si l'école a des équipes
        if school.teams:
            QMessageBox.warning(
                self,
                "Erreur",
                "Cette école ne peut pas être supprimée car elle a des équipes associées. "
                "Supprimez d'abord toutes les équipes de cette école."
            )
            return
            
        # Demander confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer l'école '{school.name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete(school)
                self.db.commit()
                
                # Rafraîchir les données
                self.load_data()
                
                QMessageBox.information(self, "Succès", "L'école a été supprimée avec succès!")
                
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")
                
    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture du widget"""
        self.db.close()
        super().closeEvent(event)
