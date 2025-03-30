from dotenv import load_dotenv
import os
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL n'est pas défini dans le fichier .env")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET n'est pas défini dans le fichier .env")

# Configuration des chemins
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
RESOURCES_DIR = BASE_DIR / "resources"

# Créer les répertoires nécessaires
LOGS_DIR.mkdir(exist_ok=True)
RESOURCES_DIR.mkdir(exist_ok=True)

# Configuration de l'application
APP_NAME = "SlayerGates Admin"
APP_VERSION = "1.0.0"
