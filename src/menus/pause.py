"""Pause menu overlay displayed when the player presses Escape during play."""

import pygame as pg
from typing import Sequence
from math import sin
from ..game.states import GameState
from .base import Menu, Item


class PauseMenu(Menu):
    """Semi-transparent pause overlay with resume,
    main menu, and quit options."""

    def __init__(
            self,
            title: str,
            items: Sequence[Item],
            window_size: tuple[int, int]
    ) -> None:
        """Initialize the pause menu."""

        super().__init__(title, items, window_size)

    @property
    def _heading_font(self) -> pg.Font:
        """Use the smaller item font for the pause title."""
        return self.item_font

    @property
    def _delta_scale(self) -> float:
        """Reduced bob amplitude for the pause screen."""
        return 0.6

    def render(self, screen: pg.Surface, time: float) -> None:
        """Draw a dark overlay, then the title and item list.

        Args:
            screen: Target pygame surface (the already-rendered game frame).
            time: Accumulated game time used to animate the title bob.
        """

        self.delta = sin(time) * self._delta_scale

        black_overlay: pg.Surface = pg.Surface(screen.get_size())
        black_overlay.set_alpha(150)
        screen.blit(black_overlay)
        self._draw_title(screen=screen)
        self._draw_content(screen=screen)

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the pause-menu item list with the selection icon.

        Args:
            screen: Target pygame surface.
        """

        y_delta = 0
        w, h = screen.get_size()
        for i, item in enumerate(self.items):

            s_h = self.score_font.get_height()
            l_h = self.pause_sel_font.get_height()

            if i == self.sel_item:
                font = self.pause_sel_font
                font_delta = l_h - s_h
            else:
                font = self.score_font
                font_delta = 0

            item_y = int(h//2.15 + y_delta - font_delta//2)
            item_x = (w - font.size(item.label)[0])//2

            if i == self.sel_item:
                icon_x = item_x - int(self.psel_icon.width*1.5)
                icon_y = (item_y + font.get_height()//2
                          - self.psel_icon.height//2)
                self._draw_icon(
                    screen=screen, icon_x=icon_x, icon_y=icon_y, pause=True)

            self._draw_element(
                text=item.label,
                screen=screen,
                font=font,
                coords=(item_x, item_y)
            )
            y_delta += int(font.get_linesize()*1.05)

    def _draw_title(
            self,
            screen: pg.Surface,
            shadow: bool = True,
            outline: bool = True,
    ) -> None:
        """Draw the pause title vertically centred on *screen*.

        Args:
            screen: Target pygame surface.
            shadow: If ``True``, draw a drop shadow behind the title.
            outline: If ``True``, draw a pixel-thick outline around the title.
        """

        w, h = screen.get_size()
        title_x = (w - self._heading_font.size(self.title)[0])//2
        title_y = int(h/3.3) + int(self.delta * self.h//100)
        self._draw_element(
            text=self.title,
            screen=screen,
            font=self._heading_font,
            coords=(title_x, title_y),
            shadow=shadow,
            outline=outline
        )

    def handle_key(
        self,
        state: GameState,
        key: int,
        first: bool,
        delay: float,
        tot_t: float
    ) -> GameState:
        """Handle item navigation, confirmation, and Escape to resume.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            New game state when a selection is confirmed, otherwise *state*.
        """

        if (delay > 0.1 and tot_t > 0.8) or first:
            match key:
                case pg.K_UP:
                    self.sel_item = (self.sel_item - 1) % len(self.items)
                case pg.K_DOWN:
                    self.sel_item = (self.sel_item + 1) % len(self.items)
                case pg.K_RETURN:
                    state = self.items[self.sel_item].action
                case pg.K_ESCAPE:
                    state = GameState.PLAY

        self.sel_label = self.items[self.sel_item].label
        return state
