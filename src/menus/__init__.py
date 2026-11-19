"""Menu sub-package: base class, factory, and shared text helpers."""

from typing import Sequence
from ..config.data import HighScores
from ..game.states import GameState
from .base import Menu, Item
from .items import MenuItem
from .helpers import outlined_text
from .end import EndMenu
from .high_scores import HighScoresMenu, Enter_Name_Menu
from .main import MainMenu
from .pause import PauseMenu
from .how_to import HowToMenu
from .settings import SettingsMenu
from ..interfaces.setting import Setting


def build_menus(
    window_size: tuple[int, int],
    config: Setting,
    hi_scores: HighScores
) -> dict[GameState, Menu]:
    """Construct and return a mapping of game states to their menu instances.

    Args:
        window_size: Current window dimensions ``(width, height)`` in pixels.
        config: Game configuration used to populate settings-aware menus.
        hi_scores: Current high-score data passed to the scores screen.

    Returns:
        A dict mapping each menu ``GameState`` to its ``Menu`` instance.
    """

    menus: dict[GameState, Menu] = dict()

    # main menu
    main_items: Sequence[MenuItem] = [
        MenuItem(label="Play", action=GameState.PLAY),
        MenuItem(label="How to play", action=GameState.HOW_TO),
        MenuItem(label="High scores", action=GameState.HIGH_SCORES),
        MenuItem(label="Settings", action=GameState.SETTINGS_MENU),
        MenuItem(label="Quit", action=GameState.QUIT)
    ]
    menus[GameState.MAIN_MENU] = MainMenu(
        title="PAC-MAN",
        items=main_items,
        window_size=window_size
    )

    # highscores menu
    highscores_items: Sequence[MenuItem] = [
        MenuItem(label='Back', action=GameState.MAIN_MENU)
    ]
    menus[GameState.HIGH_SCORES] = HighScoresMenu(
        title='HIGH SCORES',
        items=highscores_items,
        window_size=window_size,
        high_scores=hi_scores.scores
    )

    # settings menu
    settings_item: Sequence[MenuItem] = [
        MenuItem(label="Back", action=GameState.MAIN_MENU)
    ]
    menus[GameState.SETTINGS_MENU] = SettingsMenu(
        title='SETTINGS',
        items=settings_item,
        window_size=window_size,
        setting=config
    )

    # pause menu
    pause_items: Sequence[Item] = [
        MenuItem(label="Resume", action=GameState.PLAY),
        MenuItem(label="Main Menu", action=GameState.MAIN_MENU),
        # MenuItem(label="Cheats", action=GameState.CHEAT_MENU),
        MenuItem(label="Quit", action=GameState.QUIT)
    ]
    menus[GameState.PAUSE_MENU] = PauseMenu(
        title="PAUSE",
        items=pause_items,
        window_size=window_size
    )

    # enter name menu
    menus[GameState.ENTER_NAME] = Enter_Name_Menu(
        title='HIGH SCORE',
        items=[MenuItem(label='', action=GameState.HIGH_SCORES)],
        window_size=window_size,
        high_scores=hi_scores.scores
    )

    how_to_items: Sequence[MenuItem] = [
        MenuItem(label='Back', action=GameState.MAIN_MENU)
    ]
    menus[GameState.HOW_TO] = HowToMenu(
        title='How To Play',
        items=how_to_items,
        window_size=window_size
    )

    # game over screen
    menus[GameState.GAME_OVER] = EndMenu(
        title="GAME OVER",
        items=[MenuItem(label="Press any key to continue",
                        action=GameState.GAME_OVER)],
        window_size=window_size
    )

    # victory screen
    menus[GameState.VICTORY] = EndMenu(
        title="YOU WON!",
        items=[MenuItem(label="Press any key to continue",
                        action=GameState.VICTORY)],
        window_size=window_size
    )

    # final victory screen
    menus[GameState.FINAL_VICTORY] = EndMenu(
        title="YOU WON THE GAME!",
        items=[MenuItem(label="Press any key to continue",
                        action=GameState.FINAL_VICTORY)],
        window_size=window_size
    )

    return menus


__all__ = ["Menu", "build_menus", "outlined_text"]
