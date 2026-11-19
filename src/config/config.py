"""Configuration constants for the Pac-Man raycasting game.

Defines window dimensions, cardinal direction bitmasks, projection
parameters, colors, and mini-map display settings used throughout
the engine.
"""

import pygame as pg
from ..utils.paths import resource_path, get_scores_path

# config
CONFIG_FILE = resource_path("data/config.json")


# Window Size
RENDER_W = 800
RENDER_H = 600
WINDOW_W = 800
WINDOW_H = 600

# Side
W, S, E, N = 0b1000, 0b0100, 0b0010, 0b0001

# ID Element
VOID = 0
WALL = 1
PACGUM = 2
SUPER_PACGUM = 3

# Map Projection
FOV = 60
COEF_DIST_PROJ = 0.75
DIST_SHADE = 8
SKY_COLOR = (1, 9, 13)
FLOOR_COLOR = (1, 9, 13)
WALL_TEX = resource_path("assets/sprites/Texture/wall_tex.png")

# Mini Map
DIAMETER_M = 0.15
MIN_MINI_MAP_SIZE = 120
POS_X_M = 0.6
POS_Y_M = 0.6
BORDER_COLOR = (5, 53, 135)
SIZE_MINI_MAP = 12
SPRITE_SIZE_M = 1.5
COLOR_WALL = (20, 20, 255)
COLOR_PACGUM = (237, 204, 161)
GHOST_SIZE_M = 4
GHOST_COLOR_M = [
    (255, 0, 0),
    (255, 184, 255),
    (0, 255, 255),
    (255, 184, 82),
    (255, 255, 255)
]
PACMAN_FRAMES_M = resource_path("assets/sprites/Texture/pacman_mini_map")
GHOST_BLINKY_M = resource_path("assets/sprites/Texture/blinky_mini_map")
GHOST_CLYDE_M = resource_path("assets/sprites/Texture/clyde_mini_map")
GHOST_INKY_M = resource_path("assets/sprites/Texture/inky_mini_map")
GHOST_PINKY_M = resource_path("assets/sprites/Texture/pinky_mini_map")
GHOST_VULN_M = resource_path(
    "assets/sprites/Texture/vulenerable_ghost_mini_map")
GHOST_DEATH_M = resource_path("assets/sprites/Texture/deat_ghost_mini_map")

# Player
START_P_ANGLE = 90
SPEED = 3
MOUSE_SENSITIVITY = 0.1
MARGIN_COLLISION_WALL = 0.2
INVINCIBILITY_COOLDOWN = 2
DAMAGE_FLASH_DURATION: float = 0.15
BOB_AMPLITUDE_P = 5
BOB_SPEED_P = 1.5
LEAN_AMOUNT = 0.3
LEAN_ROLL = 40
LEAN_SPEED = 8.0
LEAN_WALL_MARGIN = 0.03

# Sprite
SPRITE_SCALE = 0.4
SPRITE_BOB_AMP = 6
SPRITE_BOB_SPEED = 0.5
FAR_VIEW_PACGUM = 6
FAR_VIEW_GHOST = 10

# Pacgum
DIST_PICKUP_PACGUM = 0.5
PACGUM_TEX = resource_path("assets/sprites/Texture/pacgum.png")
SUPER_PACGUM_TEX = resource_path("assets/sprites/Texture/superpacgum.png")

# Ghost
DIST_GHOST_HIT = 0.5
GHOST_SCALE = 0.8
VULNERABILITY_TIME = 10
CHASE_TIME = 24
RAND_TIME = 7
SPEED_GHOST = 1.8
ANIM_FPS = 5
FRAMES_BLINKY = resource_path("assets/sprites/Texture/ghost_sprites/blinky")
FRAMES_CLYDE = resource_path("assets/sprites/Texture/ghost_sprites/clyde")
FRAMES_INKY = resource_path("assets/sprites/Texture/ghost_sprites/inky")
FRAMES_PINKY = resource_path("assets/sprites/Texture/ghost_sprites/pinky")
FRAMES_VULN = resource_path("assets/sprites/Texture/ghost_sprites/vulnerable")
FRAMES_BLINKY_DAM = resource_path(
    "assets/sprites/Texture/ghost_sprites/blinky_dam")
FRAMES_CLYDE_DAM = resource_path(
    "assets/sprites/Texture/ghost_sprites/clyde_dam")
FRAMES_INKY_DAM = resource_path(
    "assets/sprites/Texture/ghost_sprites/inky_dam")
FRAMES_PINKY_DAM = resource_path(
    "assets/sprites/Texture/ghost_sprites/pinky_dam")

# Font
FONT = resource_path("assets/fonts/spooky.otf")
FONT_COLOR = (255, 233, 0)
OUT_COLOR = (0, 0, 0)
OUT_RATIO = 0.05

# Menus
SH_ANGLE = 310
SH_SIZE = 0.18
BG_COLOR = (0, 0, 180)
PAC_MENU = resource_path("assets/sprites/pac_2d/pac_menu.png")
PAC_SHADOW = resource_path("assets/sprites/pac_2d/pac_shadow.png")
GHOST_SPRITES: list[list[str]] = [
    [resource_path("assets/sprites/b0.png"),
     resource_path("assets/sprites/b1.png")],
    [resource_path("assets/sprites/p0.png"),
     resource_path("assets/sprites/p1.png")],
    [resource_path("assets/sprites/r0.png"),
     resource_path("assets/sprites/r1.png")],
    [resource_path("assets/sprites/o0.png"),
     resource_path("assets/sprites/o1.png")],
]
MENU_MAP = [
    [1] + [1]*50 + [1],
    [1] + [0]*50 + [1],
    [1] + [1]*50 + [1]
]
MENU_ANGLE = 0
MENU_POS = (15.5, 1.5)

# Cheat
DELAY = 0.5
EXTRA_LIVE = 1
SEQ_ADD_LIFE = [pg.K_UP, pg.K_UP, pg.K_DOWN,
                pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]
SEQ_INVICBLE_A = [pg.K_UP, pg.K_RIGHT, pg.K_DOWN,
                  pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN]
# SEQ_INVICBLE_A = [pg.K_UP, pg.K_UP, pg.K_LEFT]
SEQ_INVICBLE_D = [pg.K_UP, pg.K_UP, pg.K_UP]
SEQ_G_FREEZE_A = [pg.K_DOWN, pg.K_DOWN, pg.K_UP, pg.K_UP,
                  pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
SEQ_G_FREEZE_D = [pg.K_DOWN, pg.K_DOWN, pg.K_DOWN]
SEQ_G_VULN = [pg.K_LEFT, pg.K_RIGHT, pg.K_LEFT,
              pg.K_RIGHT, pg.K_LEFT]
SEQ_NEXT_L = [pg.K_UP, pg.K_RIGHT, pg.K_UP, pg.K_LEFT,
              pg.K_DOWN, pg.K_RIGHT, pg.K_DOWN]
# SEQ_NEXT_L = [pg.K_DOWN, pg.K_DOWN, pg.K_LEFT]

# Path finding
PINKY_FRONT_PAC = 4
INKY_FRONT_PAC = 2
CLYDE_DIST_PAC = 4

# Scoring
PATH_SCORE = get_scores_path()

# Sound
AMBIANT_SOUND = "ambiant"
AMBIANT_PATH = resource_path('data/sound/ambiant.mp3')
PACGUM_SOUND = "pacgum_take"
PACGUM_S_PATH = resource_path('data/sound/pacgum_take.wav')
S_PACGUM_SOUND = "s_pacgum"
S_PACGUM_S_PATH = resource_path("data/sound/super_pacgum_take.wav")
GHOST_SOUND = "ghost"
GHOST_S_PATH = resource_path("data/sound/ghost_hit.wav")
GHOST_HEAT_SOUND = "ghost_heat"
GHOST_HEAT_S_PATH = resource_path("data/sound/ghost_heat.wav")
MENU_SOUND = "menu"
MENU_SOUND_PATH = resource_path("data/sound/menu.mp3")

# End screen
GAME_OVER_FADE = 2.0
TRANSITION_E_TIME = 0.5
T_END_TIME = 0.17
CONTENT_END_TIME = 0.30
