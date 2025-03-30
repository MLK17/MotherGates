from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class School(Base):
    __tablename__ = "School"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relations
    teams = relationship("Team", back_populates="school")

class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True)
    pseudo = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    role = Column(String(20), nullable=False, default='user')
    
    # Relations
    created_tournaments = relationship("Tournament", back_populates="creator")
    teams_captain = relationship("Team", back_populates="captain")
    team_memberships = relationship("TeamMember", back_populates="user")
    join_requests = relationship("TeamJoinRequest", back_populates="user")

class Tournament(Base):
    __tablename__ = "Tournament"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    game = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String(50), nullable=False)
    max_players = Column(Integer, nullable=False)
    is_online = Column(Boolean, nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    creator_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    players_per_team = Column(Integer, nullable=False)
    
    # Relations
    creator = relationship("User", back_populates="created_tournaments")
    matches = relationship("Match", back_populates="tournament")
    tournament_teams = relationship("TournamentTeam", back_populates="tournament")

class Team(Base):
    __tablename__ = "Team"
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    school_id = Column(Integer, ForeignKey('School.id'), nullable=False)
    captain_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    logo = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    description = Column(Text, nullable=True)
    
    # Relations
    school = relationship("School", back_populates="teams")
    captain = relationship("User", back_populates="teams_captain")
    members = relationship("TeamMember", back_populates="team")
    join_requests = relationship("TeamJoinRequest", back_populates="team")
    tournament_teams = relationship("TournamentTeam", back_populates="team")
    matches_team1 = relationship("Match", foreign_keys="Match.team1_id", back_populates="team1")
    matches_team2 = relationship("Match", foreign_keys="Match.team2_id", back_populates="team2")
    leaderboard = relationship("Leaderboard", back_populates="team", uselist=False)

class TeamMember(Base):
    __tablename__ = "TeamMember"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    role = Column(Text, nullable=False)
    joined_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relations
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

class TeamJoinRequest(Base):
    __tablename__ = "TeamJoinRequest"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relations
    team = relationship("Team", back_populates="join_requests")
    user = relationship("User", back_populates="join_requests")

class TournamentTeam(Base):
    __tablename__ = "TournamentTeam"
    
    tournament_id = Column(Integer, ForeignKey('Tournament.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)
    registered_at = Column(DateTime, nullable=False, default=func.now())
    participating_players = Column(ARRAY(Integer), nullable=True)
    
    # Relations
    tournament = relationship("Tournament", back_populates="tournament_teams")
    team = relationship("Team", back_populates="tournament_teams")

class Match(Base):
    __tablename__ = "Match"
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('Tournament.id'), nullable=False)
    winner_id = Column(Integer, nullable=True)
    score = Column(String(50), nullable=True)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    team1_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    team2_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    completed_time = Column(DateTime, nullable=True)
    round = Column(Integer, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    
    # Relations
    tournament = relationship("Tournament", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="matches_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="matches_team2")

class Leaderboard(Base):
    __tablename__ = "Leaderboard"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    points = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relations
    team = relationship("Team", back_populates="leaderboard")
