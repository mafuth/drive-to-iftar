from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    oauth_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=False, index=True, nullable=True)
    profile_photo = Column(String, nullable=True)
    score = Column(Integer, default=0)
    is_guest = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    games = relationship("Game", back_populates="user")
    hosted_sessions = relationship("MultiplayerSession", back_populates="host")

    # Relationships need to be defined on the other side too or updated here

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    config = Column(JSON, nullable=True)
    car_index = Column(Integer, default=0) # Host's car selection for the race visual? Or generic?
    status = Column(String, default="active") # active, finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # sessions = relationship("MultiplayerSession", back_populates="race") # Removed

class MultiplayerSession(Base):
    __tablename__ = "multiplayer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    # race_id removed to avoid circular relations / logic redundancy
    host_id = Column(Integer, ForeignKey("users.id"))
    max_players = Column(Integer, default=5)
    game_seed = Column(String)
    
    status = Column(String, default="waiting") # waiting, started, finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # race = relationship("Race", back_populates="sessions") # Removed
    host = relationship("User", back_populates="hosted_sessions")
    games = relationship("Game", back_populates="session")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    race_id = Column(Integer, ForeignKey("races.id")) # Link to Race
    multiplayer_session_id = Column(Integer, ForeignKey("multiplayer_sessions.id"), nullable=True)
    car_index = Column(Integer, default=0)
    assigned_lane = Column(Integer, nullable=True)
    score = Column(Integer, default=0)
    finished_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="games")
    session = relationship("MultiplayerSession", back_populates="games")
    race = relationship("Race") # Add relationship
