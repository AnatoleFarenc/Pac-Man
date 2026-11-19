"""Screen-space rendering utilities for background effects."""

import pygame


def gradient_background(
        screen: pygame.Surface,
        color: tuple[int, int, int]
) -> None:
    """Fill *screen* with a vertical gradient derived from *color*.

    The top of the screen uses the full *color* value; brightness decreases
    linearly toward the bottom.

    Args:
        screen: The pygame surface to fill.
        color: Base RGB color for the top of the gradient.
    """

    r, g, b = color
    r_g, g_g, b_g = r, g, b

    for i in range(screen.height):
        pygame.draw.line(
            surface=screen,
            color=(r_g, g_g, b_g),
            start_pos=(0, i),
            end_pos=(screen.width - 1, i)
        )
        factor = min(1.0, 1 - i / (screen.height - 1) + 0.2)
        r_g = int(r * factor)
        g_g = int(g * factor)
        b_g = int(b * factor)
