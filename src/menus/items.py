"""Concrete menu-item types used to populate game menus."""

from .base import Item


class MenuItem(Item):
    """Standard clickable menu item that navigates to a target game state."""

    pass


class SettingsItem(Item):
    """Menu item used in the settings screen."""

    pass
