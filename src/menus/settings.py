"""Settings menu screen."""

import pygame as pg
from math import sin
from typing import Sequence
from ..game.states import GameState
from ..interfaces.setting import Setting
from .base import Menu, Item


class SettingsMenu(Menu):
    """Menu for adjusting game settings."""

    def __init__(
            self,
            title: str,
            items: Sequence[Item],
            window_size: tuple[int, int],
            setting: Setting
    ) -> None:
        """Initialize the settings menu.

        Args:
            title: Title string displayed at the top.
            items: Sequence containing the back-button item.
            window_size: ``(width, height)`` of the display window in pixels.
            setting: The ``Setting`` instance whose values are edited.
        """
        super().__init__(title, items, window_size)
        self.setting: Setting = setting
        self.sel_item = 0
        self.sel_label = self.setting.label(0)

    @property
    def _heading_font(self) -> pg.Font:
        """Use the smaller subtitle font for the name-entry title."""
        return self.subtitle_font

    def render(self, screen: pg.Surface, time: float) -> None:
        """Draw the background, title, content, and ghost bar each frame.

        Args:
            screen: Target pygame surface.
            time: Accumulated game time used to animate the title bob.
        """

        self.delta = sin(time) * self._delta_scale
        # gradient_background(screen=screen, color=self.bg_color)
        self._draw_title(screen=screen)
        self._draw_content(screen=screen)

    def _total_items(self) -> int:
        return self.setting.field_count + 1  # +1 for Back

    def _draw_slider_bar(
        self,
        screen: pg.Surface,
        font: pg.Font,
        y: int,
        field_idx: int,
        selected: bool,
        label_x: int,
        value_x_right: int,
    ) -> None:
        val = self.setting.raw_value(field_idx)
        min_val, max_val = self.setting.slider_bounds(field_idx)
        label = self.setting.label(field_idx)

        pct_text = f"{val}%"
        pct_w = font.size(pct_text)[0]
        margin = self.w // 40

        bar_left = label_x + font.size(label)[0] + margin
        bar_right = value_x_right - pct_w - margin
        bar_w = max(0, bar_right - bar_left)
        bar_h = max(4, font.get_height() // 4)
        bar_y = y + (font.get_height() - bar_h) // 2

        pg.draw.rect(screen, (60, 60, 60), (bar_left, bar_y, bar_w, bar_h),
                     border_radius=bar_h // 2)
        fill_ratio = (val - min_val) / max(1, max_val - min_val)
        fill_w = int(bar_w * fill_ratio)
        bar_color = (255, 220, 0) if selected else (160, 130, 0)
        if fill_w > 0:
            pg.draw.rect(screen, bar_color,
                         (bar_left, bar_y, fill_w, bar_h),
                         border_radius=bar_h // 2)

        pct_x = value_x_right - pct_w
        self._draw_element(pct_text, screen, font, (pct_x, y))

    def _draw_content(self, screen: pg.Surface) -> None:
        start_y = self.h // 3.8
        row_h = int(self.item_font.get_linesize())
        label_x = self.w // 4
        value_x_right = self.w * 3 // 4

        for i in range(self.setting.field_count):
            selected = (i == self.sel_item)
            font = self.small_sel_font if selected else self.small_item_font
            y = int(start_y + i * row_h)
            label = self.setting.label(i)

            if selected:
                icon_x = label_x - int(self.sel_icon.width * 1.5)
                icon_y = y + font.get_height() // 2 - self.sel_icon.height // 2
                self._draw_icon(screen=screen, icon_x=int(icon_x),
                                icon_y=int(icon_y))

            self._draw_element(label, screen, font, (label_x, y))

            if self.setting.is_slider(i):
                self._draw_slider_bar(
                    screen, font, y, i, selected, label_x, value_x_right
                )
            else:
                value = (f"< {self.setting.display(i)} >"
                         if selected else self.setting.display(i))
                val_x = value_x_right - font.size(value)[0]
                self._draw_element(value, screen, font, (val_x, y))

        self._draw_back_btn(screen)

    def _draw_back_btn(self, screen: pg.Surface) -> None:
        selected = (self.sel_item == self.setting.field_count)
        font = self.sel_font if selected else self.item_font
        label = self.items[0].label

        item_y = self.h - self.h // 8
        item_x = (self.w - font.size(label)[0]) // 2

        if selected:
            icon_x = item_x - int(self.sel_icon.width * 1.5)
            icon_y = (item_y + font.get_height() // 2 -
                      self.sel_icon.height // 2)
            self._draw_icon(screen=screen, icon_x=icon_x, icon_y=icon_y)

        self._draw_element(label, screen, font, (item_x, item_y))

    def handle_key(
            self,
            state: GameState,
            key: int,
            first: bool,
            delay: float,
            tot_t: float
    ) -> GameState:
        total = self._total_items()

        if (delay > 0.1 and tot_t > 0.8) or first:
            match key:
                case pg.K_UP:
                    self.sel_item = (self.sel_item - 1) % total
                case pg.K_DOWN:
                    self.sel_item = (self.sel_item + 1) % total
                case pg.K_LEFT:
                    if self.sel_item < self.setting.field_count:
                        self.setting.adjust(self.sel_item, -1)
                case pg.K_RIGHT:
                    if self.sel_item < self.setting.field_count:
                        self.setting.adjust(self.sel_item, +1)
                case pg.K_r:
                    if (self.sel_item < self.setting.field_count
                            and self.setting._FIELDS[self.sel_item].attr ==
                            "seed"):
                        self.setting.randomize_seed()
                case pg.K_RETURN:
                    if self.sel_item == self.setting.field_count:
                        state = self.items[0].action

        self.sel_label = (
            self.setting.label(self.sel_item)
            if self.sel_item < self.setting.field_count
            else self.items[0].label
        )
        return state
