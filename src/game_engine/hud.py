"""In-game heads-up display renderer for score, lives, level, and timer."""

import pygame as pg
from ..config.config import (
    FONT, FONT_COLOR, OUT_COLOR, OUT_RATIO, PAC_MENU
)
from ..menus.helpers import outlined_text
from .player import Player


class Hud:
    """Renders the in-game overlay showing score,
    lives, level, and remaining time."""

    def __init__(self, window_size: tuple[int, int]) -> None:
        """Create the HUD font scaled to *window_size*.

        Args:
            window_size: ``(width, height)`` of the render surface in pixels.
        """

        self.w = window_size[0]
        self.h = window_size[1]

        self.scale = min([self.w, self.h])
        self.font: pg.Font = pg.font.Font(FONT, int(self.scale/24))
        self.thickness = int(self.font.get_linesize()*OUT_RATIO)

        icon_size = self.scale // 22
        self.hp_icon: pg.Surface = pg.transform.scale(
            pg.image.load(PAC_MENU),
            (icon_size, icon_size)
        )

    def _draw_hp_icon(
            self,
            screen: pg.Surface,
            icon_x: int,
            icon_y: int
    ) -> None:
        """Blit one life icon at ``(icon_x, icon_y)``."""

        screen.blit(self.hp_icon, (icon_x, icon_y))

    def _draw_element(
            self,
            text: str,
            screen: pg.Surface,
            coords: tuple[int, int]
    ) -> None:
        """Render a single outlined text element at *coords* on *screen*.

        Args:
            text: String to render.
            screen: Target pygame surface.
            coords: ``(x, y)`` pixel position of the text.
        """

        outlined_text(
            text=text,
            screen=screen,
            coords=coords,
            font=self.font,
            thickness=self.thickness,
            outline_color=OUT_COLOR
        )
        screen.blit(
                self.font.render(
                    text=text,
                    antialias=True,
                    color=FONT_COLOR
                ),
                dest=coords
            )

    def render(
            self,
            screen: pg.Surface,
            player: Player,
            level: int,
            time: float
    ) -> None:
        """Draw the complete HUD (level, score, lives, timer) onto *screen*.

        Args:
            screen: Target pygame surface.
            player: Player instance used to read score and HP.
            level: Current level number to display.
            time: Remaining time in seconds to display.
        """

        top_text_y = self.h // 30

        # draw level
        level_str = f"LVL {level}"
        level_x = int(self.w * 0.2)
        self._draw_element(level_str, screen, (level_x, top_text_y))

        # draw score
        score_str = f"SCORE: {player.score}"
        score_x = int((self.w - self.font.size(score_str)[0]) / 2)
        self._draw_element(score_str, screen, (score_x, top_text_y))

        # draw timer
        timer_str = f"Time: {int(time)}"
        timer_x = int(self.w * 0.80)
        self._draw_element(timer_str, screen, (timer_x, top_text_y))

        # draw hp icons
        hp_x = int(self.w * 0.95)
        hp_y = int(self.h - top_text_y - self.hp_icon.get_height())
        for _ in range(player.hp):
            self._draw_hp_icon(screen, hp_x, hp_y)
            hp_x -= int(self.hp_icon.get_width() * 1.1)

    def draw_damage_flash(self, screen: pg.Surface) -> None:
        """Overlay a red transparent flash on *screen* to signal damage."""
        flash: pg.Surface = pg.Surface(screen.get_size())
        flash.fill((255, 0, 0))
        flash.set_alpha(80)
        screen.blit(flash, (0, 0))
