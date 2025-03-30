import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.core.logging import setup_logging
from src.core.database import engine, Base

def restart_application():
    QApplication.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    # Initialiser le logger
    logger = setup_logging()
    logger.info("Démarrage de l'application MotherGates Admin")
    
    try:
        # Créer les tables dans la base de données
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée avec succès")
        
        # Créer l'application Qt
        app = QApplication(sys.argv)
        
        # Créer et afficher la fenêtre principale
        window = MainWindow()
        # Ajouter le raccourci clavier pour le redémarrage
        window.shortcut_restart = window.create_shortcut(Qt.Key.Key_R | Qt.KeyboardModifier.ControlModifier, restart_application)
        window.show()
        
        # Démarrer la boucle d'événements
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
