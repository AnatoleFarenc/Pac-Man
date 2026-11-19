"""High-scores display and player name-entry menu screens."""

import pygame as pg
from typing import Sequence

from ..game.states import GameState
from .base import Menu
from .items import MenuItem


class HighScoresMenu(Menu):
    """Menu that displays the top-10 scores and a back button."""

    def __init__(
            self,
            title: str,
            items: Sequence[MenuItem],
            window_size: tuple[int, int],
            high_scores: list[dict[str, int]]
    ) -> None:
        """Initialize the high-scores menu with the current score list.

        Args:
            title: Title string displayed at the top.
            items: Sequence containing the back-button item.
            window_size: ``(width, height)`` of the display window in pixels.
            high_scores: List of ``{name: score}`` dicts in descending order.
        """
        super().__init__(title, items, window_size)
        self.high_scores: list[dict[str, int]] = high_scores

    @property
    def _heading_font(self) -> pg.Font:
        """Use the smaller subtitle font for the high-scores title."""
        return self.subtitle_font

    @property
    def _delta_scale(self) -> float:
        """Reduced bob amplitude for the high-scores screen."""
        return 0.6

    def _draw_scores(self, screen: pg.Surface) -> None:
        """Render the ranked score table onto *screen*.

        Args:
            screen: Target pygame surface.
        """

        font = self.score_font
        score_y = int(self.h/3.8)

        for i, score in enumerate(self.high_scores, 1):
            score_x = self.w//4

            self._draw_element(
                text=f"{i:>2}", screen=screen, font=font,
                coords=(score_x, score_y))
            score_x += self.w//20
            self._draw_element(
                text="-", screen=screen, font=font,
                coords=(score_x, score_y))
            score_x += self.w//20
            self._draw_element(
                text=f"{list(score.keys())[0]:<15}", screen=screen, font=font,
                coords=(score_x, score_y))
            score_x += int(self.w/3.8)
            self._draw_element(
                text="-", screen=screen, font=font,
                coords=(score_x, score_y))
            score_x += self.w//20
            self._draw_element(
                text=f"{list(score.values())[0]:>8}", screen=screen, font=font,
                coords=(score_x, score_y))
            score_y += int(font.get_linesize()*1.05)

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the score table and the back button.

        Args:
            screen: Target pygame surface.
        """

        self._draw_scores(screen=screen)

        font = self.item_font
        item_y = self.h - self.h//8
        item_x = (self.w - font.size(self.items[0].label)[0])//2

        icon_x = item_x - int(self.sel_icon.width*1.5)
        icon_y = item_y + int(self.h//20*0.1)
        self._draw_icon(screen=screen, icon_x=icon_x, icon_y=icon_y)

        self._draw_element(
            text=self.items[0].label,
            screen=screen,
            font=font,
            coords=(item_x, item_y)
        )

    def handle_key(
            self,
            state: GameState,
            key: int,
            first: bool,
            delay: float,
            tot_t: float
    ) -> GameState:
        """Return to the main menu when the player presses Enter.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            ``GameState.MAIN_MENU`` on Enter, otherwise *state* unchanged.
        """

        if key == pg.K_RETURN:
            return GameState.MAIN_MENU
        return state


class Enter_Name_Menu(Menu):
    """Menu that lets the player enter their name
    after achieving a high score."""

    def __init__(self, title: str, items: Sequence[MenuItem],
                 window_size: tuple[int, int],
                 high_scores: list[dict[str, int]]) -> None:
        """Initialize the name-entry menu with the current score list.

        Args:
            title: Title string displayed at the top.
            items: Sequence containing the confirm item.
            window_size: ``(width, height)`` of the display window in pixels.
            high_scores: Existing scores used to preview the ranking.
        """
        super().__init__(title, items, window_size)
        self.high_scores = high_scores
        self.name: str = ""
        self.score: int = 0
        self.rank: int = 0
        self._max_name_len = 10

    @property
    def _heading_font(self) -> pg.Font:
        """Use the smaller subtitle font for the name-entry title."""
        return self.subtitle_font

    @property
    def _delta_scale(self) -> float:
        """Reduced bob amplitude for the name-entry screen."""
        return 0.6

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the score preview with a blinking cursor
        at the player's rank.

        Args:
            screen: Target pygame surface.
        """
        font = self.score_font
        score_y = int(self.h / 3.8)

        preview = list(self.high_scores)
        preview.insert(self.rank, {"": self.score})
        preview = preview[:10]

        cursor = "|" if (pg.time.get_ticks() // 500) % 2 == 0 else " "

        for i, entry in enumerate(preview, 1):
            score_x = self.w // 4
            name = list(entry.keys())[0]
            val = list(entry.values())[0]

            self._draw_element(f"{i:>2}", screen, font, (score_x, score_y))
            score_x += self.w // 20
            self._draw_element("-", screen, font, (score_x, score_y))
            score_x += self.w // 20

            if i - 1 == self.rank:
                display = f"{self.name}{cursor}"
                self._draw_element(f"{display:<15}", screen, font, (score_x,
                                                                    score_y))
            else:
                self._draw_element(f"{name:<15}", screen, font, (score_x,
                                                                 score_y))

            score_x += int(self.w/3.8)
            self._draw_element("-", screen, font, (score_x, score_y))
            score_x += self.w // 20
            self._draw_element(f"{val:>8}", screen, font, (score_x, score_y))
            score_y += int(font.get_linesize() * 1.05)

    def handle_key(
            self,
            state: GameState,
            key: int,
            first: bool,
            delay: float,
            tot_t: float
    ) -> GameState:
        """Handle character input and confirm submission with Enter.

        Supports key-repeat for Backspace, filters to alphanumeric characters
        and spaces, and enforces the 15-character name length limit.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            ``GameState.HIGH_SCORES`` when a non-empty name is confirmed,
            otherwise *state* unchanged.
        """
        if key == pg.K_RETURN and self.name:
            return GameState.HIGH_SCORES
        if key == pg.K_BACKSPACE:
            if first or (delay > 0.4 and tot_t % 0.08 < 0.04):
                self.name = self.name[:-1]
        elif first and len(self.name) < self._max_name_len:
            if key == pg.K_SPACE:
                self.name += " "
            else:
                char = pg.key.name(key)
                if len(char) == 1 and (char.isalpha() or char.isdigit()):
                    self.name += char.upper()
        return state
