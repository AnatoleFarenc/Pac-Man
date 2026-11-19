"""Abstract base class and shared drawing helpers for all game menus."""
import pygame as pg
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from math import cos, sin, pi
from typing import Sequence
from ..config.config import (
    FONT, FONT_COLOR, OUT_COLOR, OUT_RATIO,
    BG_COLOR, SH_ANGLE, SH_SIZE,
    PAC_MENU, PAC_SHADOW, GHOST_SPRITES
)
from ..game.states import GameState
from .helpers import outlined_text, text_shadow


@dataclass
class Item:
    """Data container pairing a menu label with its target game state."""

    label: str
    action: GameState


class Menu(ABC):
    """Abstract base class for all game menus.

    Provides shared font loading, icon/ghost assets, and template-method
    rendering.  Subclasses implement ``_draw_content`` and ``handle_key``.
    """

    def __init__(
            self,
            title: str,
            items: Sequence[Item],
            window_size: tuple[int, int]
    ) -> None:
        """Set up shared menu assets (fonts, icons, ghosts) from *window_size*.

        Args:
            title: Title string displayed at the top of the menu.
            items: Sequence of selectable menu items.
            window_size: ``(width, height)`` of the display window in pixels.
        """

        self.title: str = title
        self.items: Sequence[Item] = items
        self.w: int = window_size[0]
        self.h: int = window_size[1]
        self.scale = min([self.w, self.h])
        self.sel_item: int = 0
        self.sel_label: str = self.items[self.sel_item].label
        self.sh_angle: int = SH_ANGLE
        self.sh_size: float = SH_SIZE
        self.out_ratio: float = OUT_RATIO
        self.delta: float = 0
        self.font_color: tuple[int, int, int] = FONT_COLOR
        self.out_color: tuple[int, int, int] = OUT_COLOR
        self.bg_color: tuple[int, int, int] = BG_COLOR

        self.sel_icon: pg.Surface = pg.transform.scale(
            pg.image.load(PAC_MENU),
            (self.scale//15, self.scale//15)
        )
        self.sel_icon_shadow: pg.Surface = pg.transform.scale(
            pg.image.load(PAC_SHADOW),
            (self.scale//15, self.scale//15)
        )
        self.sel_icon_shadow.set_alpha(130)

        self.psel_icon: pg.Surface = pg.transform.scale(
            pg.image.load(PAC_MENU),
            (self.scale//20, self.scale//20)
        )
        self.psel_icon_shadow: pg.Surface = pg.transform.scale(
            pg.image.load(PAC_SHADOW),
            (self.scale//20, self.scale//20)
        )
        self.psel_icon_shadow.set_alpha(130)

        self.ghosts: list[list[pg.Surface]] = list()
        ghosts_sprites: list[list[str]] = GHOST_SPRITES
        for ghost in ghosts_sprites:
            self.ghosts.append([
                pg.transform.scale(
                    pg.image.load(ghost[0]),
                    (self.scale//15, self.scale//15)
                ),
                pg.transform.scale(
                    pg.image.load(ghost[1]),
                    (self.scale//15, self.scale//15)
                )
            ])

    # FONTS

    @cached_property
    def title_font(self) -> pg.Font:
        """Large title font sized to 1/5 of the screen's smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/5))

    @cached_property
    def subtitle_font(self) -> pg.Font:
        """Subtitle font sized to 1/9 of the screen's smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/9))

    @cached_property
    def item_font(self) -> pg.Font:
        """Normal item font sized to 1/16 of the screen's smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/16))

    @cached_property
    def sel_font(self) -> pg.Font:
        """Selected-item font sized to 1/13 of the screen's
        smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/13))

    @cached_property
    def small_item_font(self) -> pg.Font:
        """Normal item font sized to 1/16 of the screen's
        smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/30))

    @cached_property
    def small_sel_font(self) -> pg.Font:
        """Selected-item font sized to 1/13 of the screen's
        smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/25))

    @cached_property
    def pause_sel_font(self) -> pg.Font:
        """Pause-menu selected-item font sized to 1/20 of the screen's
        smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/20))

    @cached_property
    def score_font(self) -> pg.Font:
        """Score font sized to 1/24 of the screen's smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/24))

    @cached_property
    def command_font(self) -> pg.Font:
        """Command font sized to 1/30 of the screen's smaller dimension."""
        return pg.font.Font(FONT, int(self.scale/30))

    # ROLE-BASED FONTS

    @property
    def _heading_font(self) -> pg.Font:
        """Font used for the menu title; defaults to ``title_font``."""
        return self.title_font

    # --- delta scale: controls title/ghost bob amplitude ---

    @property
    def _delta_scale(self) -> float:
        """Amplitude multiplier for the title bob animation;
        defaults to ``1.0``."""
        return 1.0

    # RENDER TEMPLATE

    def render(self, screen: pg.Surface, time: float) -> None:
        """Draw the background, title, content, and ghost bar each frame.

        Args:
            screen: Target pygame surface.
            time: Accumulated game time used to animate the title bob.
        """

        self.delta = sin(time) * self._delta_scale
        self._draw_title(screen=screen)
        self._draw_content(screen=screen)
        self._draw_ghosts(screen=screen, time=time)

    @abstractmethod
    def _draw_content(self, screen: pg.Surface) -> None:
        """Render menu-specific content onto *screen*; implemented
        by each subclass.

        Args:
            screen: Target pygame surface.
        """

        pass

    @abstractmethod
    def handle_key(
        self,
        state: GameState,
        key: int,
        first: bool,
        delay: float,
        tot_t: float
    ) -> GameState:
        """Process a key press and return the next game state.

        Args:
            state: The current game state.
            key: Pygame key constant for the pressed key.
            first: ``True`` on the first frame a key is held.
            delay: Time the key has been held in seconds.
            tot_t: Total time elapsed since the key was pressed.

        Returns:
            The new game state (unchanged if no transition is triggered).
        """

        pass

    # SHARED HELPERS

    def _draw_ghosts(self, screen: pg.Surface, time: float) -> None:
        """Draw the animated ghost row at the bottom-right of the screen.

        Args:
            screen: Target pygame surface.
            time: Accumulated game time used to cycle animation frames.
        """

        ghosts_y = int(screen.height*0.85)
        ghosts_y += int(self.delta * screen.height//200)
        ghosts_x = int(screen.width*0.75)
        j: int = int((time % 0.2) / 0.1) % 2
        for ghost in self.ghosts:
            screen.blit(ghost[j], (ghosts_x, ghosts_y))
            ghosts_x += int(ghost[j].width*1.2)

    def _draw_icon(
            self,
            screen: pg.Surface,
            icon_x: int,
            icon_y: int,
            pause: bool = False
    ) -> None:
        """Draw the Pac-Man selection icon and its drop shadow at
        the given position.

        Args:
            screen: Target pygame surface.
            icon_x: Horizontal pixel position of the icon.
            icon_y: Vertical pixel position of the icon.
            pause: If ``True``, use the smaller pause-menu icon variant.
        """

        if pause:
            icon = self.psel_icon
            shadow = self.psel_icon_shadow
        else:
            icon = self.sel_icon
            shadow = self.sel_icon_shadow

        sh_size = int(icon.width * self.sh_size)
        icon_sh_x_off = int(cos(self.sh_angle * (pi/180)) * sh_size)
        icon_sh_y_off = int(sin(self.sh_angle * (pi/180)) * sh_size)
        screen.blit(
            shadow,
            (icon_x + icon_sh_x_off, icon_y - icon_sh_y_off)
        )
        screen.blit(icon, (icon_x, icon_y))

    def _draw_element(
        self,
        text: str,
        screen: pg.Surface,
        font: pg.Font,
        coords: tuple[int, int],
        shadow: bool = True,
        outline: bool = True
    ) -> None:
        """Render a text element with optional shadow and outline at *coords*.

        Args:
            text: String to render.
            screen: Target pygame surface.
            font: Font used to render the text.
            coords: ``(x, y)`` pixel position of the text.
            shadow: If ``True``, draw a drop shadow behind the text.
            outline: If ``True``, draw a pixel-thick outline around the text.
        """

        if shadow:
            text_shadow(
                text=text,
                screen=screen,
                font=font,
                coords=coords,
                angle=self.sh_angle,
                size=self.sh_size
            )
        if outline:
            thickness = int(font.get_linesize()*self.out_ratio)
            outlined_text(
                text=text,
                screen=screen,
                coords=coords,
                font=font,
                thickness=thickness,
                outline_color=self.out_color
            )
        screen.blit(
            font.render(
                text=text,
                antialias=True,
                color=self.font_color
            ),
            dest=coords
        )

    def _draw_title(
            self,
            screen: pg.Surface,
            shadow: bool = True,
            outline: bool = True,
    ) -> None:
        """Draw the menu title centred near the top of *screen*.

        Args:
            screen: Target pygame surface.
            shadow: If ``True``, draw a drop shadow behind the title.
            outline: If ``True``, draw a pixel-thick outline around the title.
        """

        w, h = screen.get_size()
        title_x = (w - self._heading_font.size(self.title)[0])//2
        title_y = h//12 + int(self.delta * self.h//100)
        self._draw_element(
            text=self.title,
            screen=screen,
            font=self._heading_font,
            coords=(title_x, title_y),
            shadow=shadow,
            outline=outline
        )
