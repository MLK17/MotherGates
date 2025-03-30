# SlayerGates Admin Interface

Interface d'administration pour la plateforme SlayerGates permettant la gestion des tournois, écoles, équipes, utilisateurs et matchs.

## Prérequis

- Python 3.10+
- PostgreSQL 15+
- Git

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/MLK17/MotherGates.git
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

1. Copier le fichier `.env.example` en `.env` :
```bash
cp .env.example .env  # Linux/Mac
# ou
copy .env.example .env  # Windows
```

2. Configurer les variables d'environnement dans le fichier `.env` :
- `DATABASE_URL` : URL de connexion à la base de données PostgreSQL
- `JWT_SECRET` : Clé secrète pour la validation des tokens JWT

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
│   ├── services/       # Services métier
│   └── ui/            # Interface utilisateur
│       ├── dialogs/   # Boîtes de dialogue
│       └── widgets/   # Widgets personnalisés
├── resources/        # Ressources (images, icônes)
└── logs/           # Fichiers de logs
```

## Fonctionnalités

### Gestion des Tournois
- Création de tournois avec configuration complète
- Vue des inscriptions aux tournois
- Suivi des places disponibles
- Suppression de tournois avec confirmation

### Gestion des Écoles
- Création d'écoles (nom et ville)
- Liste des écoles existantes
- Suppression d'écoles (si pas d'équipes associées)
- Interface intuitive avec retours visuels

### Gestion des Équipes
- Vue des équipes par école
- Gestion des membres
- Association école-équipe
- Suivi des inscriptions aux tournois

### Gestion des Matchs
- Planification des matchs
- Suivi des résultats
- Mise à jour des statuts

### Système de Logs
- Traçabilité des actions
- Historique des modifications
- Statistiques d'utilisation

### Sécurité
- Gestion des administrateurs
- Protection des données sensibles
- Validation des entrées utilisateur

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
