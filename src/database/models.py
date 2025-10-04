from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base
from core.enums import MatchFormat, TossDecision, WicketType, PlayerRole, BallPhase

Base = declarative_base()

# ------------------------
# Core Entities
# ------------------------
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    country = Column(String, nullable=True)
    code = Column(String, nullable=True)
    type = Column(String, nullable=True)
    
    players = relationship("Player", back_populates="team")
    matches_home = relationship("Match", foreign_keys="Match.home_team_id")
    matches_away = relationship("Match", foreign_keys="Match.away_team_id")


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(DateTime, nullable=True)
    place_of_birth = Column(String, nullable=True)
    batting_style = Column(String, nullable=True)
    bowling_style = Column(String, nullable=True)
    role = Column(Enum(PlayerRole), nullable=True)

    team_id = Column(Integer, ForeignKey(Team.id, ondelete="SET NULL"), index=True)
    team = relationship("Team", back_populates="players")


class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    season = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    format = Column(Enum(MatchFormat), nullable=False)


class Stadium(Base):
    __tablename__ = "stadiums"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    pitch_type = Column(String, nullable=True)
    bounce_rating = Column(Float, nullable=True)
    grass_coverage = Column(Float, nullable=True)
    cracks_present = Column(Boolean, default=False)
    avg_first_innings_score = Column(Float, nullable=True)
    favor_spin = Column(Boolean, default=False)
    favor_pace = Column(Boolean, default=False)

    matches = relationship("Match", back_populates="stadium")


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey(Tournament.id, ondelete="CASCADE"), index=True)
    match_date = Column(DateTime, nullable=False)
    format = Column(Enum(MatchFormat), nullable=False)
    stadium_id = Column(Integer, ForeignKey(Stadium.id))

    home_team_id = Column(Integer, ForeignKey(Team.id))
    away_team_id = Column(Integer, ForeignKey(Team.id))
    toss_winner_id = Column(Integer, ForeignKey(Team.id))
    toss_decision = Column(Enum(TossDecision), nullable=True)
    winner_id = Column(Integer, ForeignKey(Team.id), nullable=True)
    result = Column(String, nullable=True)

    tournament = relationship(Tournament)
    home_team = relationship(Team, foreign_keys=[home_team_id])
    away_team = relationship(Team, foreign_keys=[away_team_id])
    stadium = relationship(Stadium, back_populates="matches")


class WeatherData(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey(Match.id, ondelete="CASCADE"), index=True)
    temperature_c = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed_kph = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    condition = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    match = relationship(Match)


# ------------------------
# Innings / Ball-by-Ball
# ------------------------
class Innings(Base):
    __tablename__ = "innings"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey(Match.id, ondelete="CASCADE"), index=True)
    batting_team_id = Column(Integer, ForeignKey(Team.id))
    bowling_team_id = Column(Integer, ForeignKey(Team.id))
    innings_number = Column(Integer, nullable=False)

    total_runs = Column(Integer, default=0)
    total_wickets = Column(Integer, default=0)
    overs_completed = Column(Float, default=0.0)

    match = relationship(Match)
    batting_team = relationship(Team, foreign_keys=[batting_team_id])
    bowling_team = relationship(Team, foreign_keys=[bowling_team_id])


class Over(Base):
    __tablename__ = "overs"
    id = Column(Integer, primary_key=True)
    innings_id = Column(Integer, ForeignKey(Innings.id, ondelete="CASCADE"), index=True)
    over_number = Column(Integer, nullable=False)
    bowler_id = Column(Integer, ForeignKey(Player.id))

    innings = relationship(Innings)
    bowler = relationship(Player)


class Ball(Base):
    __tablename__ = "balls"
    id = Column(Integer, primary_key=True)
    over_id = Column(Integer, ForeignKey(Over.id, ondelete="CASCADE"), index=True)
    ball_number = Column(Integer, nullable=False)
    batsman_id = Column(Integer, ForeignKey(Player.id))
    non_striker_id = Column(Integer, ForeignKey(Player.id))
    bowler_id = Column(Integer, ForeignKey(Player.id))

    runs_scored = Column(Integer, default=0)
    extras_type = Column(String, nullable=True)
    extras_runs = Column(Integer, default=0)
    wicket_type = Column(Enum(WicketType), nullable=True)
    player_out_id = Column(Integer, ForeignKey(Player.id), nullable=True)

    is_boundary = Column(Boolean, default=False)
    is_six = Column(Boolean, default=False)
    is_powerplay = Column(Boolean, default=False)
    phase = Column(Enum(BallPhase), nullable=True)
    timestamp = Column(DateTime)

    over = relationship(Over)
    batsman = relationship(Player, foreign_keys=[batsman_id])


# ------------------------
# Player / Team Stats
# ------------------------
class PlayerStats(Base):
    __tablename__ = "player_stats"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey(Player.id), index=True)
    match_id = Column(Integer, ForeignKey(Match.id, ondelete="CASCADE"), index=True)

    runs_scored = Column(Integer, default=0)
    balls_faced = Column(Integer, default=0)
    wickets_taken = Column(Integer, default=0)
    overs_bowled = Column(Float, default=0.0)
    economy_rate = Column(Float, nullable=True)
    strike_rate = Column(Float, nullable=True)

    player = relationship(Player)
    match = relationship(Match)

    __table_args__ = (
        UniqueConstraint("player_id", "match_id", name="uq_player_match_stats"),
    )


class TeamStats(Base):
    __tablename__ = "team_stats"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey(Team.id), index=True, nullable=False)
    tournament_id = Column(Integer, ForeignKey(Tournament.id), index=True, nullable=True)

    matches_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    no_results = Column(Integer, default=0)

    total_runs_scored = Column(Integer, default=0)
    total_runs_conceded = Column(Integer, default=0)
    wickets_taken = Column(Integer, default=0)
    wickets_lost = Column(Integer, default=0)

    net_run_rate = Column(Float, nullable=True)
    win_percentage = Column(Float, nullable=True)
    recent_form = Column(String, nullable=True)

    last_updated = Column(DateTime, nullable=False)

    team = relationship(Team)
    tournament = relationship(Tournament)

    __table_args__ = (
        UniqueConstraint("team_id", "tournament_id", name="uq_team_tournament_stats"),
    )


# ------------------------
# Head-to-Head & Player-Vs-Bowler
# ------------------------
class HeadToHeadTeamStats(Base):
    __tablename__ = "head_to_head_team_stats"
    id = Column(Integer, primary_key=True)
    team_a_id = Column(Integer, ForeignKey(Team.id), index=True, nullable=False)
    team_b_id = Column(Integer, ForeignKey(Team.id), index=True, nullable=False)
    format = Column(Enum(MatchFormat), nullable=False)

    matches_played = Column(Integer, default=0)
    team_a_wins = Column(Integer, default=0)
    team_b_wins = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    no_results = Column(Integer, default=0)

    avg_score_team_a = Column(Float, nullable=True)
    avg_score_team_b = Column(Float, nullable=True)
    net_run_rate_a_vs_b = Column(Float, nullable=True)

    last_updated = Column(DateTime, nullable=False)

    team_a = relationship(Team, foreign_keys=[team_a_id])
    team_b = relationship(Team, foreign_keys=[team_b_id])

    __table_args__ = (
        UniqueConstraint("team_a_id", "team_b_id", "format", name="uq_team_h2h"),
        Index("ix_h2h_team_pair", "team_a_id", "team_b_id", "format"),
    )


class PlayerVsBowlerStats(Base):
    __tablename__ = "player_vs_bowler_stats"
    id = Column(Integer, primary_key=True)
    batsman_id = Column(Integer, ForeignKey(Player.id), index=True, nullable=False)
    bowler_id = Column(Integer, ForeignKey(Player.id), index=True, nullable=False)
    format = Column(Enum(MatchFormat), nullable=False)

    balls_faced = Column(Integer, default=0)
    runs_scored = Column(Integer, default=0)
    dismissals = Column(Integer, default=0)
    strike_rate = Column(Float, nullable=True)
    avg = Column(Float, nullable=True)

    dot_ball_percentage = Column(Float, nullable=True)
    boundary_percentage = Column(Float, nullable=True)

    last_updated = Column(DateTime, nullable=False)

    batsman = relationship(Player, foreign_keys=[batsman_id])
    bowler = relationship(Player, foreign_keys=[bowler_id])

    __table_args__ = (
        UniqueConstraint("batsman_id", "bowler_id", "format", name="uq_player_bowler_stats"),
        Index("ix_batsman_bowler_pair", "batsman_id", "bowler_id", "format"),
    )


# ------------------------
# Probability & Derived Metrics
# ------------------------
class ProbabilityState(Base):
    __tablename__ = "probability_state"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey(Match.id, ondelete="CASCADE"), index=True)
    innings_id = Column(Integer, ForeignKey(Innings.id, ondelete="CASCADE"), index=True)
    ball_id = Column(Integer, ForeignKey(Ball.id, ondelete="CASCADE"), index=True)

    draw_prob = Column(Float, nullable=True)
    no_result_prob = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)

    runs_remaining = Column(Integer)
    balls_remaining = Column(Integer)
    wickets_remaining = Column(Integer)

    win_prob_team1 = Column(Float)
    win_prob_team2 = Column(Float)

    expected_score = Column(Float, nullable=True)
    features = Column(JSONB, nullable=True)

    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    training_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    match = relationship(Match)
    innings = relationship(Innings)
    ball = relationship(Ball)

    __table_args__ = (
        Index("ix_prob_state_match_innings_ball", "match_id", "innings_id", "ball_id"),
    )


# ------------------------
# Situational Derived Metrics (New)
# ------------------------
class SituationalMetrics(Base):
    """
    Precomputed metrics to accelerate probability calculation.
    Examples: momentum, pressure overs, batting/bowling form, pitch-specific stats.
    """
    __tablename__ = "situational_metrics"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey(Match.id, ondelete="CASCADE"), index=True)
    team_id = Column(Integer, ForeignKey(Team.id, ondelete="CASCADE"), index=True)
    innings_id = Column(Integer, ForeignKey(Innings.id, ondelete="CASCADE"), index=True, nullable=True)
    over_id = Column(Integer, ForeignKey(Over.id, ondelete="CASCADE"), index=True, nullable=True)

    momentum_index = Column(Float, nullable=True)
    pressure_overs_index = Column(Float, nullable=True)
    batting_form_index = Column(Float, nullable=True)
    bowling_form_index = Column(Float, nullable=True)
    pitch_adjusted_score = Column(Float, nullable=True)

    last_updated = Column(DateTime, nullable=False)

    match = relationship(Match)
    team = relationship(Team)
    innings = relationship(Innings)
    over = relationship(Over)
