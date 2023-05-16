"""Mímir UI helper functions for callbacks"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join
from os import getcwd
from string import ascii_uppercase
from tkinter import filedialog
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS, COURSE_GENERAL_TAGS
from src.data_handler import FILEPATHCARRIER, save_course_info, save_assignment, get_empty_variation
from src.common import resource_path

################################

class VARIATION:
    def __init__(self) -> None:
        self.variations = []

    def get_all_variations(self) -> list:
        """Get current list of variations"""
        return self.variations

    def get_var_count(self) -> int:
        """Returns how many variations are saved"""
        return len(self.variations)

    def add_variation(self, data:dict) -> None:
        """Add variation dict to list"""
        self.variations.append(data)

    def delete_var(self, var_letter) -> None:
        found = next((i for i, item in enumerate(self.variations) if item["variation_id"] == var_letter), None)
        if found:
            self.variations.remove(found)

################################

def _load_fonts():
    """
    Loads default fonts. Returns a dict of loaded fonts.
    """
    _fonts = {}
    with dpg.font_registry():
        _fonts["default"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Regular.ttf")
            ),
            24,
        )
        _fonts["italic"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Italic.ttf")
            ),
            24,
        )
        _fonts["bold"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Bold.ttf")
            ),
            24,
        )

    return _fonts


def set_style():
    """
    Set colours, fonts etc.
    """
    fonts = _load_fonts()
    dpg.bind_font(fonts["default"])
    logging.info("Fonts loaded.")

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(
                dpg.mvThemeCol_Button, (105, 90, 138), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBg, (157, 0, 255), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (105, 90, 138, 162),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core
            )

    dpg.bind_theme(global_theme)
    logging.info("Theme setup finished.")


def setup_textures():
    """
    Setup textures and texture registry
    """
    dpg.add_texture_registry(
        label="Mimir Texture Container", tag="__main_texture_container"
    )

    width, height, _, data = dpg.load_image(resource_path("resource/logoV3.png"))
    dpg.add_static_texture(
        width=width,
        height=height,
        default_value=data,
        tag="mimir_logo",
        label="Mímir Logo",
        parent="__main_texture_container",
    )
    i = 1  # number of textures added so far
    logging.info("Texture registry added, with %d textures inside." % i)

def help_(message):
    """
    Display help popup "(?)" next to the title with 'message' in it.
    From DearPyGUI demo
    """
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text("(?)", color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)

def add_variation(var: VARIATION) -> tuple[int | str, str]:
    new_id = dpg.generate_uuid()
    letter = _get_variation_letter(var.get_var_count())
    return new_id, letter


def _get_variation_letter(var):
    base = len(ascii_uppercase)
    result = ""
    while var > 0:
        result = ascii_uppercase[(var - 1) % base] + result
        var = (var - 1) // base
    return result


def cancel_variation(sender, app_data, user_data):
    pass


def close_window(sender: None, app_data: None, window_id: int | str):
    """
    Closes a UI window.

    Params:
    sender: Not used.
    app_data: Not used.
    window_id: The UUID of the window to close.
    """
    dpg.delete_item(window_id)