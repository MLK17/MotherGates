from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

# Créer une session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer la base pour les modèles
Base = declarative_base()

def get_db():
    """Retourne une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session():
    """Retourne une session de base de données directement (sans générateur)"""
    return SessionLocal()
