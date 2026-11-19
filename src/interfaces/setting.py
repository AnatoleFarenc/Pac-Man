"""User-facing game settings, separate from the internal Config model."""

import random
from dataclasses import dataclass
from ..config.data import Config
from ..config.config import WINDOW_W, WINDOW_H


@dataclass(frozen=True)
class _FieldDef:
    label: str
    attr: str
    min_val: int | None
    max_val: int | None
    step: int
    options: tuple[tuple[int, int] | str, ...] | None = None
    slider: bool = False


class Setting:
    """Holds all user-adjustable game settings and exposes a menu-friendly API.
    """

    LIVES_MIN = 1
    LIVES_MAX = 9
    TIME_MIN = 10
    TIME_MAX = 9999
    TIME_STEP = 10
    MAP_MIN = 4
    MAP_MAX = 21
    WINDOW_PRESETS: tuple[tuple[int, int], ...] = (
        (800, 600),
        (1920, 1080),
        (3840, 2160)
    )
    WINDOW_RESOLUTION: tuple[tuple[int, int], ...] = (
        (600, 400),
        (800, 600),
        (1920, 1080)
    )

    _FIELDS: list[_FieldDef] = [
        _FieldDef("Lives", "lives", LIVES_MIN, LIVES_MAX, 1),
        _FieldDef("Time (s)", "level_max_time", TIME_MIN, TIME_MAX, TIME_STEP),
        _FieldDef("Seed", "seed", None, None, 1),
        _FieldDef("Width map", "width", MAP_MIN,   MAP_MAX, 1),
        _FieldDef("Height map", "height", MAP_MIN, MAP_MAX, 1),
        _FieldDef("Window", "window_preset_idx", 0, None, 1, WINDOW_PRESETS),
        _FieldDef("Resolution", "resolution_preset_idx", 0,
                  None, 1, WINDOW_RESOLUTION),
        _FieldDef("Volume", "volume", 0, 100, 5, slider=True),
    ]

    def __init__(self, config: Config) -> None:
        """Populate initial values from a validated *config*.

        Args:
            config: The game configuration to seed settings from.
        """
        self.lives: int = config.lives
        self.level_max_time: int = config.level_max_time
        self.seed: int = config.seed
        self.width: int = config.width
        self.height: int = config.height
        self.max_levels: int = config.max_levels
        self.volume: int = 50
        self.window_preset_idx: int = 1
        if (WINDOW_W, WINDOW_H) in self.WINDOW_PRESETS:
            self.window_preset_idx = self.WINDOW_PRESETS.index(
                (WINDOW_W, WINDOW_H))
        self.resolution_preset_idx: int = 1

    @property
    def window_size(self) -> tuple[int, int]:
        return self.WINDOW_PRESETS[self.window_preset_idx]

    @property
    def resolution(self) -> tuple[int, int]:
        return self.WINDOW_RESOLUTION[self.resolution_preset_idx]

    @property
    def field_count(self) -> int:
        return len(self._FIELDS)

    def is_slider(self, index: int) -> bool:
        return self._FIELDS[index].slider

    def raw_value(self, index: int) -> int:
        return int(getattr(self, self._FIELDS[index].attr))

    def slider_bounds(self, index: int) -> tuple[int, int]:
        f = self._FIELDS[index]
        return (f.min_val or 0, f.max_val or 100)

    def label(self, index: int) -> str:
        return self._FIELDS[index].label

    def display(self, index: int) -> str:
        f = self._FIELDS[index]
        if f.options is not None:
            val = f.options[getattr(self, f.attr)]
            if isinstance(val, str):
                return val
            w, h = val
            return f"{w}x{h}"
        return str(getattr(self, self._FIELDS[index].attr))

    def adjust(self, index: int, delta: int) -> None:
        """Increment or decrement the setting at *index* by one step."""
        f = self._FIELDS[index]
        current: int = getattr(self, f.attr)
        if f.options is not None:
            new_val = max(0, min(len(f.options) - 1, current + delta))
        else:
            new_val = current + delta * f.step
            if f.min_val is not None:
                new_val = max(f.min_val, new_val)
            if f.max_val is not None:
                new_val = min(f.max_val, new_val)
        setattr(self, f.attr, new_val)

    def randomize_seed(self) -> None:
        self.seed = random.randint(0, 99999)

    def to_config(self) -> Config:
        """Return a validated Config built from the current setting values."""
        return Config(
            lives=self.lives,
            level_max_time=self.level_max_time,
            seed=self.seed,
            width=self.width,
            height=self.height,
            max_levels=self.max_levels,
        )
