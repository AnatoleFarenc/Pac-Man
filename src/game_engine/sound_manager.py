"""Centralised sound effect manager with per-channel volume control."""

import pygame as pg

from ..config.config import (
    AMBIANT_SOUND, PACGUM_SOUND,
    AMBIANT_PATH, PACGUM_S_PATH,
    S_PACGUM_SOUND, S_PACGUM_S_PATH,
    GHOST_SOUND, GHOST_S_PATH,
    GHOST_HEAT_SOUND, GHOST_HEAT_S_PATH,
    MENU_SOUND, MENU_SOUND_PATH
)


class Sound_Manager:
    """Manage all game sound effects with a master volume knob."""

    _BASE_VOLUMES: dict[str, float] = {
        AMBIANT_SOUND: 0.05,
        PACGUM_SOUND: 0.1,
        S_PACGUM_SOUND: 0.1,
        GHOST_SOUND: 1.0,
        GHOST_HEAT_SOUND: 0.3,
        MENU_SOUND: 1.0,
    }

    def __init__(self) -> None:
        """Load all sound assets and apply the default master volume."""
        self._master: float = 0.5
        self.sounds = {
            AMBIANT_SOUND: pg.mixer.Sound(AMBIANT_PATH),
            PACGUM_SOUND: pg.mixer.Sound(PACGUM_S_PATH),
            S_PACGUM_SOUND: pg.mixer.Sound(S_PACGUM_S_PATH),
            GHOST_SOUND: pg.mixer.Sound(GHOST_S_PATH),
            GHOST_HEAT_SOUND: pg.mixer.Sound(GHOST_HEAT_S_PATH),
            MENU_SOUND: pg.mixer.Sound(MENU_SOUND_PATH)
        }
        self._apply_volumes()

    def _apply_volumes(self) -> None:
        """Recompute and set each channel's volume from base * master."""
        for name, base in self._BASE_VOLUMES.items():
            if name in self.sounds:
                self.sounds[name].set_volume(base * self._master)

    def set_master_volume(self, vol: float) -> None:
        """Set the master volume, clamped to ``[0.0, 1.0]``."""
        self._master = max(0.0, min(1.0, vol))
        self._apply_volumes()

    def play(self, name: str, loops: int = 0) -> None:
        """Play the sound identified by *name*. Pass ``loops=-1`` to loop."""
        if name in self.sounds:
            sound = self.sounds[name]
            if loops < 0 and sound.get_num_channels() > 0:
                return
            sound.play(loops)

    def stop(self, name: str) -> None:
        """Stop playback of the sound identified by *name*."""
        if name in self.sounds:
            self.sounds[name].stop()
