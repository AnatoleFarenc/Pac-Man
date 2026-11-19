# Code Review — PAC_MAN Project

## 1. Bugs & Logic Errors

All bugs have been fixed.

---

## 2. Code Quality & Refactoring Opportunities

### CQ-06: Redundant computation in `Sprite.draw` (kept intentionally)
**File:** `src/entity/Sprite.py:154`
`sprite_cor_dist` differs from `self.cor_dist` due to the `max(0.1, ...)` clamp in `proj()`. The unclamped value is correct for depth testing. Not a safe replacement.

### CQ-09: Duplicate `sort` calls in `HighScores` (kept intentionally)
`self.scores.sort(...)` is called in `__init__`, `add_score`, and `to_json`. Defensive but accepted.

---

## 3. Architecture Concerns

### ARCH-01: God class — `Game` owns everything
`Game` handles window management, game state machine, entity updates, rendering, input processing, menu transitions, sound control, and cheat processing — all in one class. This makes it hard to modify any subsystem without risking regressions elsewhere.

**Suggestion:** Extract a `StateManager`, `Renderer`, and `InputHandler` at minimum.

### ARCH-02: Monolithic game loop — `play()` is ~250 lines
**File:** `src/game/game.py:428-679`
The main loop contains deeply nested state-dependent branches for rendering, input, transitions, and entity updates all interleaved. This makes the control flow very hard to follow and debug.

**Suggestion:** Each state could have its own `update()` and `render()` methods, dispatched via the state machine.

### ARCH-03: Tight coupling via `cast()` and private field access
**File:** `src/game/game.py:293, 479`
```python
cast(EndMenu, self.menus[state])._progress = ...
```
`Game` directly manipulates `_progress` (a private field) on `EndMenu`. This breaks encapsulation and makes it impossible to change `EndMenu` internals without updating `Game`.

### ARCH-04: No separation between update and render
`Map.draw()` both computes sprite state (sorting, distance) and renders. The `update_entities()` method in `Game` also mixes game logic (pickup, scoring, state transitions) with entity updates. Splitting update and render phases would make the code more testable and predictable.

### ARCH-05: Config constants are scattered globals
All configuration lives in `config.py` as module-level constants. Changing resolution or window size requires manually propagating values to every object that cached them (`render_w`, `render_h` on sprites, ghosts, map, HUD). A single config object passed by reference would be cleaner.

### ARCH-06: No tests
There are zero tests in the project. Core logic like A* pathfinding, collision detection, score management, and config loading are all testable in isolation but have no coverage. This makes refactoring risky.

### ARCH-07: Cheat shortcuts leak into the game loop
**File:** `src/game/game.py:532-535`
```python
if key[pg.K_c]:
    self.cheat.ghost_vuln()
if key[pg.K_g]:
    self.cheat.ghost_freeze()
```
These hardcoded key checks bypass the `Cheat` class's sequence-matching system. They should either be removed (debug leftovers) or moved into `Cheat.check_input`.
