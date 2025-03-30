# SlayerGates Admin Interface

Interface d'administration pour la plateforme SlayerGates permettant la gestion des tournois, écoles, équipes, utilisateurs et matchs.

## Prérequis

- Python 3.10+
- PostgreSQL 15+
- Git

## Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd mothergates
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration

1. La configuration de la base de données et autres paramètres est gérée automatiquement via les variables d'environnement.

## Lancement

Pour lancer l'application :
```bash
python main.py
```

## Structure du Projet

```
mothergates/
├── src/
│   ├── core/           # Configuration et utilitaires core
│   ├── models/         # Modèles de données
│   └── ui/            # Interface utilisateur
├── resources/        # Ressources (images, icônes)
└── logs/           # Fichiers de logs
```

## Fonctionnalités

- Gestion des tournois
- Gestion des écoles
- Gestion des équipes
- Gestion des utilisateurs
- Gestion des matchs
- Système de logs
