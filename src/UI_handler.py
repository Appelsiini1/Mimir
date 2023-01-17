"""
Mímir UI Handler
Functions to handle UI
"""

# pylint: disable=import-error
import logging
import dearpygui.dearpygui as dpg
from os.path import join

from src.constants import DISPLAY_TEXTS, LANGUAGE
from src.common import resource_path


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
    dpg.mvThemeCol_TitleBgActive = [157, 0, 255]
    dpg.mvThemeCol_Button = [105, 90, 138]
    dpg.mvThemeCol_ButtonHovered = [105, 90, 231, 162]


def _viewport_menu():
    with dpg.viewport_menu_bar():
        with dpg.menu(label=DISPLAY_TEXTS["menu_file"][LANGUAGE]):
            # TODO Add callbacks
            dpg.add_menu_item(label=DISPLAY_TEXTS["menu_create"][LANGUAGE], callback=None)
            dpg.add_menu_item(label=DISPLAY_TEXTS["menu_open"][LANGUAGE], callback=None)
            dpg.add_menu_item(label=DISPLAY_TEXTS["menu_open_recent"][LANGUAGE], callback=None)
            dpg.add_menu_item(label=DISPLAY_TEXTS["menu_update"][LANGUAGE], callback=None)

        dpg.add_menu_item(label=DISPLAY_TEXTS["menu_exit"][LANGUAGE], callback=None)

def main_window():
    """
    Create main window
    """
    label = "Mímir - " + DISPLAY_TEXTS["ui_main"][LANGUAGE]
    with dpg.window(
        label=label,
        width=1484,
        height=761,
        menubar=True,
        no_collapse=True,
        no_close=True,
        no_move=True,
    ):
        tree_node1_label = DISPLAY_TEXTS["ui_general"][LANGUAGE]
        with dpg.collapsing_header(label=tree_node1_label, default_open=True):
            dpg.add_text("Hello world!")
