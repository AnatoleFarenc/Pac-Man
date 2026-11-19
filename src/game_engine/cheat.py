"""Cheat-code handler that listens for keyboard
sequences and applies effects."""

from typing import List
import pygame as pg

from .player import Player
from .map import Map
from ..entity.ghost import Ghost
from ..config.config import (
    INVINCIBILITY_COOLDOWN,
    SPEED_GHOST,
    EXTRA_LIVE,
    SEQ_G_FREEZE_A, SEQ_G_FREEZE_D, SEQ_G_VULN,
    SEQ_INVICBLE_A, SEQ_INVICBLE_D, SEQ_ADD_LIFE,
    SEQ_NEXT_L,
    DELAY
)


class Cheat():
    """Monitors keyboard input and applies cheat
    effects when sequences are matched."""

    def __init__(self, player: Player, ghosts: List[Ghost], map: Map) -> None:
        """Bind the cheat system to *player*, *ghosts* and *map*.

        Args:
            player: The player instance whose state may be modified.
            ghosts: List of ghost entities that may be modified.
            map: The current map (used for level skip).
        """
        self.player = player
        self.ghosts = ghosts
        self.map = map
        self.input_history: list[int] = []
        self.ntime = 0.0
        self.delay = DELAY

    def check_input(self, events: List[pg.Event], dt: float) -> None:
        """Process *events* and trigger any matching cheat sequence.

        The input history is cleared after *delay* seconds of inactivity.

        Args:
            events: List of pygame events from the current frame.
            dt: Elapsed time in seconds since the last frame.
        """
        self.ntime += dt
        if self.ntime > self.delay:
            self.input_history.clear()

        for event in events:
            if event.type == pg.KEYDOWN:
                self.ntime = 0.0

                self.input_history.append(event.key)

                def ends_with(seq: list[int]) -> bool:
                    return self.input_history[-len(seq):] == seq

                if ends_with(SEQ_ADD_LIFE):
                    self.add_life()
                    self.input_history.clear()
                elif ends_with(SEQ_G_VULN):
                    self.ghost_vuln()
                    self.input_history.clear()
                elif ends_with(SEQ_INVICBLE_A):
                    self.invincible_activated()
                    self.input_history.clear()
                elif ends_with(SEQ_INVICBLE_D):
                    self.invincible_deactivated()
                    self.input_history.clear()
                elif ends_with(SEQ_G_FREEZE_A):
                    self.ghost_freeze()
                    self.input_history.clear()
                elif ends_with(SEQ_G_FREEZE_D):
                    self.ghost_unfreeze()
                    self.input_history.clear()
                elif ends_with(SEQ_NEXT_L):
                    self.skip_level()
                    self.input_history.clear()

    def add_life(self) -> None:
        """Add one extra life to the player."""
        self.player.hp += EXTRA_LIVE

    def ghost_vuln(self) -> None:
        """Force all ghosts into the VULNERABLE state."""
        for ghost in self.ghosts:
            ghost.set_vulnerable()

    def invincible_activated(self) -> None:
        """Grant the player permanent invincibility by
        setting an infinite cooldown."""
        self.player.invincibility_cooldown = float("inf")
        self.player.vulnerable = False

    def invincible_deactivated(self) -> None:
        """Restore the player's normal invincibility cooldown."""
        self.player.invincibility_cooldown = INVINCIBILITY_COOLDOWN
        self.player.vulnerable = True

    def ghost_freeze(self) -> None:
        """Stop all ghosts by setting their speed to zero."""
        for ghost in self.ghosts:
            ghost.speed = 0

    def ghost_unfreeze(self) -> None:
        """Restore all ghosts to their normal movement speed."""
        for ghost in self.ghosts:
            ghost.speed = SPEED_GHOST

    def skip_level(self) -> None:
        """Skip the current level by clearing all remaining pacgums."""
        self.map.remaining_pacgum = 0
