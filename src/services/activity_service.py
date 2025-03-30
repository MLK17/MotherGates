from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from ..models.base import Team, Tournament, User, Match, TeamMember, TournamentTeam

class ActivityService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_new_teams(self, limit: int = 10) -> List[Team]:
        """Récupère les équipes récemment créées"""
        return self.db.query(Team)\
            .options(
                joinedload(Team.captain),
                joinedload(Team.school)
            )\
            .order_by(desc(Team.created_at))\
            .limit(limit)\
            .all()
    
    def get_tournament_registrations(self, tournament_id: int = None) -> List[TournamentTeam]:
        """Récupère les inscriptions aux tournois"""
        query = self.db.query(TournamentTeam)\
            .options(
                joinedload(TournamentTeam.team).joinedload(Team.captain),
                joinedload(TournamentTeam.tournament)
            )\
            .order_by(desc(TournamentTeam.registered_at))
            
        if tournament_id:
            query = query.filter(TournamentTeam.tournament_id == tournament_id)
            
        return query.all()
    
    def get_tournament_slots(self) -> List[dict]:
        """Récupère les places disponibles dans tous les tournois"""
        # Sous-requête pour compter le nombre de joueurs inscrits par tournoi
        registered_players = self.db.query(
            Tournament.id.label('tournament_id'),
            func.count(TeamMember.id).label('player_count')
        )\
        .join(TournamentTeam, Tournament.id == TournamentTeam.tournament_id)\
        .join(Team, TournamentTeam.team_id == Team.id)\
        .join(TeamMember, Team.id == TeamMember.team_id)\
        .group_by(Tournament.id)\
        .subquery()
        
        # Requête principale pour récupérer les tournois avec le nombre de joueurs inscrits
        tournaments = self.db.query(
            Tournament,
            func.coalesce(registered_players.c.player_count, 0).label('registered_count')
        )\
        .outerjoin(registered_players, Tournament.id == registered_players.c.tournament_id)\
        .all()
        
        result = []
        for tournament, registered_count in tournaments:
            result.append({
                'title': tournament.title,
                'max_players': tournament.max_players,
                'registered_players': registered_count,
                'available_slots': tournament.max_players - registered_count
            })
        return result
    
    def get_team_members(self) -> List[TeamMember]:
        """Récupère tous les membres des équipes"""
        return self.db.query(TeamMember)\
            .options(
                joinedload(TeamMember.team).joinedload(Team.school),
                joinedload(TeamMember.user)
            )\
            .all()
            
    def get_match_history(self, limit: int = 20) -> List[Match]:
        """Récupère l'historique des matchs"""
        matches = self.db.query(Match)\
            .options(
                joinedload(Match.tournament),
                joinedload(Match.team1),
                joinedload(Match.team2)
            )\
            .filter(Match.status == "COMPLETED")\
            .order_by(desc(Match.completed_time))\
            .limit(limit)\
            .all()
            
        # Pour chaque match, définir le nom de l'équipe gagnante
        for match in matches:
            if match.winner_id:
                if match.winner_id == match.team1.id:
                    match.winner_name = match.team1.name
                elif match.winner_id == match.team2.id:
                    match.winner_name = match.team2.name
                else:
                    match.winner_name = "Inconnu"
            else:
                match.winner_name = "Non défini"
                
        return matches
