"""How-to-play menu screen showing the game controls."""

import pygame as pg
from math import sin
from typing import Sequence
from ..game.states import GameState
from .base import Menu
from .items import MenuItem


HOWTO = [
    ("W, A, S, D,", "Move/Strafe"),
    ("MOUSE", "Rotate camera"),
    ("Esc", "Pause/Resume"),
]


class HowToMenu(Menu):
    """Menu that shows the player the game controls."""

    def __init__(
            self,
            title: str,
            items: Sequence[MenuItem],
            window_size: tuple[int, int]
    ) -> None:
        """Initialize the how-to-play menu."""
        super().__init__(title, items, window_size)

    @property
    def _heading_font(self) -> pg.Font:
        """Use the smaller subtitle font for the how-to-play title."""

        return self.subtitle_font

    @property
    def _delta_scale(self) -> float:
        """Reduced bob amplitude for the how-to-play screen."""

        return 0.6

    def render(self, screen: pg.Surface, time: float) -> None:
        """Draw the background, title, content, and ghost bar each frame.

        Args:
            screen: Target pygame surface.
            time: Accumulated game time used to animate the title bob.
        """

        self.delta = sin(time) * self._delta_scale
        # gradient_background(screen=screen, color=self.bg_color)
        self._draw_title(screen=screen)
        self._draw_content(screen=screen)

    def draw_back_btn(self, screen: pg.Surface) -> None:
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

    def get_char_cheat(self) -> list[pg.Surface]:
        v_surf = self.command_font.render("V", True, self.font_color)
        return [
            pg.transform.rotate(v_surf, 180),
            pg.transform.rotate(v_surf, 0),
            pg.transform.rotate(v_surf, 270),
            pg.transform.rotate(v_surf, 90)
        ]

    def draw_arrow(self, screen: pg.Surface,
                   arrows: list[pg.Surface],
                   x: int, y: int) -> None:
        comma = self.command_font.render(", ", True, self.font_color)
        for i, arrow in enumerate(arrows):
            rect = arrow.get_rect(midleft=(x,
                                           y +
                                           self.command_font.get_height()
                                           // 2))
            screen.blit(arrow, rect)
            x = rect.right + 2
            if i < len(arrows) - 1:
                comma_rect = comma.get_rect(midleft=(x, y +
                                            self.command_font.get_height()
                                            // 2))
                screen.blit(comma, comma_rect)
                x = comma_rect.right + 2

    def _draw_cheat_row(self, screen: pg.Surface, x: int, y: int) -> None:
        arrow = self.get_char_cheat()
        up = arrow[0]
        down = arrow[1]
        left = arrow[2]
        right = arrow[3]

        cheat = {
            "ADD LIFE":          [up, up, down, down, left, right],
            "GHOST VULNERABLE":  [left, right, left, right, left],
            "INVINCIBILITY ON":  [up, right, down, left, up, right, down],
            "INVINCIBILITY OFF": [up, up, up],
            "FREEZE GHOSTS":     [down, down, up, up, down, right, left],
            "UNFREEZE GHOSTS":   [down, down, down],
            "NEXT LEVEL":        [up, right, up, left, down, right,
                                  down],
        }

        font = self.command_font

        for name, sequ in cheat.items():
            self.draw_arrow(screen, sequ, x, y)
            self._draw_element(
                text=name,
                screen=screen,
                font=self.command_font,
                coords=(self.w // 4 + self.w // 3, y)
            )
            y += int(font.get_linesize() * 1.3)

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the control list onto *screen*.

        Args:
            screen: Target pygame surface.
        """
        font = self.command_font
        y = int(self.h / 3.5)

        arrow = self.get_char_cheat()
        up = arrow[0]
        down = arrow[1]
        left = arrow[2]
        right = arrow[3]
        arrow_key = [up, left, down, right]

        for key, action in HOWTO:
            x = self.w // 4
            self._draw_element(text=key, screen=screen,
                               font=font, coords=(x, y))
            if key == "W, A, S, D,":
                x += font.size(key)[0] + font.size("A")[0]
                self.draw_arrow(screen, arrow_key, x, y)
                x = self.w // 4
            x += self.w // 3
            self._draw_element(text=action,
                               screen=screen, font=font, coords=(x, y))
            y += int(font.get_linesize() * 1.3)

        self._draw_cheat_row(screen=screen, x=self.w // 4, y=y)

        self.draw_back_btn(screen)

    def handle_key(
            self,
            state: GameState,
            key: int,
            first: bool,
            delay: float,
            tot_t: float
    ) -> GameState:
        """Return to the previous screen when Enter is pressed.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            The action associated with the selected item, or *state* unchanged.
        """

        if key == pg.K_RETURN:
            state = self.items[self.sel_item].action

        return state
