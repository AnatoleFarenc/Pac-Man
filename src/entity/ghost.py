"""Ghost enemy entities with A* pathfinding and vulnerability state machine."""

import glob
import heapq
from typing import Tuple
import math
# from random import choice
from enum import Enum, auto
from .sprite import Sprite
from ..config.config import (
    GHOST_SCALE, DIST_GHOST_HIT, VULNERABILITY_TIME, CHASE_TIME,
    RAND_TIME, SPEED_GHOST, FRAMES_VULN, FAR_VIEW_GHOST,
    PINKY_FRONT_PAC, INKY_FRONT_PAC, CLYDE_DIST_PAC
)


class GhostType(Enum):
    """Enumeration of the four ghost personalities."""

    BLINKY = auto()
    INKY = auto()
    PINKY = auto()
    CLYDE = auto()


class GhostState(Enum):
    """Enumeration of the possible AI states a ghost can be in."""

    CHASE = auto()
    RANDOM = auto()
    VULNERABLE = auto()
    DEAD = auto()


class Direction(Enum):
    """Enumeration of movement directions used by the
    ghost pathfinding system."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    SPAWN = auto()


class Ghost(Sprite):
    """Enemy entity that chases the player through the maze.

    Extends ``Sprite`` with movement, vulnerability state management, and
    hit detection.  When a super-pacgum is collected, the ghost enters a
    vulnerable state and changes its texture until the timer expires.
    """

    def __init__(
            self,
            render_dim: tuple[int, int],
            x: float,
            y: float,
            ghost_type: GhostType,
            path_frames_idl: str,
            path_frames_damage: str,
            color: Tuple[int, int, int],
            value: int
    ) -> None:
        """Initialize the ghost at the given world position.

        Args:
            render_dim: Render surface dimensions (width, height).
            x: World X coordinate of the ghost's starting position.
            y: World Y coordinate of the ghost's starting position.
            ghost_type: Personality enum value that drives targeting behaviour.
            path_frames_idl: Directory with normal animation frames.
            path_frames_damage: Directory with death-state animation frames.
            color: RGB colour used for the mini-map indicator.
            value: Score points awarded when the ghost is eaten.
        """
        super().__init__(render_dim, x, y)
        self.name: GhostType = ghost_type

        # display
        self.sprite_scale: float = GHOST_SCALE
        self.color = color
        self.bob_anime_activate: bool = False
        self._far_view: int = FAR_VIEW_GHOST
        frames_path = sorted(glob.glob(f"{path_frames_idl}/*.png"))
        frames_path_dam = sorted(glob.glob(f"{path_frames_damage}/*.png"))
        frames_path_vuln = sorted(glob.glob(f"{FRAMES_VULN}/*.png"))
        self._anim_frames = self._load_textures(frames_path)
        self._anim_frames_dam = self._load_textures(frames_path_dam)
        self._anim_frames_vuln = self._load_textures(frames_path_vuln)
        self._anim_curr_frames = self._anim_frames

        # position
        self.spawn: tuple[float, float] = (x, y)
        self.pos: tuple[float, float] = self.spawn
        self.speed: float = SPEED_GHOST
        self.next_pos: tuple[float, float] = self.spawn

        # state
        self.state: GhostState = GhostState.CHASE
        self.dir: Direction = Direction.SPAWN
        self.curr_t: float = 0

        # point
        self.point_value = value

    @property
    def pos(self) -> tuple[float, float]:
        """Current world position as an ``(x, y)`` tuple."""

        return (self.x, self.y)

    @pos.setter
    def pos(self, pos: tuple[float, float]) -> None:
        """Set the ghost position from an ``(x, y)`` tuple."""

        self.x = pos[0]
        self.y = pos[1]

    def check_hit(self) -> bool:
        """Return whether the ghost is close enough to hit the player.

        Returns:
            ``True`` if the distance to the player is below ``DIST_GHOST_HIT``,
            ``False`` otherwise.
        """
        return self.dist < DIST_GHOST_HIT

    def set_vulnerable(self) -> None:
        """Switch the ghost into the VULNERABLE state and reset the timer."""

        self.state = GhostState.VULNERABLE
        self.curr_t = 0

    def check_state(self, dt: float) -> None:
        """Advance the internal timer and update the vulnerability state.

        Increments the current time by *dt*, clears the vulnerability flag
        once the remaining time has elapsed, and swaps the texture to match
        the current state.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """

        self.curr_t += dt

        match self.state:
            # vuln
            case GhostState.VULNERABLE:
                self._anim_curr_frames = self._anim_frames_vuln
                if self.curr_t > VULNERABILITY_TIME:
                    self.state = GhostState.CHASE
                    self.curr_t = 0
                    self._anim_curr_frames = self._anim_frames
            # chase
            case GhostState.CHASE:
                # add distinction CLOSE TO PAC OR FAR
                # CLOSE KEEP CHASING
                # FAR GET RANDOM
                if self.curr_t > CHASE_TIME:
                    self.curr_t = 0
                    self.state = GhostState.RANDOM
                    self._anim_curr_frames = self._anim_frames
            # random
            case GhostState.RANDOM:
                if self.curr_t > RAND_TIME:
                    self.curr_t = 0
                    self.state = GhostState.CHASE
            # dead
            case GhostState.DEAD:
                dx = self.x - self.spawn[0]
                dy = self.y - self.spawn[1]
                if (dx * dx + dy * dy) < 0.01:
                    self.curr_t = 0
                    self.speed = SPEED_GHOST
                    self.state = GhostState.CHASE
                    self.dir = Direction.SPAWN
                    self._anim_curr_frames = self._anim_frames

    def take_damage(self) -> None:
        """Handle the ghost being eaten by the player while vulnerable."""

        self.state = GhostState.DEAD
        self.next_pos = self.spawn
        self._anim_curr_frames = self._anim_frames_dam

    def move(self, dt: float) -> None:
        """Move the ghost one step toward the target position.

        Advances the ghost at most ``speed * dt`` world units per call.
        If the remaining distance is smaller than the frame displacement,
        the ghost is snapped directly to the target.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """
        n_x, n_y = self.next_pos
        frame_speed = self.speed * dt
        dx = n_x - self.x
        dy = n_y - self.y

        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist <= frame_speed:
            self.x = n_x
            self.y = n_y
        else:
            self.x += (dx / dist) * frame_speed
            self.y += (dy / dist) * frame_speed

        self.play_anim(dt)

    def get_direction(self) -> Direction:
        """Derive the ghost's current movement direction from its
        next target cell."""

        x = int(self.x) + 0.5
        y = int(self.y) + 0.5

        if self.next_pos == (x, y + 1):
            return Direction.DOWN
        elif self.next_pos == (x, y - 1):
            return Direction.UP
        elif self.next_pos == (x + 1, y):
            return Direction.RIGHT
        elif self.next_pos == (x - 1, y):
            return Direction.LEFT
        else:
            return Direction.SPAWN

    def set_target(
            self,
            grid: list[list[int]],
            pac_coords: tuple[float, float],
            blinky_p: tuple[float, float],
            p_angle: float
    ) -> None:
        """Compute and store the next grid cell this ghost should move toward.

        Delegates to the appropriate pathfinding strategy based on the current
        state (chase, vulnerable, random) and updates ``self.dir``.

        Args:
            grid: The cell maze grid used for pathfinding.
            pac_coords: Current player world position ``(x, y)``.
            blinky_p: Blinky's position, needed by Inky's targeting.
            p_angle: Player viewing angle in degrees.
        """
        chase_target = self.search_chase_target(
            grid=grid,
            pac_coords=pac_coords,
            p_angle=p_angle,
            blinky_p=blinky_p
        )
        # ghost dependent pathfinding TO-DO
        match self.state:
            case GhostState.CHASE:
                self.next_pos = self._find_path(
                    grid=grid,
                    goal=chase_target
                )
            case GhostState.VULNERABLE:
                self.next_pos = self._flee(
                    grid=grid,
                    goal=pac_coords
                )
            case GhostState.RANDOM:
                self.next_pos = self._find_path(
                    grid=grid,
                    goal=self.spawn
                )
            case _:
                pass

        # compute direction
        self.dir = self.get_direction()

    def search_chase_target(
            self,
            grid: list[list[int]],
            pac_coords: tuple[float, float],
            p_angle: float,
            blinky_p: tuple[float, float]) -> tuple[float, float]:
        """Return the personality-specific chase target tile for this ghost.

        Args:
            grid: The cell maze grid used to validate target positions.
            pac_coords: Current player position ``(x, y)`` in world units.
            p_angle: Player viewing angle in degrees.
            blinky_p: Blinky's current position, used by Inky's targeting.

        Returns:
            Target world position ``(x, y)`` the ghost should path toward.
        """
        pac_x, pac_y = pac_coords
        dx = math.cos(math.radians(p_angle))
        dy = math.sin(math.radians(p_angle))

        if self.name == GhostType.BLINKY:
            return pac_coords
        if self.name == GhostType.PINKY:
            tx = int(pac_x + dx * PINKY_FRONT_PAC)
            ty = int(pac_y + dy * PINKY_FRONT_PAC)
            if (tx < 0 or ty < 0 or ty >= len(grid) or
                    tx >= len(grid[0])
                    or grid[ty][tx] == 1):
                return pac_coords
            return (tx + 0.5, ty + 0.5)
        if self.name == GhostType.INKY:
            p2x = pac_x + dx * INKY_FRONT_PAC
            p2y = pac_y + dy * INKY_FRONT_PAC

            bx, by = blinky_p
            tx = int(p2x + (p2x - bx))
            ty = int(p2y + (p2y - by))
            if (tx < 0 or ty < 0 or ty >= len(grid) or
                    tx >= len(grid[0])
                    or grid[ty][tx] == 1):
                return pac_coords
            return (tx + 0.5, ty + 0.5)
        if self.name == GhostType.CLYDE:
            cx, cy = self.pos
            dist = ((cx - pac_x) ** 2 + (cy - pac_y) ** 2) ** 0.5
            if dist > CLYDE_DIST_PAC:
                return pac_coords
            else:
                return self.spawn

        return pac_coords

    @staticmethod
    def neighbors(
            cell: tuple[int, int],
            grid: list[list[int]]
    ) -> list[tuple[int, int]]:
        """Return the passable orthogonal neighbours of *cell* in *grid*.

        Args:
            cell: ``(col, row)`` integer grid position to expand.
            grid: The cell maze grid where ``1`` denotes a wall.

        Returns:
            List of passable adjacent ``(col, row)`` positions.
        """

        x, y = cell
        neighbors: list[tuple[int, int]] = []

        if x != 0 and grid[y][x - 1] != 1:
            neighbors.append(((x - 1), y))
        if y != 0 and grid[y - 1][x] != 1:
            neighbors.append((x, (y - 1)))
        if x != len(grid[0]) - 1 and grid[y][x + 1] != 1:
            neighbors.append((x + 1, y))
        if y != len(grid) - 1 and grid[y + 1][x] != 1:
            neighbors.append((x, y + 1))

        return neighbors

    def _flee(
            self,
            grid: list[list[int]],
            goal: tuple[float, float]
    ) -> tuple[float, float]:
        """Return the next step toward the cell farthest from the player.

        Args:
            grid: The cell maze grid.
            goal: Player world position ``(x, y)`` to flee from.

        Returns:
            World position ``(x, y)`` of the first step along the escape path.
        """
        pac_x, pac_y = int(goal[0]), int(goal[1])

        best = None
        best_dist = -1
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell != 1:
                    dist = abs(x - pac_x) + abs(y - pac_y)
                    if dist > best_dist:
                        best_dist = dist
                        best = (x + 0.5, y + 0.5)

        assert best is not None
        return self._find_path(grid, best)

    def _find_path(
            self,
            grid: list[list[int]],
            goal: tuple[float, float]
    ) -> tuple[float, float]:
        """Run A* and return the first step along the shortest path to *goal*.

        If no path exists the ghost stays in its current cell.

        Args:
            grid: The cell maze grid where ``1`` denotes a wall.
            goal: Target world position ``(x, y)``.

        Returns:
            World position ``(x, y)`` of the next cell center to move toward.
        """

        def heuristic(start: tuple[int, int], end: tuple[int, int]) -> float:
            """Manhattan distance between *start* and *end* grid cells."""

            return abs(start[0] - end[0]) + abs(start[1] - end[1])

        start_int = (int(self.x), int(self.y))
        goal_int = (int(goal[0]), int(goal[1]))

        if start_int == goal_int:
            return goal

        # g_cost dict
        g_cost: dict[tuple[int, int], int] = dict()
        g_cost[start_int] = 0

        # parent dict
        parent: dict[tuple[int, int], tuple[int, int]] = dict()

        # create heapq
        queue: list[tuple[float, tuple[int, int]]] = []
        closed: set[tuple[int, int]] = set()
        heapq.heappush(queue, (heuristic(start_int, goal_int), start_int))

        # A* algorithm
        while queue:
            curr = heapq.heappop(queue)[1]
            if curr in closed:
                continue
            closed.add(curr)
            if curr == goal_int:
                break
            for cell in self.neighbors(curr, grid):
                # direction filter for first move
                if curr == start_int:
                    x, y = curr
                    if cell == (x - 1, y) and self.dir == Direction.RIGHT:
                        continue
                    elif cell == (x + 1, y) and self.dir == Direction.LEFT:
                        continue
                    elif cell == (x, y - 1) and self.dir == Direction.DOWN:
                        continue
                    elif cell == (x, y + 1) and self.dir == Direction.UP:
                        continue
                    else:
                        pass
                cell_g = g_cost[curr] + 1
                if cell not in g_cost or cell_g < g_cost[cell]:
                    g_cost[cell] = cell_g
                    parent[cell] = curr
                    heapq.heappush(
                        queue,
                        (cell_g + heuristic(cell, goal_int), cell)
                    )

        # reconstruct path
        if goal_int not in parent:
            return (int(self.x) + 0.5, int(self.y) + 0.5)

        path = []
        curr = goal_int
        path.append(curr)
        while parent[curr] != start_int:
            path.append(parent[curr])
            curr = parent[curr]

        x, y = path[-1]

        return (x + 0.5, y + 0.5)
