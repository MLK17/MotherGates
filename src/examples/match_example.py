from datetime import datetime, timedelta
from ..core.database import SessionLocal
from ..services.match_service import MatchService

def demo_match_management():
    # Créer une session de base de données
    db = SessionLocal()
    match_service = MatchService(db)
    
    try:
        # 1. Créer un match
        print("\nCréation d'un nouveau match...")
        scheduled_time = datetime.now() + timedelta(days=1)
        match = match_service.create_match(
            tournament_id=1,  # Assurez-vous que ce tournoi existe
            team1_id=1,      # Assurez-vous que cette équipe existe
            team2_id=2,      # Assurez-vous que cette équipe existe
            round=1,
            scheduled_time=scheduled_time
        )
        print(f"Match créé: {match.id} - {match.status}")
        
        # 2. Mettre à jour le statut du match (début du match)
        print("\nDébut du match...")
        match = match_service.update_status(match.id, "in_progress")
        print(f"Statut mis à jour: {match.status}")
        
        # 3. Mettre à jour le score
        print("\nMise à jour du score...")
        match = match_service.update_score(
            match_id=match.id,
            score="16-14",
            winner_id=match.team1_id  # L'équipe 1 gagne
        )
        print(f"Score final: {match.score}, Gagnant: Équipe {match.winner_id}")
        
        # 4. Récupérer tous les matchs du tournoi
        print("\nListe des matchs du tournoi 1:")
        tournament_matches = match_service.get_tournament_matches(tournament_id=1)
        for m in tournament_matches:
            print(f"Match {m.id}: {m.team1_id} vs {m.team2_id} - {m.status}")
            
    except Exception as e:
        print(f"Erreur: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    demo_match_management()
