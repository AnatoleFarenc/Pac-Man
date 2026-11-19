"""End-of-game menu screen with fade-in score display."""

import pygame as pg
import time as _t
from typing import Sequence
from ..game.states import GameState
from .base import Menu
from .items import MenuItem
from ..config.config import (
    T_END_TIME,
    CONTENT_END_TIME
)


class EndMenu(Menu):
    """Victory / game-over overlay that fades in over the last game frame."""

    def __init__(
            self,
            title: str,
            items: Sequence[MenuItem],
            window_size: tuple[int, int]
    ) -> None:
        """Initialize the end menu.

        Args:
            title: Title string (e.g. "VICTORY" or "GAME OVER").
            items: Sequence containing the continue prompt item.
            window_size: ``(width, height)`` of the display window in pixels.
        """
        super().__init__(title, items, window_size)
        self.score: int = 0
        self.level: int = 0
        self._progress: float = 0.0
        self.done: bool = False
        self._overlay = pg.Surface(window_size)
        self._overlay.fill((0, 0, 0))

    @property
    def _heading_font(self) -> pg.Font:
        return self.subtitle_font

    @property
    def _delta_scale(self) -> float:
        return 0.6

    def render(self, screen: pg.Surface, time: float) -> None:
        """Fade in the overlay, then reveal title and score.

        Args:
            screen: Target pygame surface.
            time: Accumulated game time (unused; progress is self-managed).
        """
        p = self._progress

        self._overlay.set_alpha(int(min(p * 4, 1.0) * 255))
        screen.blit(self._overlay, (0, 0))

        # Title and content spawn
        if p > T_END_TIME:
            self._draw_title(screen=screen)
        if p > CONTENT_END_TIME:
            self._draw_content(screen=screen)

    def _draw_content(self, screen: pg.Surface) -> None:
        """Render the level, score, and a blinking continue prompt.

        Args:
            screen: Target pygame surface.
        """
        font = self.item_font

        level_msg = f"Level {self.level}"
        level_x = (self.w - font.size(level_msg)[0]) // 2
        level_y = int(self.h / 3.3)
        self._draw_element(
            text=level_msg,
            screen=screen,
            font=font,
            coords=(level_x, level_y)
        )

        score_label = "Your score:"
        score_label_x = (self.w - font.size(score_label)[0]) // 2
        score_label_y = int(self.h / 2.4)
        self._draw_element(
            text=score_label,
            screen=screen,
            font=font,
            coords=(score_label_x, score_label_y)
        )

        score_str = str(self.score)
        score_x = (self.w - font.size(score_str)[0]) // 2
        score_y = int(self.h / 2)
        self._draw_element(
            text=score_str,
            screen=screen,
            font=font,
            coords=(score_x, score_y)
        )

        if self._progress > 0.50:
            prompt = self.items[0].label
            prompt_x = (self.w - self.score_font.size(prompt)[0]) // 2
            prompt_y = int(self.h / 1.4)
            if int(_t.time() * 1.4) % 2 == 0:
                self._draw_element(
                    text=prompt,
                    screen=screen,
                    font=self.score_font,
                    coords=(prompt_x, prompt_y)
                )

    def handle_key(
            self,
            state: GameState,
            key: int,  # noqa: ARG002
            first: bool,  # noqa: ARG002
            delay: float,  # noqa: ARG002
            tot_t: float  # noqa: ARG002
    ) -> GameState:
        """Mark the end screen as done once the animation has progressed."""
        if self._progress >= 0.5:
            self.done = True
        return state
