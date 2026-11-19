"""Overlay mini-map renderer that draws the maze as a 2-D top-down view."""

import pygame as pg
import math
from typing import Tuple, List

from .map import Map
from ..entity.ghost import Ghost, GhostState
from ..entity.sprite_mini_map import Sprite_mini_map
from ..entity.ghost import GhostType
from ..config.config import (
    COLOR_WALL, COLOR_PACGUM,
    WALL, PACGUM, SUPER_PACGUM,
    PACMAN_FRAMES_M, GHOST_BLINKY_M,
    GHOST_INKY_M, GHOST_PINKY_M,
    SIZE_MINI_MAP, BORDER_COLOR,
    GHOST_VULN_M,
    GHOST_COLOR_M,
    GHOST_DEATH_M
    )


class Mini_map():
    """Top-down overlay that renders the maze walls as a scaled 2-D map.

    Each maze cell is drawn as a square whose side length is derived
    from the total mini-map size divided by the maze height.
    """

    def __init__(self, map: Map, size: int,
                 pos: Tuple[int, int]) -> None:
        """Initialize the mini-map renderer.

        Args:
            map: The game map whose ``cell_maze`` will be rendered.
            size: Side length in pixels of the mini-map circle.
            pos: ``(x, y)`` pixel position of the mini-map center on screen.
        """
        self.width = len(map.cell_maze[0]) * SIZE_MINI_MAP
        self.height = len(map.cell_maze) * SIZE_MINI_MAP
        self.box = pg.Surface((size, size), pg.SRCALPHA)
        self.radius = size / 2
        self.pos = pos

        self.map = map

        self.size_cell = self.radius / SIZE_MINI_MAP
        self.size_pg = SIZE_MINI_MAP / 5
        self.size_spg = SIZE_MINI_MAP / 1.5

        self.border = max(1, int(size * 0.030))
        self.indicator_size = max(4, int(size * 0.04))

        self.mask = pg.Surface((size, size), pg.SRCALPHA)
        self.mask.fill((0, 0, 0, 0))
        pg.draw.circle(
            self.mask,
            (255, 255, 255, 255),
            (int(self.radius), int(self.radius)),
            int(self.radius),)

        self.player = Sprite_mini_map(0, 0, PACMAN_FRAMES_M)
        self._ghost_sprites: List[Sprite_mini_map] = []
        self.__place_ghost()

    def __world_to_box(self, wx: float, wy: float,
                       p_pos: Tuple[float, float],
                       p_angle: float) -> Tuple[float, float]:
        """Convert a world position to mini-map box pixel coordinates.

        Rotates the coordinate so the map is always oriented with the player
        facing upward.

        Args:
            wx: World X coordinate to convert.
            wy: World Y coordinate to convert.
            p_pos: Player's current world position ``(x, y)``.
            p_angle: Player's viewing angle in degrees.

        Returns:
            Pixel coordinates ``(px, py)`` relative to the mini-map box center.
        """
        draw_x = (wx - p_pos[0]) * self.size_cell
        draw_y = (wy - p_pos[1]) * self.size_cell

        angle_rad = math.radians(-p_angle - 90)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rx = draw_x * cos_a - draw_y * sin_a
        ry = draw_x * sin_a + draw_y * cos_a

        return self.radius + rx, self.radius + ry

    def __draw_map_cell(self, p_pos: Tuple[float, float],
                        p_angle: float) -> None:
        """Draw a rotated square for each wall cell onto the mini-map surface.

        Args:
            p_pos: Player's current world position ``(x, y)``.
            p_angle: Player's viewing angle in degrees.
        """
        half = self.size_cell / 2
        for row_idx, row in enumerate(self.map.cell_maze):
            for col_idx, cell in enumerate(row):
                if cell == WALL:
                    cx, cy = self.__world_to_box(
                        col_idx + 0.5, row_idx + 0.5, p_pos, p_angle)
                    angle_rad = math.radians(-p_angle - 90)
                    cos_a = math.cos(angle_rad)
                    sin_a = math.sin(angle_rad)
                    corners = []
                    for dx, dy in ([(-half, -half), (half, -half),
                                   (half, half), (-half, half)]):
                        rx = dx * cos_a - dy * sin_a
                        ry = dx * sin_a + dy * cos_a
                        corners.append((cx + rx, cy + ry))
                    pg.draw.polygon(self.box, COLOR_WALL, corners)

    def __draw_pacgum(self, p_pos: Tuple[float, float],
                      p_angle: float) -> None:
        """Draw all active pacgums and super-pacgums onto the mini-map surface.

        Args:
            p_pos: Player's current world position ``(x, y)``.
            p_angle: Player's viewing angle in degrees.
        """
        for row_idx, row in enumerate(self.map.cell_maze):
            for col_idx, cell in enumerate(row):
                if (cell == PACGUM and
                        self.map.pacgum_dict[(col_idx, row_idx)].is_active):
                    draw_x, draw_y = self.__world_to_box(
                        col_idx + 0.5, row_idx + 0.5, p_pos, p_angle)
                    half_pg = self.size_pg / 2
                    pg.draw.circle(
                        self.box,
                        COLOR_PACGUM,
                        (int(draw_x), int(draw_y)),
                        int(half_pg))
                if (cell == SUPER_PACGUM and
                        self.map.pacgum_dict[(col_idx, row_idx)].is_active):
                    draw_x, draw_y = self.__world_to_box(
                        col_idx + 0.5, row_idx + 0.5, p_pos, p_angle)
                    half_spg = self.size_spg / 2
                    pg.draw.circle(
                        self.box,
                        COLOR_PACGUM,
                        (int(draw_x), int(draw_y)),
                        int(half_spg))

    def __place_ghost(self) -> None:
        """Instantiate one mini-map sprite for each ghost in display order.

        Creates four ``Sprite_mini_map`` objects — Blinky, Pinky, Inky, and
        Clyde — and appends them to ``_ghost_sprites``.  The order must match
        the ghost list passed to ``__draw_ghost`` so that each sprite is
        paired with the correct ghost entity at render time.
        """
        self._ghost_sprites.append(Sprite_mini_map(0, 0, GHOST_BLINKY_M))
        self._ghost_sprites.append(Sprite_mini_map(0, 0, GHOST_PINKY_M))
        self._ghost_sprites.append(Sprite_mini_map(0, 0, GHOST_INKY_M))
        # self._ghost_sprites.append(Sprite_mini_map(0, 0, GHOST_CLYDE_M))

        for ghost in self._ghost_sprites:
            ghost.add_animation(GHOST_DEATH_M)
            ghost.add_animation(GHOST_VULN_M)

    def __draw_ghost(self, ghosts: List[Ghost],
                     p_pos: Tuple[float, float],
                     p_angle: float, dt: float) -> None:
        """Draw each ghost as an animated sprite on the mini-map surface.

        Args:
            ghosts: Ordered list of ghost entities to render.
            p_pos: Player's current world position ``(x, y)``.
            p_angle: Player's viewing angle in degrees.
            dt: Elapsed time in seconds since the last frame.
        """
        for sprite, ghost in zip(self._ghost_sprites, ghosts):
            if ghost.name == GhostType.CLYDE:
                continue

            if (ghost.state != GhostState.VULNERABLE and
                    ghost.state != GhostState.DEAD):
                sprite.change_frames(0)
            if ghost.state == GhostState.DEAD:
                sprite.change_frames(1)
            if ghost.state == GhostState.VULNERABLE:
                sprite.change_frames(2)

            draw_x, draw_y = self.__world_to_box(ghost.x, ghost.y,
                                                 p_pos, p_angle)

            dx = draw_x - self.radius
            dy = draw_y - self.radius
            dist = math.hypot(dx, dy)

            if dist <= self.radius:
                sprite.draw(
                    self.box,
                    (draw_x / self.size_cell, draw_y / self.size_cell),
                    self.size_cell, dt)

    def __draw_ghost_indicator(self, ghosts: List[Ghost],
                               p_pos: Tuple[float, float],
                               p_angle: float, window: pg.Surface,
                               cx: float, cy: float) -> None:
        """Draw a small colored square at the mini-map
        edge for each off-screen ghost.

        Args:
            ghosts: List of ghost entities to check.
            p_pos: Player's current world position ``(x, y)``.
            p_angle: Player's viewing angle in degrees.
            window: Main window surface to draw the edge indicators on.
            cx: X pixel coordinate of the mini-map center on *window*.
            cy: Y pixel coordinate of the mini-map center on *window*.
        """
        for i, ghost in enumerate(ghosts):
            if ghost.name == GhostType.CLYDE:
                continue

            draw_x, draw_y = self.__world_to_box(ghost.x,
                                                 ghost.y,
                                                 p_pos, p_angle)

            color = ghost.color
            if ghost.state == GhostState.VULNERABLE:
                color = GHOST_COLOR_M[4]

            dx = draw_x - self.radius
            dy = draw_y - self.radius
            dist = math.hypot(dx, dy)
            if dist > self.radius:
                size = self.indicator_size
                edge_x = cx + (dx / dist) * (self.radius - self.border / 2)
                edge_y = cy + (dy / dist) * (self.radius - self.border / 2)
                pg.draw.rect(
                    window,
                    color,
                    (edge_x - size / 2,
                     edge_y - size / 2,
                     size,
                     size)
                )

    def draw(self, window: pg.Surface, p_pos: Tuple[float, float],
             ghosts: List[Ghost], dt: float, p_angle: float = 0.0) -> None:
        """Draw the mini-map overlay onto *window*.

        Args:
            window: The pygame surface to draw onto.
            p_pos: Player world position ``(x, y)``.
            ghosts: List of ghost entities to render on the mini-map.
            dt: Elapsed time in seconds since the last frame.
            p_angle: Player viewing angle in degrees.
        """

        self.box.fill((0, 0, 0, 255))

        self.__draw_map_cell(p_pos, p_angle)
        self.__draw_pacgum(p_pos, p_angle)
        self.__draw_ghost(ghosts, p_pos, p_angle, dt)

        center = (self.radius / self.size_cell, self.radius / self.size_cell)
        self.player.draw(self.box, center, self.size_cell, dt, -90)

        self.box.blit(self.mask, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

        # Draw border
        pg.draw.circle(
            self.box,
            BORDER_COLOR,
            (int(self.radius), int(self.radius)),
            int(self.radius),
            self.border
        )

        cx, cy = self.pos
        window.blit(self.box, (cx - self.radius, cy - self.radius))
        self.__draw_ghost_indicator(ghosts, p_pos, p_angle, window, cx, cy)
