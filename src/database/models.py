from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from core.enums import MatchFormat, TossDecision, WicketType, PlayerRole, BallPhase

class Base(DeclarativeBase):
    pass

# ------------------------
# Core Entities
# ------------------------
class Team(Base):
    __tablename__ = "teams"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    players: Mapped[List["Player"]] = relationship("Player", back_populates="team")
    matches_as_team_a: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.team_a_id", back_populates="team_a"
    )
    matches_as_team_b: Mapped[List["Match"]] = relationship(
        "Match", foreign_keys="Match.team_b_id", back_populates="team_b"
    )

class Player(Base):
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    dob: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    place_of_birth: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    batting_style: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bowling_style: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"), index=True
    )
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="players")
    
    # Additional relationships
    player_roles: Mapped[List["PlayerRole"]] = relationship("PlayerRole", back_populates="player")
    player_specialties: Mapped[List["PlayerSpecialty"]] = relationship("PlayerSpecialty", back_populates="player")

class PlayerRole(Base):
    __tablename__ = "player_roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    role: Mapped[PlayerRole] = mapped_column(Enum(PlayerRole))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    format: Mapped[MatchFormat] = mapped_column(Enum(MatchFormat))
    
    player: Mapped["Player"] = relationship("Player", back_populates="player_roles")

class PlayerSpecialty(Base):
    __tablename__ = "player_specialties"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    specialty: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)
    
    player: Mapped["Player"] = relationship("Player", back_populates="player_specialties")

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    season: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    format: Mapped[MatchFormat] = mapped_column(Enum(MatchFormat), nullable=False)
    
    # Relationships
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="tournament")

class Stadium(Base):
    __tablename__ = "stadiums"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)

    pitch_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bounce_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    grass_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cracks_present: Mapped[bool] = mapped_column(Boolean, default=False)
    avg_first_innings_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    favor_spin: Mapped[bool] = mapped_column(Boolean, default=False)
    favor_pace: Mapped[bool] = mapped_column(Boolean, default=False)

    matches: Mapped[List["Match"]] = relationship("Match", back_populates="stadium")

class Match(Base):
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(
        ForeignKey("tournaments.id", ondelete="CASCADE"), index=True
    )
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    format: Mapped[MatchFormat] = mapped_column(Enum(MatchFormat), nullable=False)
    stadium_id: Mapped[int] = mapped_column(ForeignKey("stadiums.id"))

    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    neutral_venue: Mapped[bool] = mapped_column(Boolean, default=False)
    toss_winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    toss_decision: Mapped[Optional[TossDecision]] = mapped_column(Enum(TossDecision), nullable=True)
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    result: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="matches")
    team_a: Mapped["Team"] = relationship("Team", foreign_keys=[team_a_id], back_populates="matches_as_team_a")
    team_b: Mapped["Team"] = relationship("Team", foreign_keys=[team_b_id], back_populates="matches_as_team_b")
    stadium: Mapped["Stadium"] = relationship("Stadium", back_populates="matches")
    pitch_conditions: Mapped[List["PitchConditions"]] = relationship("PitchConditions", back_populates="match")
    weather_data: Mapped[List["WeatherData"]] = relationship("WeatherData", back_populates="match")
    innings: Mapped[List["Innings"]] = relationship("Innings", back_populates="match")
    player_stats: Mapped[List["PlayerStats"]] = relationship("PlayerStats", back_populates="match")

class PitchConditions(Base):
    __tablename__ = "pitch_conditions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    stadium_id: Mapped[int] = mapped_column(ForeignKey("stadiums.id"))
    
    # Dynamic pitch metrics
    hardness_rating: Mapped[Optional[float]] = mapped_column(Float)
    moisture_content: Mapped[Optional[float]] = mapped_column(Float)
    wear_level: Mapped[Optional[float]] = mapped_column(Float)
    predicted_behavior: Mapped[Optional[str]] = mapped_column(String)
    
    assessed_by: Mapped[Optional[str]] = mapped_column(String)
    assessment_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    match: Mapped["Match"] = relationship("Match", back_populates="pitch_conditions")
    stadium: Mapped["Stadium"] = relationship("Stadium")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), index=True
    )
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed_kph: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    condition: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    match: Mapped["Match"] = relationship("Match", back_populates="weather_data")


# ------------------------
# Innings / Ball-by-Ball
# ------------------------
class Innings(Base):
    __tablename__ = "innings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), index=True
    )
    batting_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    bowling_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    innings_number: Mapped[int] = mapped_column(Integer, nullable=False)

    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    total_wickets: Mapped[int] = mapped_column(Integer, default=0)
    overs_completed: Mapped[float] = mapped_column(Float, default=0.0)

    match: Mapped["Match"] = relationship("Match", back_populates="innings")
    batting_team: Mapped["Team"] = relationship("Team", foreign_keys=[batting_team_id])
    bowling_team: Mapped["Team"] = relationship("Team", foreign_keys=[bowling_team_id])
    overs: Mapped[List["Over"]] = relationship("Over", back_populates="innings")

class Over(Base):
    __tablename__ = "overs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    innings_id: Mapped[int] = mapped_column(
        ForeignKey("innings.id", ondelete="CASCADE"), index=True
    )
    over_number: Mapped[int] = mapped_column(Integer, nullable=False)
    bowler_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

    innings: Mapped["Innings"] = relationship("Innings", back_populates="overs")
    bowler: Mapped["Player"] = relationship("Player")
    balls: Mapped[List["Ball"]] = relationship("Ball", back_populates="over")

class Ball(Base):
    __tablename__ = "balls"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    over_id: Mapped[int] = mapped_column(
        ForeignKey("overs.id", ondelete="CASCADE"), index=True
    )
    ball_number: Mapped[int] = mapped_column(Integer, nullable=False)
    batsman_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    non_striker_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    bowler_id: Mapped[int] = mapped_column(ForeignKey("players.id"))

    runs_scored: Mapped[int] = mapped_column(Integer, default=0)
    extras_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    extras_runs: Mapped[int] = mapped_column(Integer, default=0)
    wicket_type: Mapped[Optional[WicketType]] = mapped_column(Enum(WicketType), nullable=True)
    player_out_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)

    is_boundary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_six: Mapped[bool] = mapped_column(Boolean, default=False)
    is_powerplay: Mapped[bool] = mapped_column(Boolean, default=False)
    phase: Mapped[Optional[BallPhase]] = mapped_column(Enum(BallPhase), nullable=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)

    over: Mapped["Over"] = relationship("Over", back_populates="balls")
    batsman: Mapped["Player"] = relationship("Player", foreign_keys=[batsman_id])
    ball_tracking: Mapped[Optional["BallTracking"]] = relationship("BallTracking", back_populates="ball")
    
class BallTracking(Base):
    __tablename__ = "ball_tracking"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ball_id: Mapped[int] = mapped_column(ForeignKey("balls.id"))
    
    # Hawk-Eye equivalent data
    release_speed: Mapped[Optional[float]] = mapped_column(Float)
    bounce_point: Mapped[Optional[float]] = mapped_column(Float)
    swing_angle: Mapped[Optional[float]] = mapped_column(Float)
    seam_position: Mapped[Optional[float]] = mapped_column(Float)
    impact_point_bat: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Outcome predictions
    expected_runs: Mapped[Optional[float]] = mapped_column(Float)
    wicket_probability: Mapped[Optional[float]] = mapped_column(Float)

    ball: Mapped["Ball"] = relationship("Ball", back_populates="ball_tracking")

# ------------------------
# Player / Team Stats
# ------------------------
class PlayerStats(Base):
    __tablename__ = "player_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), index=True
    )

    runs_scored: Mapped[int] = mapped_column(Integer, default=0)
    balls_faced: Mapped[int] = mapped_column(Integer, default=0)
    wickets_taken: Mapped[int] = mapped_column(Integer, default=0)
    overs_bowled: Mapped[float] = mapped_column(Float, default=0.0)
    economy_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    strike_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    player: Mapped["Player"] = relationship("Player", back_populates="player_stats")
    match: Mapped["Match"] = relationship("Match", back_populates="player_stats")

    __table_args__ = (
        UniqueConstraint("player_id", "match_id", name="uq_player_match_stats"),
    )


class TeamStats(Base):
    __tablename__ = "team_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    tournament_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tournaments.id"), index=True, nullable=True
    )

    matches_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    ties: Mapped[int] = mapped_column(Integer, default=0)
    no_results: Mapped[int] = mapped_column(Integer, default=0)

    total_runs_scored: Mapped[int] = mapped_column(Integer, default=0)
    total_runs_conceded: Mapped[int] = mapped_column(Integer, default=0)
    wickets_taken: Mapped[int] = mapped_column(Integer, default=0)
    wickets_lost: Mapped[int] = mapped_column(Integer, default=0)

    net_run_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    win_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recent_form: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    team: Mapped["Team"] = relationship("Team")
    tournament: Mapped[Optional["Tournament"]] = relationship("Tournament")

    __table_args__ = (
        UniqueConstraint("team_id", "tournament_id", name="uq_team_tournament_stats"),
    )


# ------------------------
# Head-to-Head & Player-Vs-Bowler
# ------------------------
class HeadToHeadTeamStats(Base):
    __tablename__ = "head_to_head_team_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    format: Mapped[MatchFormat] = mapped_column(Enum(MatchFormat), nullable=False)

    matches_played: Mapped[int] = mapped_column(Integer, default=0)
    team_a_wins: Mapped[int] = mapped_column(Integer, default=0)
    team_b_wins: Mapped[int] = mapped_column(Integer, default=0)
    ties: Mapped[int] = mapped_column(Integer, default=0)
    no_results: Mapped[int] = mapped_column(Integer, default=0)

    avg_score_team_a: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_score_team_b: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    net_run_rate_a_vs_b: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    team_a: Mapped["Team"] = relationship("Team", foreign_keys=[team_a_id])
    team_b: Mapped["Team"] = relationship("Team", foreign_keys=[team_b_id])

    __table_args__ = (
        UniqueConstraint("team_a_id", "team_b_id", "format", name="uq_team_h2h"),
        Index("ix_h2h_team_pair", "team_a_id", "team_b_id", "format"),
    )


class PlayerVsBowlerStats(Base):
    __tablename__ = "player_vs_bowler_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batsman_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True, nullable=False)
    bowler_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True, nullable=False)
    format: Mapped[MatchFormat] = mapped_column(Enum(MatchFormat), nullable=False)

    balls_faced: Mapped[int] = mapped_column(Integer, default=0)
    runs_scored: Mapped[int] = mapped_column(Integer, default=0)
    dismissals: Mapped[int] = mapped_column(Integer, default=0)
    strike_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    dot_ball_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    boundary_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    batsman: Mapped["Player"] = relationship("Player", foreign_keys=[batsman_id])
    bowler: Mapped["Player"] = relationship("Player", foreign_keys=[bowler_id])

    __table_args__ = (
        UniqueConstraint("batsman_id", "bowler_id", "format", name="uq_player_bowler_stats"),
        Index("ix_batsman_bowler_pair", "batsman_id", "bowler_id", "format"),
    )


# ------------------------
# Probability & Derived Metrics
# ------------------------
class ProbabilityState(Base):
    __tablename__ = "probability_state"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), index=True
    )
    innings_id: Mapped[int] = mapped_column(
        ForeignKey("innings.id", ondelete="CASCADE"), index=True
    )
    ball_id: Mapped[int] = mapped_column(
        ForeignKey("balls.id", ondelete="CASCADE"), index=True
    )

    draw_prob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    no_result_prob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    runs_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    balls_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    wickets_remaining: Mapped[Optional[int]] = mapped_column(Integer)

    win_prob_team1: Mapped[Optional[float]] = mapped_column(Float)
    win_prob_team2: Mapped[Optional[float]] = mapped_column(Float)

    expected_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    features: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    model_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    training_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    match: Mapped["Match"] = relationship("Match")
    innings: Mapped["Innings"] = relationship("Innings")
    ball: Mapped["Ball"] = relationship("Ball")

    __table_args__ = (
        Index("ix_prob_state_match_innings_ball", "match_id", "innings_id", "ball_id"),
    )


# ------------------------
# Situational Derived Metrics
# ------------------------
class SituationalMetrics(Base):
    __tablename__ = "situational_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    innings_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("innings.id", ondelete="CASCADE"), index=True, nullable=True
    )
    over_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("overs.id", ondelete="CASCADE"), index=True, nullable=True
    )

    momentum_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pressure_overs_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    batting_form_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bowling_form_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pitch_adjusted_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    match: Mapped["Match"] = relationship("Match")
    team: Mapped["Team"] = relationship("Team")
    innings: Mapped[Optional["Innings"]] = relationship("Innings")
    over: Mapped[Optional["Over"]] = relationship("Over")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    features_used: Mapped[Optional[dict]] = mapped_column(JSONB)
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    training_data_range: Mapped[Optional[dict]] = mapped_column(JSONB)
    performance_metrics: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class PredictionAudit(Base):
    __tablename__ = "prediction_audit"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"))
    prediction_time: Mapped[datetime] = mapped_column(DateTime)
    features_used: Mapped[Optional[dict]] = mapped_column(JSONB)
    prediction_output: Mapped[Optional[dict]] = mapped_column(JSONB)
    actual_result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    prediction_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)