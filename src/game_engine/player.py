"""Player entity with movement, collision, and
invincibility-state management."""

import pygame as pg
import math
from typing import Tuple
from ..config.config import (
    START_P_ANGLE, SPEED, MOUSE_SENSITIVITY, MARGIN_COLLISION_WALL,
    WALL, INVINCIBILITY_COOLDOWN, BOB_AMPLITUDE_P, BOB_SPEED_P,
    LEAN_AMOUNT, LEAN_SPEED, LEAN_WALL_MARGIN
    )


class Player():
    """Represent the player in the game world.

    Handles position, orientation, movement input and wall collision.
    """

    def __init__(self, hp: int, start_pos: Tuple[float, float]) -> None:
        """Initialize the player at the given position on the map.

        Args:
            hp: Number of hit points the player starts with.
            start_pos: Initial (x, y) world coordinates of the player.
        """

        # position
        self.spawn: tuple[float, float] = start_pos
        self.x: float = start_pos[0]
        self.y: float = start_pos[1]
        self.angle: float = START_P_ANGLE
        self.speed: float = SPEED

        # state
        self.hp = hp
        self.vulnerable: bool = True
        self.score: int = 0
        self.curr_t: float = 0.0

        # tools
        self.invincibility_cooldown: float = INVINCIBILITY_COOLDOWN

        # Bobing
        self.bob_timer = 0.0
        self.bob_offset = 0.0
        self.is_moving = False
        # lean
        self.lean = 0.0
        self.lean_current = 0.0
        self._render_x: float = start_pos[0]
        self._render_y: float = start_pos[1]

    @property
    def pos(self) -> tuple[float, float]:
        """Current world position as an ``(x, y)`` tuple."""

        return (self.x, self.y)

    @property
    def render_x(self) -> float:
        """X coordinate used for rendering,
        offset by the current lean effect."""
        return self._render_x

    @render_x.setter
    def render_x(self, x: float) -> None:
        self._render_x = x

    @property
    def render_y(self) -> float:
        """Y coordinate used for rendering,
        offset by the current lean effect."""
        return self._render_y

    @render_y.setter
    def render_y(self, y: float) -> None:
        self._render_y = y

    def set_rotation(self, dx: float) -> None:
        """Rotate the player based on horizontal mouse movement.

        Args:
            dx: Horizontal mouse delta in pixels.
        """

        self.angle += dx * MOUSE_SENSITIVITY

    def move(self, cell_maze: list[list[int]], dt: float) -> None:
        """Read keyboard input and update the player position.

        Handles forward/backward movement (W/S or Up/Down arrows),
        strafing (A/D or Left/Right arrows), and a 180-degree turn on Space.
        Each axis is resolved independently against wall collisions.

        Args:
            cell_maze: The cell grid used for wall collision checks.
            dt: Elapsed time in seconds since the last frame.
        """

        keys = pg.key.get_pressed()
        one_press_keys = pg.key.get_just_pressed()
        forward_x = math.cos(math.radians(self.angle))
        forward_y = math.sin(math.radians(self.angle))
        right_x = math.sin(math.radians(self.angle))
        right_y = -math.cos(math.radians(self.angle))
        new_x = self.x
        new_y = self.y

        frame_speed = self.speed * dt

        if keys[pg.K_UP] or keys[pg.K_w]:
            new_x += forward_x * frame_speed
            new_y += forward_y * frame_speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            new_x -= forward_x * frame_speed
            new_y -= forward_y * frame_speed
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            new_x += right_x * (frame_speed / 2)
            new_y += right_y * (frame_speed / 2)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            new_x -= right_x * (frame_speed / 2)
            new_y -= right_y * (frame_speed / 2)

        old_x = self.x
        old_y = self.y
        if self.check_wall(cell_maze, new_x, self.y):
            self.x = new_x
        if self.check_wall(cell_maze, self.x, new_y):
            self.y = new_y

        if one_press_keys[pg.K_SPACE]:
            self.angle += 180

        self.is_moving = (self.x != old_x or self.y != old_y)
        if self.is_moving:
            self.bob_timer += dt
            self.bob_offset = (BOB_AMPLITUDE_P *
                               math.sin(self.bob_timer *
                                        BOB_SPEED_P * 2 *
                                        math.pi))
        else:
            self.bob_offset *= 0.85
            if abs(self.bob_offset) < 0.5:
                self.bob_offset = 0.0
                self.bob_timer = 0.0

        if keys[pg.K_q]:
            self.lean = 1.0
        elif keys[pg.K_e]:
            self.lean = -1.0
        else:
            self.lean = 0.0
        self.lean_current += (self.lean - self.lean_current) * LEAN_SPEED * dt

        lean_rad = math.radians(self.angle)
        dir_x = math.sin(lean_rad)
        dir_y = -math.cos(lean_rad)
        lean_dx = dir_x * LEAN_AMOUNT
        lean_dy = dir_y * LEAN_AMOUNT
        sign = 1.0 if self.lean_current >= 0 else -1.0
        lx = self.x + lean_dx * self.lean_current
        ly = self.y + lean_dy * self.lean_current
        cx = lx + dir_x * sign * LEAN_WALL_MARGIN
        cy = ly + dir_y * sign * LEAN_WALL_MARGIN
        if cell_maze[int(cy)][int(cx)] == WALL:
            lo, hi = 0.0, abs(self.lean_current)
            for _ in range(6):
                mid = (lo + hi) / 2
                mx = self.x + lean_dx * sign * mid
                my = self.y + lean_dy * sign * mid
                x = int(mx + dir_x * sign * LEAN_WALL_MARGIN)
                y = int(my + dir_y * sign * LEAN_WALL_MARGIN)
                if cell_maze[y][x] == WALL:
                    hi = mid
                else:
                    lo = mid
            lx = self.x + lean_dx * sign * lo
            ly = self.y + lean_dy * sign * lo
        self._render_x = lx
        self._render_y = ly

    def check_wall(
            self,
            cell_maze: list[list[int]],
            x: float,
            y: float
    ) -> bool:
        """Check whether the given position is free of wall collisions.

        Tests the four corners of the player's bounding box against the map.

        Args:
            cell_maze: The cell grid used for collision detection.
            x: World x coordinate to test.
            y: World y coordinate to test.

        Returns:
            True if the position is passable, False if a wall is hit.
        """

        for dx in [-MARGIN_COLLISION_WALL, MARGIN_COLLISION_WALL]:
            for dy in [-MARGIN_COLLISION_WALL, MARGIN_COLLISION_WALL]:
                if cell_maze[int(y + dy)][int(x + dx)] == WALL:
                    return False
        return True

    def check_state(self, dt: float) -> None:
        """Advance the invincibility timer and restore
        vulnerability when it expires.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """

        if not self.vulnerable:
            self.curr_t += dt
        if self.curr_t > self.invincibility_cooldown:
            self.vulnerable = True
            self.curr_t = 0

    def new_spawn(self, start_pos: tuple[float, float]) -> None:
        """Teleport the player to *start_pos* and reset orientation and state.

        Args:
            start_pos: New ``(x, y)`` world coordinates for the spawn point.
        """

        self.spawn = start_pos
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.angle = START_P_ANGLE
        self.vulnerable = True
        self.curr_t = 0

    def die(self) -> None:
        """Deduct one hit point, trigger invincibility,
        and reset to the spawn point."""

        self.hp -= 1
        self.vulnerable = False
        self.x = self.spawn[0]
        self.y = self.spawn[1]
        self.angle = START_P_ANGLE
