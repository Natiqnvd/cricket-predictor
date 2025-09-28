from enum import Enum

class MatchFormat(Enum):
    TEST = "Test"
    ODI = "ODI"
    T20 = "T20"
    T10 = "T10"

class TossDecision(Enum):
    BAT = "bat"
    FIELD = "field"

class WicketType(Enum):
    BOWLED = "bowled"
    CAUGHT = "caught"
    LBW = "lbw"
    RUN_OUT = "run_out"
    STUMPED = "stumped"
    HIT_WICKET = "hit_wicket"
    RETIRED = "retired"
    OTHER = "other"

class PlayerRole(Enum):
    BATSMAN = "batsman"
    BOWLER = "bowler"
    WICKET_KEEPER = "wicket_keeper"
    ALL_ROUNDER = "all_rounder"

class BallPhase(Enum):
    POWER_PLAY = "power_play"
    MIDDLE = "middle"
    DEATH = "death"