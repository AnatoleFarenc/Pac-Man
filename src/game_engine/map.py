"""Maze map generation and raycasting rendering for the 3-D view."""

import math
import pygame as pg
import numpy as np
from typing import Dict, List, Tuple, Union
from mazegenerator import MazeGenerator
from .player import Player
from ..entity.ghost import Ghost
from ..entity.pacgum import Pacgum
from ..entity.super_pacgum import SuperPacgum
from ..config.config import (
    N, S, E, W,
    FOV,
    COEF_DIST_PROJ,
    DIST_SHADE,
    SKY_COLOR, FLOOR_COLOR,
    WALL, PACGUM, SUPER_PACGUM, VOID,
    LEAN_ROLL,
    WALL_TEX
)


class Map():
    """Procedurally generated maze with raycasting-based 3-D wall rendering.

    Generates a maze using MazeGenerator, converts it to a cell-based
    grid, and exposes methods for wall collision detection and rendering
    the first-person view with texture mapping and distance shading.
    """

    def __init__(
            self,
            render_dim: Tuple[int, int],
            width: int,
            height: int,
            seed: int,
            pacgum_pts: int,
            super_pacgum_pts: int
    ) -> None:
        """Initialize the map, generate the maze, and load the wall texture.

        Args:
            render_dim: Render surface dimensions ``(width, height)``.
            width: Number of maze cells along the horizontal axis.
            height: Number of maze cells along the vertical axis.
            seed: Random seed used for deterministic maze generation.
            pacgum_pts: Score value of a regular pacgum.
            super_pacgum_pts: Score value of a super-pacgum.
        """

        # maze
        self.gen_maze = MazeGenerator(
            size=(width, height),
            perfect=False,
            seed=seed
        )
        self.width = width
        self.height = height
        self.maze = self.gen_maze.maze
        self.cell_maze = self.reform_map()
        self.cell_w = len(self.cell_maze[0])
        self.cell_h = len(self.cell_maze)

        # display
        self.max_size_ray = int(math.sqrt(len(self.cell_maze)**2 +
                                len(self.cell_maze[0])**2)) + 1
        self.render_w, self.render_h = render_dim
        self.frame = np.zeros(
            (self.render_w, self.render_h, 3), dtype=np.uint8)
        self.load_tex(WALL_TEX)

        # pacgums
        self.pacgum_dict: Dict[Tuple[int, int],
                               Union[Pacgum, SuperPacgum]] = {}
        self.place_pacgum(pacgum_pts, super_pacgum_pts)
        self.total_pacgum = len(self.pacgum_dict)
        self.remaining_pacgum = self.total_pacgum

    @property
    def center(self) -> tuple[float, float]:
        """Return the coords of the empty map center."""

        if self.width % 2 == 0:
            x = int(self.cell_w/2 - 1)
        else:
            x = int(self.cell_w/2)
        y = int(self.cell_h/2 - 1)

        if self.cell_maze[y][x] != 1:
            return (x + 0.5, y + 0.5)
        else:
            return (x + 0.5, y - 1 + 0.5)

    def update_render_dim(self, render_dim: Tuple[int, int]) -> None:
        """Resize the frame buffer when the render resolution changes."""
        self.render_w, self.render_h = render_dim
        self.frame = np.zeros(
            (self.render_w, self.render_h, 3), dtype=np.uint8)
        for sprite in self.pacgum_dict.values():
            sprite.render_w, sprite.render_h = render_dim

    def load_tex(self, path: str) -> None:
        """Load and scale a wall texture from disk into a NumPy array.

        Args:
            path: File-system path to the texture image (PNG or any format
                  supported by pygame).
        """

        tex_surf = pg.image.load(path).convert()
        tex_surf = pg.transform.scale(tex_surf, (64, 64))
        self.wall_tex = pg.surfarray.array3d(tex_surf)
        self.tex_w = self.wall_tex.shape[0]
        self.tex_h = self.wall_tex.shape[1]

    def reform_map(self) -> List[List[int]]:
        """Convert the raw maze into a cell-based wall grid.

        Each maze cell and the passages between cells are expanded so
        that walls occupy explicit grid positions.  A value of ``1``
        means a wall; ``0`` means open space.

        Returns:
            A 2-D list of integers with dimensions
            ``(height * 2 + 1) x (width * 2 + 1)``.
        """

        new_rows = (self.height * 2) + 1
        new_cols = (self.width * 2) + 1
        new_maze = [[VOID for _ in range(new_cols)] for _ in range(new_rows)]

        for y in range(0, new_rows, 2):
            for x in range(0, new_cols, 2):
                new_maze[y][x] = 1

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                y_r, x_r = y * 2, x * 2
                if cell & N:
                    new_maze[y_r][x_r + 1] = WALL
                if cell & S:
                    new_maze[y_r + 2][x_r + 1] = WALL
                if cell & E:
                    new_maze[y_r + 1][x_r + 2] = WALL
                if cell & W:
                    new_maze[y_r + 1][x_r] = WALL

        return new_maze

    def has_wall(self, col: int, row: int) -> bool:
        """Return whether the given cell grid position contains a wall.

        Out-of-bounds coordinates are treated as walls so that rays
        never escape the maze boundaries.

        Args:
            col: Horizontal index into the cell grid.
            row: Vertical index into the cell grid.

        Returns:
            ``True`` if the position is a wall or out of bounds,
            ``False`` otherwise.
        """

        if (row < 0 or row >= len(self.cell_maze) or col < 0 or
                col >= len(self.cell_maze[0])):
            return True
        return self.cell_maze[row][col] == 1

    def cast_ray(self, px: float, py: float,
                 angle_rad: float) -> Tuple[float, str, float]:
        """Cast a single ray from the player position and find the first
        wall hit.

        Uses the DDA (Digital Differential Analysis) algorithm to step
        through the cell grid efficiently.

        Args:
            px: Player X position in world units.
            py: Player Y position in world units.
            angle_rad: Ray direction in radians.

        Returns:
            A 3-tuple ``(dist, side, wall_x)`` where *dist* is the
            distance to the wall along the ray, *side* is ``"H"`` for a
            vertical grid line hit or ``"V"`` for a horizontal grid line
            hit, and *wall_x* is the fractional offset within the hit
            cell (used for texture mapping).  Returns
            ``(inf, "NO SIDE", 0.0)`` when no wall is found within the
            maximum ray length.
        """

        dx, dy = math.cos(angle_rad), math.sin(angle_rad)
        col, row = int(px), int(py)
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        t_delta_x = abs(1 / dx) if dx != 0 else float('inf')
        t_delta_y = abs(1 / dy) if dy != 0 else float('inf')
        t_max_x = (col + 1 - px if dx > 0 else px - col) * t_delta_x
        t_max_y = (row + 1 - py if dy > 0 else py - row) * t_delta_y

        for _ in range(self.max_size_ray):
            if t_max_x < t_max_y:
                col += step_x
                if self.has_wall(col, row):
                    dist = t_max_x
                    side = "H"
                    wall_x = py + dist * dy
                    wall_x -= math.floor(wall_x)
                    return dist, side, wall_x
                t_max_x += t_delta_x
            else:
                row += step_y
                if self.has_wall(col, row):
                    dist = t_max_y
                    side = "V"
                    wall_x = px + dist * dx
                    wall_x -= math.floor(wall_x)
                    return dist, side, wall_x
                t_max_y += t_delta_y
        return float('inf'), "NO SIDE", 0.0

    def draw_walls(self, window: pg.Surface, px: float, py: float,
                   p_angle: float, bob_offset_p: float = 0,
                   lean: float = 0.0) -> None:
        """Render the raycasted 3-D view for the current frame.

        Fills the internal frame buffer with sky and floor colors, then
        casts one ray per screen column, samples the wall texture, and
        applies distance-based shading before blitting the result to
        *window*.

        Args:
            window: The pygame surface to draw onto.
            px: Player X position in world units.
            py: Player Y position in world units.
            p_angle: Player viewing angle in degrees.
            bob_offset_p: Vertical head-bob offset in pixels.
            lean: Current lean factor (negative left, positive right).
        """

        self.frame[:] = 0

        self.zbuffer = np.zeros(self.render_w)

        sky_color = np.array(SKY_COLOR, dtype=np.uint8)
        floor_color = np.array(FLOOR_COLOR, dtype=np.uint8)
        self.frame[:, :self.render_h//2] = sky_color
        self.frame[:, self.render_h//2:] = floor_color

        p_rad = math.radians(p_angle)
        half_fov = math.radians(FOV / 2)
        fov_rad = math.radians(FOV)

        self.DIST_PROJ = ((self.render_w / 2) / math.tan(half_fov) *
                          COEF_DIST_PROJ)

        for col in range(self.render_w):
            angle_rad = p_rad - half_fov + (fov_rad / self.render_w) * col
            dist, side, wall_x = self.cast_ray(px, py, angle_rad)

            # apply fish-eye to correct see wall
            angle_diff = angle_rad - p_rad
            cor_dist = dist * math.cos(angle_diff)
            cor_dist = max(0.0001, cor_dist)

            wall_h = int(self.DIST_PROJ / cor_dist)
            roll = int(
                lean * LEAN_ROLL * (col - self.render_w/2) / self.render_w)
            top = max(
                0, self.render_h//2 - wall_h//2 - int(bob_offset_p) + roll)
            bot = min(self.render_h, self.render_h//2 + wall_h//2 -
                      int(bob_offset_p) + roll)

            shade = max(0.15, 1.0 - cor_dist / DIST_SHADE)
            if side == 'V':
                shade *= 0.6

            tex_x = int(wall_x * self.tex_w) % self.tex_w
            col_h = bot - top
            if col_h <= 0:
                continue

            tex_start = 0.0
            if wall_h > self.render_h:
                tex_start = (wall_h - self.render_h) / 2
            tex_step = self.tex_h / wall_h
            tex_y = np.arange(col_h)
            tex_y = (((tex_y * tex_step) + tex_start * tex_step).astype(int)
                     % self.tex_h)

            tex_col = self.wall_tex[tex_x, tex_y]

            self.frame[col, top:bot] = (tex_col * shade).astype(np.uint8)

            self.zbuffer[col] = cor_dist

    def __check_pacgum_place(self, x: int, y: int) -> bool:
        """Return whether a pacgum can be placed at the given cell coordinates.

        A cell is eligible if it is not a wall and has at least one non-wall
        neighbour (top, bottom, left, or right).

        Args:
            x: Horizontal index into the cell grid.
            y: Vertical index into the cell grid.

        Returns:
            ``True`` if the cell is a valid pacgum location, ``False``
            otherwise.
        """

        if self.cell_maze[y][x] == 1:
            return False

        neighbors = [
            self.cell_maze[y - 1][x],
            self.cell_maze[y + 1][x],
            self.cell_maze[y][x - 1],
            self.cell_maze[y][x + 1]
        ]
        for neighbor in neighbors:
            if neighbor != 1:
                return True
        return False

    def place_pacgum(self, pacgum_pts: int, super_pacgum_pts: int) -> None:
        """Populate the maze with pacgums and super-pacgums.

        Iterates every cell of the grid and places a ``Super_pacgum`` at the
        four corner positions, and a regular ``Pacgum`` everywhere else that
        passes ``__check_pacgum_place``.  The cell value in ``cell_maze`` is
        updated to ``PACGUM`` or ``SUPER_PACGUM`` accordingly, and each
        object is stored in ``pacgum_dict`` keyed by ``(x, y)``.
        """

        maze_w = len(self.cell_maze[0])
        maze_h = len(self.cell_maze)

        for y in range(maze_h):
            for x in range(maze_w):
                if self.__check_pacgum_place(x, y):
                    if ((x == 1 and y == 1) or
                            (x == 1 and y == maze_h - 2) or
                            (x == maze_w - 2 and y == 1) or
                            (x == maze_w - 2 and y == maze_h - 2)):
                        self.pacgum_dict.update({(x, y):
                                                 SuperPacgum(
                                                     (self.render_w,
                                                      self.render_h),
                                                     x + 0.5,
                                                     y + 0.5,
                                                     super_pacgum_pts)})
                        self.cell_maze[y][x] = SUPER_PACGUM
                    else:
                        self.pacgum_dict.update({(x, y):
                                                 Pacgum(
                                                     (self.render_w,
                                                      self.render_h),
                                                     x + 0.5,
                                                     y + 0.5,
                                                     pacgum_pts)})
                        self.cell_maze[y][x] = PACGUM

    def draw(
            self,
            window: pg.Surface,
            player: Player,
            ghosts: list[Ghost],
            dt: float
    ) -> None:
        """Update all pacgums and render the complete 3-D frame to *window*.

        Updates each pacgum's state relative to the player, removes picked-up
        pacgums from the remaining count, renders the raycasted walls, then
        draws all active pacgum sprites on top before blitting the frame.

        Args:
            window: The pygame surface to draw onto.
            player: The player, used for position and angle.
            dt: Elapsed time in seconds since the last frame.
        """

        self.draw_walls(window, player.render_x, player.render_y, player.angle,
                        player.bob_offset, player.lean_current)

        all_sprites = list(self.pacgum_dict.values()) + ghosts
        all_sprites.sort(key=lambda s: s.dist, reverse=True)
        for sprite in all_sprites:
            sprite.draw(self.frame, self.zbuffer, self.DIST_PROJ, dt)

        pg.surfarray.blit_array(window, self.frame)
