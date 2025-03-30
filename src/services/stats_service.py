from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models.base import User, Team, TeamMember, School, TournamentTeam

class StatsService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_user_growth(self) -> List[Tuple[datetime, int]]:
        """
        Récupère la croissance des utilisateurs au fil du temps.
        Retourne une liste de tuples (date, nombre cumulé d'utilisateurs)
        """
        # Récupérer tous les utilisateurs triés par date de création
        users = self.db.query(User)\
            .order_by(User.created_at)\
            .all()
            
        if not users:
            return []
            
        # Calculer le nombre cumulé d'utilisateurs par date
        result = []
        count = 0
        current_date = None
        
        for user in users:
            date = user.created_at.date()
            if date != current_date:
                if current_date is not None:
                    result.append((current_date, count))
                current_date = date
            count += 1
            
        # Ajouter le dernier point
        if current_date is not None:
            result.append((current_date, count))
            
        return result
        
    def get_team_growth(self) -> List[Tuple[datetime, int]]:
        """
        Récupère la croissance des équipes au fil du temps.
        Retourne une liste de tuples (date, nombre cumulé d'équipes)
        """
        # Récupérer toutes les équipes triées par date de création
        teams = self.db.query(Team)\
            .order_by(Team.created_at)\
            .all()
            
        if not teams:
            return []
            
        # Calculer le nombre cumulé d'équipes par date
        result = []
        count = 0
        current_date = None
        
        for team in teams:
            date = team.created_at.date()
            if date != current_date:
                if current_date is not None:
                    result.append((current_date, count))
                current_date = date
            count += 1
            
        # Ajouter le dernier point
        if current_date is not None:
            result.append((current_date, count))
            
        return result

    def get_players_per_team(self) -> List[Tuple[str, int]]:
        """
        Récupère le nombre de joueurs par équipe.
        Retourne une liste de tuples (nom de l'équipe, nombre de joueurs)
        """
        # Compter le nombre de joueurs par équipe
        stats = self.db.query(
            Team.name,
            func.count(TeamMember.user_id).label('player_count')
        )\
            .join(TeamMember, Team.id == TeamMember.team_id)\
            .group_by(Team.id, Team.name)\
            .order_by(func.count(TeamMember.user_id).desc())\
            .all()
            
        return [(team.name, team.player_count) for team in stats]
        
    def get_tournament_registrations_per_school(self) -> List[Tuple[str, int]]:
        """
        Récupère le nombre d'inscriptions aux tournois par école.
        Retourne une liste de tuples (nom de l'école, nombre d'inscriptions)
        """
        # Compter le nombre d'inscriptions par école
        stats = self.db.query(
            School.name,
            func.count(TournamentTeam.tournament_id).label('registration_count')
        )\
            .join(Team, School.id == Team.school_id)\
            .join(TournamentTeam, Team.id == TournamentTeam.team_id)\
            .group_by(School.id, School.name)\
            .order_by(func.count(TournamentTeam.tournament_id).desc())\
            .all()
            
        return [(school.name, school.registration_count) for school in stats]
