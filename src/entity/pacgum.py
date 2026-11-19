"""Regular pacgum collectible scattered throughout the maze."""

from .sprite import Sprite
from ..config.config import (
    PACGUM_TEX, FAR_VIEW_PACGUM, DIST_PICKUP_PACGUM
    )


class Pacgum(Sprite):
    """Collectible pacgum sprite placed throughout the maze."""

    def __init__(self, render_dim: tuple[int, int], x: float,
                 y: float, value: int) -> None:
        """Initialize the pacgum at the given world position.

        Args:
            render_dim: Render surface dimensions (width, height).
            x: World X coordinate of the pacgum centre.
            y: World Y coordinate of the pacgum centre.
            value: Score points awarded on pickup.
        """

        super().__init__(render_dim, x, y)
        self.value = value
        self._load_texture(PACGUM_TEX)
        self._far_view = FAR_VIEW_PACGUM

    def check_pickup(self) -> bool:
        """Deactivate and signal collection when the player is close enough.

        Returns:
            ``True`` if the pacgum was active and within pick-up range
            (distance < 0.5), ``False`` otherwise.
        """
        if not self.is_active:
            return False
        if self.dist < DIST_PICKUP_PACGUM:
            self.is_active = False
            return True
        return False
