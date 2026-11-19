"""Mini-map animated sprite for player and ghost overlay icons."""

import glob
from typing import Tuple, List
import pygame as pg

from .base_sprite import BaseSprite
from ..config.config import (
    SPRITE_SIZE_M
)


class Sprite_mini_map(BaseSprite):
    """Animated sprite displayed on the mini-map overlay.

    Loads a sequence of PNG frames from a directory and renders them
    as a scaled, rotatable sprite centred on a mini-map cell position.
    """

    def __init__(self, x: float, y: float, frames_path: str) -> None:
        """Initialize the mini-map sprite and load its animation frames.

        Args:
            x: Initial world X coordinate of the sprite.
            y: Initial world Y coordinate of the sprite.
            frames_path: Directory containing the PNG animation frames,
                sorted alphabetically to determine playback order.
        """
        super().__init__(x, y)
        self.bob_anime_activate = False

        frames = sorted(glob.glob(f"{frames_path}/*.png"))
        self._anim_frames = [self._load_textures(frames)]
        self._anim_curr_frames = self._anim_frames[0]
        self._anim_fps = 4
        self._all_pg_frames: List[List[pg.Surface]] = [
            [pg.image.load(p).convert_alpha() for p in frames]
        ]
        self._pg_frames: List[pg.Surface] = self._all_pg_frames[0]

    def add_animation(self, frames_path: str) -> None:
        """Append an additional animation set loaded from *frames_path*.

        Args:
            frames_path: Directory containing PNG frames sorted alphabetically.
        """
        frames = sorted(glob.glob(f"{frames_path}/*.png"))
        self._anim_frames.append(self._load_textures(frames))
        self._all_pg_frames.append(
            [pg.image.load(p).convert_alpha() for p in frames]
        )

    def change_frames(self, idx: int) -> None:
        """Switch the active animation set to index *idx*,
        wrapping to 0 if out of range.

        Args:
            idx: Index of the animation set to activate.
        """
        target = idx if idx < len(self._anim_frames) else 0
        if self._anim_curr_frames is not self._anim_frames[target]:
            self._anim_curr_frames = self._anim_frames[target]
            self._pg_frames = self._all_pg_frames[target]
            self._anim_index = 0

    def draw(self, surface: pg.Surface, s_pos: Tuple[float, float],
             size_cell: float, dt: float, angle: float = 0.0) -> None:
        """Draw the current animation frame onto the mini-map surface.

        Converts the world position to pixel coordinates, advances the
        animation, scales the frame to ``PACMAN_SIZE_M * 2`` pixels, and
        blits it centred and rotated at *angle* degrees.

        Args:
            surface: The pygame surface to draw onto (the mini-map box).
            s_pos: Sprite position in world units ``(x, y)``.
            size_cell: Pixel size of one mini-map cell, used to convert
                world units to pixel coordinates.
            dt: Elapsed time in seconds since the last frame.
            angle: Clockwise rotation angle in degrees (default ``0.0``).
        """
        px, py = s_pos
        px *= size_cell
        py *= size_cell

        self.play_anim(dt)

        frame = self._pg_frames[self._anim_index]
        size = int(size_cell * SPRITE_SIZE_M)
        scaled = pg.transform.scale(frame, (size, size))
        rotated = pg.transform.rotate(scaled, -angle)
        rect = rotated.get_rect(center=(px, py))
        surface.blit(rotated, rect)
