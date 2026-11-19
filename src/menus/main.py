"""Main menu screen shown at game startup."""

import pygame as pg
from typing import Sequence
from ..game.states import GameState
from .base import Menu
from .items import MenuItem


class MainMenu(Menu):
    """The primary game menu with navigation to all other screens."""

    def __init__(
            self,
            title: str,
            items: Sequence[MenuItem],
            window_size: tuple[int, int]
    ) -> None:
        """Initialize the main menu."""

        super().__init__(title, items, window_size)

    @property
    def _delta_scale(self) -> float:
        """Reduced bob amplitude for the how-to-play screen."""

        return 0.6

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the vertically-stacked item list with the selection icon.

        Args:
            screen: Target pygame surface.
        """

        y_delta = 0
        for i, item in enumerate(self.items):

            s_h = self.item_font.get_height()
            l_h = self.sel_font.get_height()

            if i == self.sel_item:
                font = self.sel_font
                font_delta = l_h - s_h
            else:
                font = self.item_font
                font_delta = 0

            item_y = int(self.h//2.25 + y_delta - font_delta//2)
            item_x = (self.w - font.size(item.label)[0])//2

            if i == self.sel_item:
                icon_x = item_x - int(self.sel_icon.width*1.5)
                icon_y = (item_y + font.get_height()//2
                          - self.sel_icon.height//2)
                self._draw_icon(screen=screen, icon_x=icon_x, icon_y=icon_y)

            self._draw_element(
                text=item.label,
                screen=screen,
                font=font,
                coords=(item_x, item_y),
                shadow=True,
                outline=True
            )
            y_delta += int(font.get_linesize()*1.05)

    def handle_key(
            self,
            state: GameState,
            key: int,
            first: bool,
            delay: float,
            tot_t: float
    ) -> GameState:
        """Move selection or confirm with Enter; support
        key-repeat via *delay*/*tot_t*.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            New game state when Enter is pressed, otherwise *state* unchanged.
        """

        if (delay > 0.1 and tot_t > 0.8) or first:
            match key:
                case pg.K_UP:
                    self.sel_item = (self.sel_item - 1) % len(self.items)
                case pg.K_DOWN:
                    self.sel_item = (self.sel_item + 1) % len(self.items)
                case pg.K_RETURN:
                    state = self.items[self.sel_item].action

        self.sel_label = self.items[self.sel_item].label
        return state
