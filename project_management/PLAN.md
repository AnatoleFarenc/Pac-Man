# PAC-MAN — Project Plan

## Done

- [x] CLI argument handling (single config file path)
- [x] Config parsing and loading (pydantic, robust error handling)
- [x] High scores parsing, storage, and loading
- [x] Maze generation via mazegenerator package

---

## Build Order

### 1. Map
**Owner: Anatole**

The Map class wraps the mazegenerator output and exposes a clean interface to the rest of the game:
- Query whether a world-space position is a wall
- Convert between grid coordinates and world-space coordinates (using a CELL_SIZE constant)
- Provide spawn positions: player center, ghost corners, pacgum/super-pacgum locations

The internal representation (expanded grid, edge-based, etc.) is Anatole's decision.

### 2. Player
**Owner: TBD**

- Continuous position (x, y floats) and direction angle in world space
- 4-directional movement (WASD / arrow keys)
- Wall collision using the Map interface
- State: lives, current score, invincibility flag (for cheat mode)
- Respawns at maze center on death

### 3. Raycaster
**Owner: Anatole**

- Casts rays from the player's position using their angle and FOV
- Queries the Map at each step to detect wall hits
- Computes projected wall slice heights for each screen column
- Renders the 3D view to the pygame surface

### 4. Pacgums
**Owner: TBD**

- Placed in corridor cells at level init (most corridors → regular pacgums, 4 corners → super-pacgums)
- Eaten on player contact → score update, check win condition
- Super-pacgum → triggers ghost frightened state for a duration

### 5. Ghosts
**Owner: TBD**

- 4 ghosts, one per corner, each with a home corner for respawn
- Two behaviors: chase (normal) and flee (frightened after super-pacgum)
- Respawn at home corner after being eaten (after a delay)
- Pathfinding uses the Map interface

---

## Game Class and State Machine

A central `Game` class owns:
- The main pygame loop
- A `GameState` enum to track current state
- References to all game objects (map, player, ghosts, pacgums)
- One rendering/update method per state

### GameState enum

```
MAIN_MENU
PLAYING
PAUSED
GAME_OVER
VICTORY
FINAL_VICTORY (all levels completed)
NAME_ENTRY
```

### State flow

```
MAIN_MENU → PLAYING → PAUSED → PLAYING
                     → GAME_OVER → NAME_ENTRY → MAIN_MENU
                     → VICTORY  → NAME_ENTRY → MAIN_MENU
```

### UI screens (methods on Game)

- `draw_main_menu()` — title, start, highscores, instructions, exit
- `draw_hud()` — score, lives, level, remaining time (always visible during PLAYING)
- `draw_pause()` — resume / return to main menu
- `draw_game_over()` — final score
- `draw_victory()` — final score + congratulations
- `draw_final_victory()` — special screen when arriving at the game's end
- `draw_name_entry()` — text input for highscore name (max 10 chars, alphanumeric)

---

## Level Progression

- Level 1: fixed seed (from config)
- Levels 2+: random seed
- At least 10 levels total
- Score and lives carry over between levels
- Each level has a time limit (`level_max_time` from config)
- Time out → configurable consequence (restart level or game over)

---

## Menus

Two independent menu classes — no shared base class, navigation logic is simple enough not to warrant inheritance.

### NavigationMenu
- A list of selectable options navigated with keyboard (up/down/enter)
- Used for: main menu, pause menu

### SettingsMenu
- A list of key/value pairs that can be edited
- Used for: config menu, cheat menu

### Standalone screens (not menu classes)
- **High scores screen** — display only, no navigation
- **Name entry screen** — text input, fundamentally different interaction model

---

## Cheat Mode

Activated during gameplay (keyboard shortcut TBD or in pause menu):
- Invincibility (ghosts cannot kill player)
- Ghost freeze
- Level skip
- Extra lives

---

## Team Split Summary

| Feature | Owner |
|---|---|
| Config / scores / CLI | Ben |
| Map + Raycaster | Anatole |
| Player | TBD |
| Pacgums | TBD |
| Ghosts | TBD |
| Game loop + UI | TBD |
| Menus | Ben |
