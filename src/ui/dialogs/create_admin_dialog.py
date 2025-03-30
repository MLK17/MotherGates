from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, 
                            QMessageBox, QLabel, QVBoxLayout)
from PyQt6.QtCore import Qt
from ...services.user_service import UserService
from ...core.database import SessionLocal

class CreateAdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SessionLocal()
        self.user_service = UserService(self.db)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Créer un administrateur")
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Message d'information sur les exigences du mot de passe
        password_info = QLabel(
            "Le mot de passe doit respecter les critères suivants :\n"
            "• Minimum 12 caractères\n"
            "• Au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>)\n"
            "• Au moins un chiffre\n"
            "• Au moins une lettre majuscule\n"
            "• Au moins une lettre minuscule\n"
            "• Pas de caractères répétés plus de 2 fois (ex: 'aaa')\n"
            "• Pas de séquences numériques simples (ex: '123')\n"
            "• Pas de mots de passe communs\n"
            "• Ne doit pas contenir le mot 'admin'"
        )
        password_info.setStyleSheet("color: #666; font-size: 10pt;")
        password_info.setWordWrap(True)
        main_layout.addWidget(password_info)
        
        # Champs de saisie
        self.pseudo_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Pseudo:", self.pseudo_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Mot de passe:", self.password_edit)
        
        main_layout.addLayout(form_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Créer")
        self.cancel_button = QPushButton("Annuler")
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)
        
        # Ajuster la taille de la fenêtre
        self.setMinimumWidth(400)
        
        # Connexions
        self.create_button.clicked.connect(self.create_admin)
        self.cancel_button.clicked.connect(self.reject)
        
    def create_admin(self):
        """Crée un nouvel administrateur"""
        try:
            self.user_service.create_admin(
                pseudo=self.pseudo_edit.text(),
                email=self.email_edit.text(),
                password=self.password_edit.text()
            )
            QMessageBox.information(self, "Succès", "L'administrateur a été créé avec succès")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")
            
    def closeEvent(self, event):
        """Ferme la connexion à la base de données lors de la fermeture du dialogue"""
        self.db.close()
        super().closeEvent(event)
