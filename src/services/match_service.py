from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from ..models.base import Match, Tournament, Team

class MatchService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_match(self, tournament_id: int, team1_id: int, team2_id: int, 
                    round: int, scheduled_time: Optional[datetime] = None) -> Match:
        """
        Crée un nouveau match dans un tournoi
        """
        # Vérifier que les équipes existent et sont inscrites au tournoi
        tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            raise ValueError("Tournament not found")
            
        team1 = self.db.query(Team).filter(Team.id == team1_id).first()
        team2 = self.db.query(Team).filter(Team.id == team2_id).first()
        if not team1 or not team2:
            raise ValueError("One or both teams not found")
            
        # Créer le match
        match = Match(
            tournament_id=tournament_id,
            team1_id=team1_id,
            team2_id=team2_id,
            round=round,
            status="pending",
            scheduled_time=scheduled_time
        )
        
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match
    
    def update_score(self, match_id: int, score: str, winner_id: Optional[int] = None) -> Match:
        """
        Met à jour le score d'un match et optionnellement définit le gagnant
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError("Match not found")
            
        if winner_id and winner_id not in [match.team1_id, match.team2_id]:
            raise ValueError("Winner must be one of the participating teams")
            
        match.score = score
        match.winner_id = winner_id
        if winner_id:
            match.status = "completed"
            match.completed_time = datetime.now()
            
        self.db.commit()
        self.db.refresh(match)
        return match
    
    def update_status(self, match_id: int, status: str) -> Match:
        """
        Met à jour le statut d'un match
        """
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError("Match not found")
            
        match.status = status
        if status == "completed" and not match.completed_time:
            match.completed_time = datetime.now()
            
        self.db.commit()
        self.db.refresh(match)
        return match
    
    def get_tournament_matches(self, tournament_id: int, round: Optional[int] = None) -> List[Match]:
        """
        Récupère tous les matchs d'un tournoi, optionnellement filtrés par round
        """
        query = self.db.query(Match).filter(Match.tournament_id == tournament_id)
        if round is not None:
            query = query.filter(Match.round == round)
        return query.all()
    
    def get_team_matches(self, team_id: int, status: Optional[str] = None) -> List[Match]:
        """
        Récupère tous les matchs d'une équipe, optionnellement filtrés par statut
        """
        query = self.db.query(Match).filter(
            or_(Match.team1_id == team_id, Match.team2_id == team_id)
        )
        if status:
            query = query.filter(Match.status == status)
        return query.order_by(Match.scheduled_time).all()
    
    def get_all_matches(self) -> List[Match]:
        """
        Récupère tous les matchs avec leurs relations (tournoi et équipes)
        """
        return self.db.query(Match)\
            .options(
                joinedload(Match.tournament),
                joinedload(Match.team1),
                joinedload(Match.team2)
            )\
            .order_by(Match.created_at.desc())\
            .all()
    
    def get_current_matches(self) -> List[Match]:
        """
        Récupère tous les matchs en cours ou à venir
        """
        return self.db.query(Match)\
            .options(
                joinedload(Match.tournament),
                joinedload(Match.team1),
                joinedload(Match.team2)
            )\
            .filter(Match.status.in_(['pending', 'in_progress']))\
            .order_by(Match.scheduled_time)\
            .all()

    def get_match(self, match_id: int) -> Match:
        """Récupère un match par son ID"""
        return self.db.query(Match)\
            .options(
                joinedload(Match.tournament),
                joinedload(Match.team1),
                joinedload(Match.team2)
            )\
            .filter(Match.id == match_id)\
            .first()
            
    def update_match_score(self, match_id: int, score: str, winner_id: int = None, status: str = None) -> Match:
        """Met à jour le score d'un match"""
        match = self.get_match(match_id)
        if not match:
            raise ValueError("Match non trouvé")
            
        match.score = score
        if winner_id:
            match.winner_id = winner_id
            match.status = "COMPLETED"
            match.completed_time = datetime.now()
        elif status:
            match.status = status
            
        self.db.commit()
        return match

    def delete_match(self, match_id: int):
        """Supprime un match"""
        match = self.get_match(match_id)
        if not match:
            raise ValueError("Match non trouvé")
            
        self.db.delete(match)
        self.db.commit()
