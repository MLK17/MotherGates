from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from ..models.base import User, School, Team, TeamMember
from werkzeug.security import generate_password_hash
import re

class UserService:
    def __init__(self, db: Session):
        self.db = db
        
    def validate_admin_password(self, password: str) -> tuple[bool, str]:
        """
        Valide le mot de passe d'un administrateur selon des critères stricts.
        Retourne un tuple (is_valid, message)
        """
        # Liste de mots de passe communs à interdire
        common_passwords = [
            "admin123", "password", "123456", "qwerty", "azerty",
            "motdepasse", "administrator", "adminadmin"
        ]

        # Vérification de la longueur (minimum 12 caractères)
        if len(password) < 12:
            return False, "Le mot de passe doit contenir au moins 12 caractères"

        # Vérification des caractères spéciaux
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>)"

        # Vérification des chiffres
        if not re.search(r"\d", password):
            return False, "Le mot de passe doit contenir au moins un chiffre"

        # Vérification des lettres majuscules
        if not re.search(r"[A-Z]", password):
            return False, "Le mot de passe doit contenir au moins une lettre majuscule"

        # Vérification des lettres minuscules
        if not re.search(r"[a-z]", password):
            return False, "Le mot de passe doit contenir au moins une lettre minuscule"

        # Vérification des séquences répétées (ex: "aaa", "111")
        if re.search(r"(.)\1{2,}", password):
            return False, "Le mot de passe ne doit pas contenir de caractères répétés plus de deux fois de suite"

        # Vérification des séquences numériques (ex: "123", "987")
        if re.search(r"(?:012|123|234|345|456|567|678|789|987|876|765|654|543|432|321|210)", password):
            return False, "Le mot de passe ne doit pas contenir de séquences numériques simples"

        # Vérification des mots de passe communs
        if password.lower() in common_passwords:
            return False, "Ce mot de passe est trop commun, veuillez en choisir un plus complexe"

        # Vérification de la présence du mot "admin"
        if "admin" in password.lower():
            return False, "Le mot de passe ne doit pas contenir le mot 'admin'"

        return True, "Mot de passe valide"

    def create_admin(self, pseudo: str, email: str, password: str) -> User:
        """
        Crée un nouvel utilisateur avec le rôle administrateur
        """
        # Validation du mot de passe
        is_valid, message = self.validate_admin_password(password)
        if not is_valid:
            raise ValueError(f"Mot de passe invalide : {message}")

        # Vérifier si l'utilisateur existe déjà
        existing_user = self.db.query(User)\
            .filter((User.pseudo == pseudo) | (User.email == email))\
            .first()
            
        if existing_user:
            raise ValueError("Un utilisateur avec ce pseudo ou cet email existe déjà")
            
        # Créer le nouvel administrateur
        user = User(
            pseudo=pseudo,
            email=email,
            password=generate_password_hash(password),
            role='admin'
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
        
    def get_players(self, search_term: str = None, school_id: Optional[int] = None) -> List[User]:
        """
        Récupère la liste des joueurs (role = user) avec filtres optionnels
        """
        query = self.db.query(User)\
            .filter(User.role == 'user')\
            .options(
                joinedload(User.team_memberships)
                .joinedload(TeamMember.team)
                .joinedload(Team.school)
            )
            
        if search_term:
            query = query.filter(
                User.pseudo.ilike(f"%{search_term}%") |
                User.email.ilike(f"%{search_term}%")
            )
            
        if school_id:
            query = query.join(User.team_memberships)\
                .join(TeamMember.team)\
                .join(Team.school)\
                .filter(School.id == school_id)
            
        return query.order_by(User.pseudo).all()
        
    def get_schools(self) -> List[School]:
        """Récupère la liste des écoles pour le filtre"""
        return self.db.query(School).order_by(School.name).all()

    def get_all_users_with_relations(self) -> List[User]:
        """Récupère tous les utilisateurs avec leurs relations (écoles et équipes via TeamMember)"""
        return self.db.query(User)\
            .options(
                joinedload(User.team_memberships)
                .joinedload(TeamMember.team)
                .joinedload(Team.school)
            )\
            .order_by(User.created_at.desc())\
            .all()

    def get_all_schools(self) -> List[School]:
        """Récupère toutes les écoles"""
        return self.db.query(School)\
            .order_by(School.name)\
            .all()

    def get_all_teams(self) -> List[Team]:
        """Récupère toutes les équipes"""
        return self.db.query(Team)\
            .order_by(Team.name)\
            .all()
