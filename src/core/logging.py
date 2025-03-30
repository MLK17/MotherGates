from loguru import logger
import sys
from pathlib import Path
from .config import LOGS_DIR

# Configuration du logger
def setup_logging():
    # Supprimer les handlers par défaut
    logger.remove()
    
    # Format du log
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    
    # Ajouter le handler pour la console
    logger.add(sys.stderr, format=log_format)
    
    # Ajouter le handler pour le fichier
    log_file = LOGS_DIR / "slayergates.log"
    logger.add(
        log_file,
        format=log_format,
        rotation="1 day",
        retention="1 month",
        compression="zip"
    )

    return logger
