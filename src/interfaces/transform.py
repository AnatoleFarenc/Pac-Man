"""Structural protocols used as lightweight interfaces across the engine."""

from typing import Protocol


class HasTransform(Protocol):
    """Protocol for objects with a 2-D world position and a viewing angle."""

    x: float
    y: float
    angle: float

    @property
    def render_x(self) -> float:
        """X coordinate used for rendering
        (may differ from ``x`` when leaning)."""
        ...

    @property
    def render_y(self) -> float:
        """Y coordinate used for rendering
        (may differ from ``y`` when leaning)."""
        ...
