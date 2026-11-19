# Refactor Plan — Game Architecture

## 1. State Pattern for Game States

**Problem:** `play()` (~250 lines) is a monolithic loop with interleaved `if self.state == ...` blocks for update, render, input, sound, and transitions.

**Approach:**
- Each `GameState` enum value maps to a state object with `update(game, dt)` and `render(game)`.
- `update()` returns the next `GameState` to transition to, or `None` to stay.
- Each state handles its own transition side effects (e.g. `SettingsMenuState.update()` calls `game.new_level()` before returning `MAIN_MENU`).
- The state object receives the `Game` instance to read/write shared data (`player`, `map`, `ghosts`, `time_left`, etc.).
- The game loop becomes state-agnostic:
  1. Gather events
  2. Tick clock
  3. `new_state = current_state.update(game, dt)`
  4. Swap state if needed
  5. `current_state.render(game)`
  6. `pg.display.flip()`

**States to extract:**
- `PlayState` — player movement, entity updates, collision, timer, cheat input, HUD, minimap
- `PauseMenuState` — pause overlay, resume/quit
- `MainMenuState`, `HowToState`, `HighScoresState`, `SettingsMenuState`, `CheatMenuState` — menu wrappers
- `EndScreenState` — shared by GAME_OVER, VICTORY, FINAL_VICTORY (parameterized or subclassed)
- `EnterNameState` — name entry, score saving

**State-independent (stays in loop):**
- `pg.event.get()`, quit handling
- Clock tick / dt calculation
- `pg.display.flip()`
- Key repeat tracking (`pressed`, `pressed_t`, `key_acc`)

---

## 2. Renderer Extraction

**Problem:** Rendering logic (surface filling, scaling, blitting, CRT effect) is mixed into the game loop and duplicated across state blocks (e.g. PLAY and END_SCREEN both do `render_surf.fill` -> `map.draw` -> `hud.render` -> `transform.scale` -> `blit` -> `mini_map.draw`).

**Approach:**
- Extract a `Renderer` class that owns `render_surf`, `screen`, `window_size`.
- Provide methods like `begin_frame()`, `end_frame()`, `scale_and_blit()`.
- State `render()` methods call into `Renderer` instead of manipulating surfaces directly.
- Centralizes any post-processing (CRT effect) in one place.

---

## 3. InputHandler Extraction

**Problem:** Input processing (event loop, key repeat logic, mouse grab, escape handling) is spread across the game loop with local variables (`pressed`, `pressed_t`, `key_acc`, `first`).

**Approach:**
- Extract an `InputHandler` class that owns key repeat state and processes raw `pg.event` lists.
- Exposes clean queries: `is_pressed(key)`, `just_pressed(key)`, `mouse_dx()`, `escape_pressed()`.
- State `update()` methods query the `InputHandler` (via `game.input`) instead of raw pygame calls.
- Eliminates the scattered key repeat arithmetic from the loop.

---

## 4. Fix Private Field Access (ARCH-03)

**Problem:** `Game` directly sets `EndMenu._progress` via `cast()`.

**Approach:**
- Add a public `set_progress(value)` method to `EndMenu`.
- With the state pattern, `EndScreenState.update()` calls `menu.set_progress(...)` — no cast needed.

---

## 5. Move Cheat Shortcuts into `Cheat` (ARCH-07)

**Problem:** Hardcoded `K_c` / `K_g` checks in the game loop bypass `Cheat.check_input`.

**Approach:**
- Move these into `Cheat.check_input()` or into `PlayState.update()` as part of the cheat system.
- Remove the raw key checks from the loop.

---

## 6. Config as a Passable Object (ARCH-05)

**Problem:** Config values are scattered module-level constants. Changing resolution requires manually propagating to every object that cached them.

**Approach:**
- Config is already partially an object (`self.config`). Ensure all subsystems reference `game.config` instead of caching their own copies of `render_w`, `render_h`, etc.
- When settings change, subsystems pick up new values on next frame automatically.

---

## Suggested Order

1. **State pattern** — biggest impact, untangles `play()`.
2. **InputHandler** — simplifies state `update()` methods immediately after.
3. **Renderer** — simplifies state `render()` methods.
4. **Cheat shortcuts** — small, do alongside PlayState.
5. **EndMenu private field** — small, do alongside EndScreenState.
6. **Config passthrough** — can be incremental.
