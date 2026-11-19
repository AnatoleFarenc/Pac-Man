"""Game-state enumeration used to drive the top-level state machine."""

from enum import Enum, auto


class GameState(Enum):
    """All possible states of the game's top-level finite state machine."""

    MAIN_MENU = auto()
    PLAY = auto()
    HOW_TO = auto()
    HIGH_SCORES = auto()
    SETTINGS_MENU = auto()
    QUIT = auto()
    PAUSE_MENU = auto()
    CHEAT_MENU = auto()
    VICTORY = auto()
    FINAL_VICTORY = auto()
    GAME_OVER = auto()
    ENTER_NAME = auto()
