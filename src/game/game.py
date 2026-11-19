"""Main game loop and top-level orchestration for the
Pac-Man raycasting game."""

import pygame as pg
import time
import os
import sys
from ..config.data import Config, HighScores
from ..game_engine.hud import Hud
from ..entity.ghost import Ghost, GhostType, GhostState
from ..entity.super_pacgum import SuperPacgum
from ..game_engine.map import Map
from ..game_engine.player import Player
from ..game_engine.mini_map import Mini_map
from ..game_engine.cheat import Cheat
from ..config.config import (
    RENDER_W, RENDER_H, FRAMES_BLINKY, FRAMES_CLYDE,
    FRAMES_INKY, FRAMES_PINKY, MENU_MAP, MENU_POS, MENU_ANGLE,
    SPEED_GHOST, GHOST_COLOR_M, FRAMES_BLINKY_DAM, FRAMES_INKY_DAM,
    FRAMES_PINKY_DAM, FRAMES_CLYDE_DAM,
    DIAMETER_M, MIN_MINI_MAP_SIZE,
    WINDOW_W, WINDOW_H,
    AMBIANT_SOUND, PACGUM_SOUND,
    S_PACGUM_SOUND, GHOST_SOUND,
    GHOST_HEAT_SOUND, MENU_SOUND,
    TRANSITION_E_TIME, DAMAGE_FLASH_DURATION
    )
from typing import cast
from ..menus import Menu, build_menus, outlined_text
from ..menus.end import EndMenu
from ..menus.high_scores import Enter_Name_Menu, HighScoresMenu
from .states import GameState
from ..interfaces.setting import Setting
from ..game_engine.sound_manager import Sound_Manager


class Game:
    """Top-level game object that owns the engine, entities, and game loop."""

    def __init__(
            self,
            config: Config,
            hi_scores: HighScores
    ) -> None:
        """Initialize pygame, create the window
        and instantiate all subsystems.

        Args:
            config: Validated game configuration (map size, lives, scores…).
            hi_scores: Current high-score table loaded at startup.
        """
        # config
        self.setting = Setting(config)

        pg.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
        pg.init()
        self.sound_manager = Sound_Manager()

        # display
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS')
        else:
            base_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), '..', '..')
        icon_path = os.path.join(
            base_path, 'assets', 'sprites', 'pac_icone_l_m.png')
        if os.path.exists(icon_path):
            pg.display.set_icon(pg.image.load(icon_path))
        pg.display.set_caption("Pac-Man")
        self.display = pg.display.Info()
        self.window_size: tuple[int, int] = (
            int(WINDOW_W),
            int(WINDOW_H)
            )
        self.w: int = self.window_size[0]
        self.h: int = self.window_size[1]
        self.render_w, self.render_h = RENDER_W, RENDER_H
        self.render_surf = pg.Surface((self.render_w,
                                       self.render_h))
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pg.display.set_mode(
            self.window_size
            )
        self.hud: Hud = Hud((self.render_w,
                             self.render_h))

        # clock
        self.clock = pg.time.Clock()
        self.acc_time: float = 0.0

        # entities/game engine
        self.config: Config = self.setting.to_config()
        self.map = Map(
            (self.render_w, self.render_h),
            self.config.width,
            self.config.height,
            self.config.seed,
            self.config.points_per_pacgum,
            self.config.points_per_super_pacgum
        )
        self.menu_map = Map(
            (self.render_w, self.render_h),
            self.config.width,
            self.config.height,
            self.config.seed,
            self.config.points_per_pacgum,
            self.config.points_per_super_pacgum
        )
        self.menu_map.cell_maze = MENU_MAP
        self.player = Player(self.config.lives, self.map.center)
        self.menu_player = Player(self.config.lives, MENU_POS)
        self.menu_player.angle = MENU_ANGLE
        self.ghosts: list[Ghost] = self.create_ghosts()
        self.menu_ghosts: list[Ghost] = []
        self.cheat = Cheat(self.player, self.ghosts, self.map)

        # Mini map
        self.size_mini_map = max(int(self.h * DIAMETER_M), MIN_MINI_MAP_SIZE)
        self.pos_mini_map = (int(self.size_mini_map * 0.6),
                             int(self.size_mini_map * 0.6))
        self.mini_map = Mini_map(self.map, self.size_mini_map,
                                 self.pos_mini_map)

        # damage flash
        self.damage_flash_timer: float = 0.0

        # gamestate
        self.state: GameState = GameState.MAIN_MENU
        self.curr_lvl: int = 1
        self.playing: bool = False
        self.start_time: float = 0
        self.time_left: float = self.config.level_max_time + 1
        self.transition_t: float = 0.0
        self.menu_transition: bool = False
        self.END_SCREEN_DURATION: float = 4.0

        # menus
        self.menus: dict[GameState, Menu] = build_menus(
            self.window_size, self.setting, hi_scores)
        self.curr_menu: Menu = self.menus[self.state]

        # hight score
        self.high_score: HighScores = hi_scores

        # debug
        self.debug_font: pg.Font = pg.font.SysFont(
            None,
            (min(self.window_size)//35)
        )

    def update_window(self, new_state: GameState) -> None:
        """Rebuild the display and all render surfaces after a settings change.

        Resizes the window, recreates menus, regenerates the mini-map and
        render surface, and updates each ghost's render dimensions.

        Args:
            new_state: The game state to activate after the window update.
        """
        self.window_size = self.setting.window_size
        self.w, self.h = self.window_size

        # window center
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pg.display.set_mode(self.window_size)

        self.size_mini_map = max(int(self.h * DIAMETER_M), MIN_MINI_MAP_SIZE)
        self.pos_mini_map = (int(self.size_mini_map * 0.6),
                             int(self.size_mini_map * 0.6))
        self.mini_map = Mini_map(self.map, self.size_mini_map,
                                 self.pos_mini_map)

        self.menus = build_menus(self.window_size, self.setting,
                                 self.high_score)
        self.curr_menu = self.menus[new_state]

        self.render_w, self.render_h = self.setting.resolution
        self.render_surf = pg.Surface((self.render_w, self.render_h))
        self.hud = Hud((self.render_w, self.render_h))
        render_dim = (self.render_w, self.render_h)
        self.map.update_render_dim(render_dim)
        for ghost in self.ghosts:
            ghost.render_w, ghost.render_h = render_dim
        self.menu_map = Map(
            render_dim,
            self.config.width,
            self.config.height,
            self.config.seed,
            self.config.points_per_pacgum,
            self.config.points_per_super_pacgum
        )
        self.menu_map.cell_maze = MENU_MAP

    def debug(self) -> None:
        """Overlay debug information
        (state, positions, ghost status) on the screen."""

        # draw debug rectangle (transparent)
        debug_rect = pg.Surface((self.w//3, self.h//4))
        debug_rect.set_alpha(40)
        debug_rect.fill((255, 255, 255))
        self.screen.blit(debug_rect, (0, int(self.h*0.75)))

        # draw debug info
        debug_info: list[str] = [
            f"State: {self.state.name}"
        ]
        if not self.playing:
            debug_info.append(
                f"Selected: {self.curr_menu.sel_label}"
            )

        if self.playing:
            debug_info.append(
                f"Player pos: {self.player.x:.2f}, {self.player.y:.2f}"
            )
            for ghost in self.ghosts:
                debug_info.append(
                    (f"{ghost.name.name} state: {ghost.state.name} "
                     f"direction: {ghost.dir.name}")
                )
            debug_info.append(
                f"Vulnerability: {self.player.vulnerable}"
            )

        info_x: int = self.w//50
        info_y: int = int(self.h*0.78)
        for info in debug_info:
            outlined_text(
                text=info,
                screen=self.screen,
                font=self.debug_font,
                thickness=1,
                coords=(info_x, info_y)
            )
            self.screen.blit(
                self.debug_font.render(
                    text=info,
                    antialias=True,
                    color='white'
                ),
                dest=(info_x, info_y)
            )
            info_y += int(self.debug_font.get_height()*1.1)

    def create_ghosts(self) -> list[Ghost]:
        """Instantiate the four ghosts and place them at the maze corners.

        Creates ``blinky``, ``pinky``, ``inky``, and ``clyde`` at the four
        corners of the cell grid.
        """

        maze_w = len(self.map.cell_maze[0])
        maze_h = len(self.map.cell_maze)

        ghosts: list[Ghost] = list()
        render_dim = (self.render_w, self.render_h)
        ghosts.append(
            Ghost(
                render_dim, 1.5, maze_h - 1.5, GhostType.BLINKY, FRAMES_BLINKY,
                FRAMES_BLINKY_DAM,
                GHOST_COLOR_M[0], self.config.points_per_ghost))
        ghosts.append(
            Ghost(render_dim, maze_w - 1.5, 1.5, GhostType.PINKY,
                  FRAMES_PINKY, FRAMES_PINKY_DAM,
                  GHOST_COLOR_M[1], self.config.points_per_ghost))
        ghosts.append(
            Ghost(render_dim, maze_w - 1.5, maze_h - 1.5, GhostType.INKY,
                  FRAMES_INKY,
                  FRAMES_INKY_DAM,
                  GHOST_COLOR_M[2], self.config.points_per_ghost))
        ghosts.append(
            Ghost(render_dim, 1.5, 1.5, GhostType.CLYDE, FRAMES_CLYDE,
                  FRAMES_CLYDE_DAM,
                  GHOST_COLOR_M[3], self.config.points_per_ghost))

        return ghosts

    def end_level(self, state: GameState) -> None:
        """Freeze gameplay and transition to the end screen for *state*.

        Injects the current score and level into the end menu, resets its
        animation progress, and starts the transition timer.

        Args:
            state: The end-game state to display
                (``GAME_OVER``, ``VICTORY``, or ``FINAL_VICTORY``).
        """
        end_menu = cast(EndMenu, self.menus[state])
        self.player.score += int(self.time_left*5)
        end_menu.score = self.player.score
        end_menu.level = self.curr_lvl
        end_menu.done = False
        end_menu._progress = 0.0
        self.state = state
        self.playing = False
        self.menu_transition = True
        self.transition_t = 0.0

    def new_level(self) -> None:
        """Reset the map, ghosts, and timers to start the next level.

        Uses the configured seed for level 1 and a time-based seed for
        subsequent levels so each run produces a different maze.
        """

        if self.curr_lvl == 1:
            seed = self.config.seed
        else:
            seed = int(time.time())

        # recreate the map
        self.map = Map(
            (self.render_w, self.render_h),
            width=self.config.width,
            height=self.config.height,
            seed=seed,
            pacgum_pts=self.config.points_per_pacgum,
            super_pacgum_pts=self.config.points_per_super_pacgum
        )
        self.mini_map = Mini_map(self.map, self.size_mini_map,
                                 self.pos_mini_map)

        # reload/reset ghosts/player
        self.ghosts = self.create_ghosts()
        if self.curr_lvl == 1:
            self.player = Player(self.config.lives, self.map.center)
        else:
            self.player.new_spawn(self.map.center)
        self.time_left = self.config.level_max_time + 1
        self.damage_flash_timer = 0.0
        self.cheat.player = self.player
        self.cheat.ghosts = self.ghosts
        self.cheat.map = self.map

    def ghost_hit(self, ghost: Ghost) -> None:
        """Handle a collision between the player and a ghost.

        If the player is still within the invincibility window the hit is
        ignored.  If the ghost is vulnerable the ghost takes damage instead.
        Otherwise the player loses one hit point and the invincibility
        cooldown is reset.

        Args:
            ghost: The ghost that collided with the player.
        """

        if not self.player.vulnerable or ghost.state == GhostState.DEAD:
            return

        if ghost.state == GhostState.VULNERABLE:
            self.sound_manager.play(GHOST_HEAT_SOUND)
            ghost.state = GhostState.DEAD
            ghost.speed = SPEED_GHOST * 2
            ghost.next_pos = ghost.spawn
            ghost.take_damage()
            self.player.score += ghost.point_value
        else:
            self.sound_manager.play(GHOST_SOUND)
            self.player.die()
            self.damage_flash_timer = DAMAGE_FLASH_DURATION
            blinky_pos = [g.pos for g in self.ghosts
                          if g.name == GhostType.BLINKY][0]
            for s_ghost in self.ghosts:
                s_ghost.pos = s_ghost.spawn
                s_ghost.set_target(self.map.cell_maze, self.player.pos,
                                   blinky_pos, self.player.angle)
            if self.player.hp == 0:
                self.end_level(GameState.GAME_OVER)

    def update_entities(self, dt: float) -> None:
        """Advance pacgum pickup logic and ghost AI
        for one tick of *dt* seconds.

        Args:
            dt: Elapsed time in seconds since the last frame.
        """

        # Pacgums
        for _, pacgum in self.map.pacgum_dict.items():
            pacgum.update(self.player)
            if pacgum.check_pickup():
                self.map.remaining_pacgum = max(
                    0, self.map.remaining_pacgum - 1)
                self.player.score += pacgum.value
                if isinstance(pacgum, SuperPacgum):
                    self.sound_manager.play(S_PACGUM_SOUND)
                    for ghost in self.ghosts:
                        ghost.set_vulnerable()
                else:
                    self.sound_manager.play(PACGUM_SOUND)

        # Ghosts
        blinky_pos = [g.pos for g in self.ghosts
                      if g.name == GhostType.BLINKY][0]
        for ghost in self.ghosts:
            ghost.update(self.player)
            if ghost.check_hit():
                self.ghost_hit(ghost)
            ghost.play_anim(dt)
            ghost.check_state(dt)
            dx = ghost.x - ghost.next_pos[0]
            dy = ghost.y - ghost.next_pos[1]
            if ghost.state != GhostState.DEAD and (dx * dx + dy * dy) < 0.01:
                ghost.set_target(self.map.cell_maze, self.player.pos,
                                 blinky_pos, self.player.angle)
            ghost.move(dt)

        # Player
        self.player.check_state(dt)

    def render_menu(self, acc_time: float) -> None:
        """Draw the animated 3-D background and the current menu overlay.

        Args:
            acc_time: Accumulated game time in seconds.
        """

        self.render_surf.fill("black")
        self.menu_player.render_x += 0.005
        if self.menu_player.render_x > 25.5:
            self.menu_player.render_x = MENU_POS[0]
        self.menu_map.draw(
            self.render_surf, self.menu_player, self.menu_ghosts, acc_time)

        scaled = pg.transform.scale(self.render_surf, self.window_size)
        self.screen.blit(scaled, (0, 0))
        self.curr_menu.render(self.screen, acc_time)

    def play(self) -> None:
        """Run the main event/update/render loop until the player quits."""

        running: bool = True
        dt: float = 0.0
        pressed: int | None = None
        first: bool = False
        pressed_t: float = 0.0
        pressed_tot_t: float = 0.0
        key_acc: float = 0.2

        pg.mouse.set_visible(False)

        while running:
            pg.event.set_grab(True)
            first = False

            # load current state
            if self.state in self.menus:
                self.curr_menu = self.menus[self.state]
                self.playing = False
            else:
                self.playing = True

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    running = False
                    break
                elif (
                    event.type == pg.MOUSEMOTION
                    and self.state == GameState.PLAY
                ):
                    dx, _ = event.rel
                    self.player.set_rotation(dx)
                elif event.type == pg.KEYDOWN:
                    pressed = event.key
                    first = True
                    pressed_t = 1
                elif event.type == pg.KEYUP:
                    if event.key == pressed:
                        pressed = None
                        key_acc = 0.2
                        pressed_tot_t = 0

            # CLOCK
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            if self.menu_transition:
                self.transition_t += dt
                if self.state in [GameState.GAME_OVER, GameState.VICTORY,
                                  GameState.FINAL_VICTORY]:
                    cast(EndMenu, self.menus[self.state])._progress = min(
                        self.transition_t / self.END_SCREEN_DURATION, 1.0
                    )

            # GAME
            if self.state in [GameState.PLAY, GameState.PAUSE_MENU]:
                self.sound_manager.play(AMBIANT_SOUND, -1)
                self.sound_manager.stop(MENU_SOUND)
                self.render_surf.fill("black")

                if self.state == GameState.PLAY:
                    self.damage_flash_timer = max(
                        0.0, self.damage_flash_timer - dt
                    )
                    if self.damage_flash_timer <= 0.0:
                        self.time_left -= dt
                        self.player.move(self.map.cell_maze, dt)
                        self.update_entities(dt)
                        if self.state == GameState.PLAY:
                            if self.map.remaining_pacgum == 0:
                                if self.curr_lvl >= self.config.max_levels:
                                    self.end_level(GameState.FINAL_VICTORY)
                                else:
                                    self.end_level(GameState.VICTORY)
                            elif self.time_left <= 0:
                                self.player.die()
                                self.damage_flash_timer = DAMAGE_FLASH_DURATION
                                self.time_left = self.config.level_max_time + 1
                                if self.player.hp == 0:
                                    self.end_level(GameState.GAME_OVER)
                        self.cheat.check_input(events, dt)
                self.map.draw(self.render_surf, self.player, self.ghosts, dt)
                self.hud.render(
                    screen=self.render_surf,
                    player=self.player,
                    level=self.curr_lvl,
                    time=self.time_left
                    )
                if self.damage_flash_timer > 0.0:
                    self.hud.draw_damage_flash(self.render_surf)

                scaled = pg.transform.scale(self.render_surf, self.window_size)
                self.screen.blit(scaled, (0, 0))

                self.mini_map.draw(
                    self.screen,
                    (self.player.x, self.player.y),
                    self.ghosts,
                    dt,
                    self.player.angle
                    )

                key = pg.key.get_just_pressed()
                if key[pg.K_c]:
                    self.cheat.ghost_vuln()
                if key[pg.K_g]:
                    self.cheat.ghost_freeze()

            # END SCREEN
            if self.state in [GameState.GAME_OVER, GameState.VICTORY,
                              GameState.FINAL_VICTORY]:
                self.render_surf.fill("black")
                self.map.draw(self.render_surf, self.player, self.ghosts, dt)
                self.hud.render(
                    screen=self.render_surf,
                    player=self.player,
                    level=self.curr_lvl,
                    time=self.time_left
                )
                scaled = pg.transform.scale(self.render_surf, self.window_size)
                self.screen.blit(scaled, (0, 0))
                self.mini_map.draw(
                    self.screen,
                    (self.player.x, self.player.y),
                    self.ghosts,
                    dt,
                    self.player.angle
                )
                self.menus[self.state].render(self.screen, self.acc_time)

            # MENUS
            if not self.playing:
                self.sound_manager.play(MENU_SOUND, -1)
                if self.state in [GameState.PAUSE_MENU]:
                    self.curr_menu.render(self.screen, self.acc_time)
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY,
                                    GameState.FINAL_VICTORY]:
                    pass
                else:
                    self.sound_manager.stop(AMBIANT_SOUND)
                    self.render_menu(self.acc_time)

            # CRT EFFECT
            # apply_crt_effect(self.screen, time=self.acc_time)

            # USER INPUT
            if pressed and pg.key.get_pressed()[pressed]:
                key_acc += 0.015
            if key_acc > 3.5:
                key_acc = 3.5
            if not self.playing and pressed is not None:
                new_state = self.curr_menu.handle_key(
                    state=self.state,
                    key=pressed,
                    first=first,
                    delay=pressed_t,
                    tot_t=pressed_tot_t
                    )
                if self.state == GameState.SETTINGS_MENU:
                    self.sound_manager.set_master_volume(
                        self.setting.volume / 100
                    )
                if new_state != self.state:
                    if self.state == GameState.SETTINGS_MENU:
                        self.config = self.setting.to_config()
                        self.new_level()
                        self.curr_lvl = 1
                        if self.setting.window_size != self.window_size:
                            self.update_window(new_state)
                    if (
                        self.state == GameState.PAUSE_MENU
                        and new_state == GameState.MAIN_MENU
                    ):
                        self.new_level()
                    if (
                        self.state == GameState.ENTER_NAME
                        and new_state == GameState.HIGH_SCORES
                    ):
                        name = cast(Enter_Name_Menu,
                                    self.menus[GameState.ENTER_NAME]).name
                        self.high_score.add_score(self.player.score, name)
                        # self.high_score.to_json(
                        #     self.config.highscores_filename
                        # )
                        cast(HighScoresMenu,
                             self.menus[GameState.HIGH_SCORES]).high_scores = (
                            self.high_score.scores
                        )
                        self.new_level()
                    pg.mouse.set_pos(self.w//2, self.h//2)
                    self.state = new_state
                    pressed = None
                    if self.state == GameState.PLAY:
                        self.start_time = self.acc_time

            # exit if player presse one key
            if (
                self.menu_transition
                and self.state in [
                    GameState.GAME_OVER,
                    GameState.VICTORY,
                    GameState.FINAL_VICTORY
                ]
                and cast(EndMenu, self.menus[self.state]).done
                and self.transition_t > TRANSITION_E_TIME
            ):
                self.menu_transition = False
                if self.state in [GameState.GAME_OVER,
                                  GameState.FINAL_VICTORY]:
                    self.curr_lvl = 1
                    if self.high_score.is_high(self.player.score):
                        enter = cast(Enter_Name_Menu,
                                     self.menus[GameState.ENTER_NAME])
                        enter.score = self.player.score
                        enter.rank = self.high_score.get_rank(
                            self.player.score)
                        enter.name = ""
                        self.state = GameState.ENTER_NAME
                    else:
                        self.new_level()
                        self.state = GameState.MAIN_MENU
                elif self.state == GameState.VICTORY:
                    self.curr_lvl += 1
                    self.new_level()
                    self.state = GameState.PLAY
                pressed = None

            if pressed == pg.K_ESCAPE:
                if self.state == GameState.PLAY:
                    self.state = GameState.PAUSE_MENU
                elif self.state == GameState.PAUSE_MENU:
                    self.state = GameState.PLAY
                else:
                    pass
                pressed = None

            if pressed_t > 0.1:
                pressed_t = 0
            if self.state == GameState.QUIT:
                running = False
                break

            # DEBUG
            # self.debug()

            pg.display.flip()
            # dt = self.clock.tick(60)/1000
            pressed_t += dt * key_acc
            pressed_tot_t += dt
            self.acc_time += dt
