"""Text rendering helpers for outlines and drop shadows."""

import pygame as pg
from math import cos, sin, pi


def outlined_text(
        text: str,
        screen: pg.Surface,
        coords: tuple[int, int],
        font: pg.Font,
        thickness: int = 10,
        outline_color: str | tuple[int, int, int] = "black"
) -> None:
    """Blit *text* with a pixel-thick outline onto *screen* at *coords*.

    Renders the text eight times (cardinal and diagonal offsets) in
    *outline_color* to produce a solid border effect.

    Args:
        text: The string to render.
        screen: Target pygame surface.
        coords: ``(x, y)`` pixel position of the main text.
        font: Font used to render the text.
        thickness: Outline offset in pixels.
        outline_color: Color of the outline.
    """

    outline = font.render(
        text, antialias=True, color=outline_color
    )

    x, y = coords

    # blit outline (8 offsets: 4 cardinal and 4 diagonals)
    screen.blit(outline, (x - thickness, y))
    screen.blit(outline, (x + thickness, y))
    screen.blit(outline, (x, y - thickness))
    screen.blit(outline, (x, y + thickness))
    screen.blit(outline, (x - thickness, y - thickness))
    screen.blit(outline, (x - thickness, y + thickness))
    screen.blit(outline, (x + thickness, y - thickness))
    screen.blit(outline, (x + thickness, y + thickness))


def text_shadow(
        text: str,
        screen: pg.Surface,
        coords: tuple[int, int],
        font: pg.Font,
        angle: int,
        size: float,
        alpha: int = 130
) -> None:
    """Blit a semi-transparent shadow of *text* onto *screen*
    at an angular offset.

    Args:
        text: The string to render as a shadow.
        screen: Target pygame surface.
        coords: ``(x, y)`` pixel position of the main (non-shadow) text.
        font: Font used to render the shadow.
        angle: Direction of the shadow offset in degrees.
        size: Shadow distance as a fraction of the font line size.
        alpha: Opacity of the shadow surface (0–255).
    """

    shadow = font.render(
        text=text,
        antialias=True,
        color='black'
    )
    shadow.set_alpha(alpha)

    # compute shadow offset from angle
    shadow_size = int(font.get_linesize()*size)
    x, y = coords
    x = x + int(cos(angle*(pi/180))*shadow_size)
    y = y - int(sin(angle*(pi/180))*shadow_size)
    screen.blit(shadow, (x, y))
