"""Super-pacgum collectible that triggers ghost vulnerability."""

from .pacgum import Pacgum
from ..config.config import SUPER_PACGUM_TEX


class SuperPacgum(Pacgum):
    """High-value collectible placed at the four corners of the maze."""

    def __init__(self, render_dim: tuple[int, int],
                 x: float, y: float, value: int) -> None:
        """Initialize the super-pacgum at the given world position.

        Args:
            render_dim: Render surface dimensions (width, height).
            x: World X coordinate of the super-pacgum centre.
            y: World Y coordinate of the super-pacgum centre.
            value: Score points awarded on pickup.
        """

        super().__init__(render_dim, x, y, value)
        self._load_texture(SUPER_PACGUM_TEX)
