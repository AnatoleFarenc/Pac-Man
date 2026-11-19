"""Billboard sprite base class for the raycasting 3-D view."""

import numpy as np
import numpy.typing as npt
import math
import random
import pygame as pg
from ..config.config import (
    FOV,
    DIST_SHADE,
    SPRITE_SCALE,
    SPRITE_BOB_AMP,
    SPRITE_BOB_SPEED,
)
from ..interfaces.transform import HasTransform
from .base_sprite import BaseSprite


class Sprite(BaseSprite):
    """Base class for all billboard sprites rendered in the 3-D view.

    Handles world-space positioning, distance and angle computation relative
    to the player, projection onto the screen, bobbing animation, and
    alpha-masked texture blitting into the frame buffer.
    """

    def __init__(self, render_dim: tuple[int, int],
                 x: float, y: float) -> None:
        """Initialize the sprite at the given world position.

        Args:
            render_dim: Render surface dimensions ``(width, height)``.
            x: World X coordinate of the sprite centre.
            y: World Y coordinate of the sprite centre.
        """
        super().__init__(x, y)
        self.cor_dist = float("inf")
        self._far_view = float("inf")
        self.point_value = 0
        self.dx = 0.0
        self.dy = 0.0
        self.dist = float('inf')
        self.rel_angle = 0.0
        self.window_x = 0
        self.h = 0
        self.w = 0
        self.top = 0
        self.left = 0
        self._bob_phase = random.uniform(0, 2 * math.pi)
        self.bob_time = 0.0
        self._bob_amp = SPRITE_BOB_AMP
        self.sprite_scale = SPRITE_SCALE
        self.render_w, self.render_h = render_dim

    def get_dist_to_player(self) -> float:
        """Return the Euclidean distance from this sprite to the player."""
        return math.sqrt(self.dx*self.dx + self.dy*self.dy)

    def get_relative_angle_to_player(self, player: HasTransform) -> float:
        """Return the signed angle between the player's view and this sprite.

        The result is normalised to the range ``[-π, π]``.

        Args:
            player: The player whose viewing angle is used as the reference.

        Returns:
            Relative angle in radians, positive meaning to the right.
        """
        angle = math.atan2(self.dy, self.dx)
        rel_angle = angle - math.radians(player.angle)

        # Normalize between -pi and pi
        while rel_angle > math.pi:
            rel_angle -= 2 * math.pi
        while rel_angle < -math.pi:
            rel_angle += 2 * math.pi

        return rel_angle

    def update(self, player: HasTransform) -> None:
        """Recompute distance and relative angle to the player each frame.

        Args:
            player: The current player state.
        """
        self.dx = self.x - player.render_x
        self.dy = self.y - player.render_y
        self.dist = self.get_dist_to_player()
        self.rel_angle = self.get_relative_angle_to_player(player)

    def proj(self, dist_proj: float, dt: float) -> bool:
        """Compute the screen-space projection of this sprite.

        Calculates the sprite's horizontal screen position, display size, and
        vertical offset including the bobbing animation.  Stores the results in
        ``self.top``, ``self.left``, ``self.h``, and ``self.w``.

        Args:
            dist_proj: Projection-plane distance used to scale sprite height.
            dt: Elapsed time in seconds since the last frame.

        Returns:
            ``True`` if the sprite is within the field of view, ``False`` if
            it falls outside and should not be drawn.
        """
        half_fov = math.radians(FOV / 2)

        if abs(self.rel_angle) > half_fov + 0.1:
            return False

        window_x = int(self.render_w / 2 + (self.rel_angle / half_fov) *
                       (self.render_w / 2))
        self.cor_dist = max(0.1, self.dist * math.cos(self.rel_angle))
        wall_h = int(dist_proj / self.cor_dist)
        self.h = int(wall_h * self.sprite_scale)
        self.w = self.h
        floor_line = self.render_h // 2 + wall_h // 2

        self.bob_time += dt
        if self.bob_anime_activate:
            bob = math.sin(self.bob_time * SPRITE_BOB_SPEED * 2 * math.pi +
                           self._bob_phase)
        else:
            bob = 1
        self.top = (floor_line - self.h
                    - int(bob * self._bob_amp))
        self.left = window_x - self.w // 2

        return True

    def draw(
            self, frame: npt.NDArray[np.uint8],
            zbuffer: npt.NDArray[np.float64],
            dist_proj: float, dt: float
            ) -> None:
        """Render the sprite into the frame buffer with depth and alpha
        masking.

        Skips inactive or off-screen sprites.  For each visible column, the
        sprite is discarded if it lies behind the wall stored in *zbuffer*.
        The texture is sampled vertically and blitted with distance shading,
        respecting per-pixel alpha (threshold 128).

        Args:
            frame: The ``(WINDOW_W, WINDOW_H, 3)`` NumPy frame buffer.
            zbuffer: Per-column wall distances from the raycaster.
            dist_proj: Projection-plane distance used by ``proj``.
            dt: Elapsed time in seconds since the last frame.
        """
        if not self.is_active:
            return
        if not self.proj(dist_proj, dt):
            return
        if self.cor_dist >= self._far_view:
            return
        if self.texture is None or self.texture_alpha is None:
            return

        shade = max(0.1, 1.0 - self.dist / DIST_SHADE)
        sprite_cor_dist = self.dist * math.cos(self.rel_angle)

        top = max(0, self.top)
        bot = min(self.render_h, self.top + self.h)
        col_h = bot - top
        if col_h <= 0:
            return

        clip_top = max(0, -self.top)
        tex_step = self.texture.shape[1] / self.h
        tex_y = ((np.arange(col_h) + clip_top) * tex_step).astype(int)
        tex_y = np.clip(tex_y, 0, self.texture.shape[1] - 1)

        x_start = max(0, self.left)
        x_end = min(self.render_w, self.left + self.w)
        if x_start >= x_end:
            return

        xs = np.arange(x_start, x_end)
        depth_mask = sprite_cor_dist < zbuffer[xs]
        xs = xs[depth_mask]
        if xs.size == 0:
            return

        tex_xs = ((xs - self.left) / self.w *
                  self.texture.shape[0]).astype(int)
        tex_xs = np.clip(tex_xs, 0, self.texture.shape[0] - 1)

        cols_color = self.texture[tex_xs][:, tex_y, :]
        cols_alpha = self.texture_alpha[tex_xs][:, tex_y]
        alpha_mask = cols_alpha > 128

        pixels = (cols_color * shade).astype(np.uint8)
        for i, sx in enumerate(xs):
            frame[sx, top:bot][alpha_mask[i]] = pixels[i][alpha_mask[i]]

    def _load_texture(self, path: str) -> None:
        """Load an RGBA texture from *path* into NumPy arrays.

        Stores the colour data in
        ``self.texture`` and the alpha channel in ``self.texture_alpha``.

        Args:
            path: File-system path to the texture image.
        """
        surf = pg.image.load(path).convert_alpha()
        self.texture = pg.surfarray.array3d(surf)
        self.texture_alpha = pg.surfarray.array_alpha(surf)
