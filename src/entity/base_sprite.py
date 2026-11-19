"""Abstract base class shared by all sprite types (3-D view and mini-map)."""

import numpy as np
import numpy.typing as npt
import pygame as pg
from typing import Any, List, Tuple, Optional
from ..config.config import ANIM_FPS


class BaseSprite:
    """Minimal base shared by all sprite types (3-D view and mini-map).

    Handles world position, active state, animation bookkeeping, and
    texture loading. Subclasses are responsible for their own ``draw``
    implementation.
    """

    def __init__(self, x: float, y: float) -> None:
        """Set up world position, animation state, and display attributes.

        Args:
            x: Initial world X coordinate.
            y: Initial world Y coordinate.
        """

        self.is_active = True

        # position
        self.x = x
        self.y = y

        # display
        self.bob_anime_activate = True
        self.texture: Optional[npt.NDArray[np.uint8]] = None
        self.texture_alpha: Optional[npt.NDArray[np.uint8]] = None
        self._anim_frames: List[Any] = []
        self._anim_curr_frames = self._anim_frames
        self._anim_index = 0
        self._anim_timer = 0.0
        self._anim_fps = ANIM_FPS

    def _load_textures(
            self,
            path_list: List[str]
            ) -> List[Tuple[npt.NDArray[np.uint8], npt.NDArray[np.uint8]]]:
        """Load RGBA textures from a list of paths into NumPy arrays.

        Args:
            path_list: File-system paths to the texture images.

        Returns:
            List of (rgb_array, alpha_array) tuples.
        """

        frames = []
        for path in path_list:
            surf = pg.image.load(path).convert_alpha()
            rgb = pg.surfarray.array3d(surf)
            alpha = pg.surfarray.array_alpha(surf)
            frames.append((rgb, alpha))
        return frames

    def play_anim(self, dt: float) -> None:
        """Advance the animation by *dt* seconds and update
        the current texture.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """

        if not self._anim_curr_frames:
            return
        self._anim_timer += dt
        if self._anim_timer >= 1.0 / self._anim_fps:
            self._anim_timer = 0.0
            self._anim_index = ((self._anim_index + 1) %
                                len(self._anim_curr_frames))
        self.texture, self.texture_alpha = self._anim_curr_frames[
            self._anim_index]
