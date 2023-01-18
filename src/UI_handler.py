"""
Mímir UI Handler

Functions to handle UI
"""

# pylint: disable=import-error
import logging
from os.path import join
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE
from src.common import resource_path


def _stop():
    dpg.stop_dearpygui()
    dpg.destroy_context()


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


def _set_style():
    """
    Set colours, fonts etc.
    """
    fonts = _load_fonts()
    dpg.bind_font(fonts["default"])

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


def _setup_textures():
    dpg.add_texture_registry(
        label="Mimir Texture Container", tag="__main_texture_container"
    )

    width, height, channels, data = dpg.load_image(resource_path("resource/logo.png"))
    dpg.add_static_texture(
        width=width,
        height=height,
        default_value=data,
        tag="mimir_logo",
        label="Mímir Logo",
        parent="__main_texture_container",
    )

def setup_ui():
    """
    Shorthand for calling all UI setup functions
    """
    _set_style()
    _setup_textures()

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
        with dpg.menu_bar():
            with dpg.menu(label=DISPLAY_TEXTS["menu_file"][LANGUAGE]):
                # TODO Add callbacks
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_create"][LANGUAGE], callback=None
                )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_open"][LANGUAGE], callback=None
                )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_open_recent"][LANGUAGE], callback=None
                )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_update"][LANGUAGE], callback=None
                )

            dpg.add_menu_item(
                label=DISPLAY_TEXTS["menu_exit"][LANGUAGE], callback=_stop
            )
        tree_node1_label = DISPLAY_TEXTS["ui_info"][LANGUAGE]
        with dpg.collapsing_header(label=tree_node1_label, default_open=True):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_course_id"][LANGUAGE] + ":")
                    dpg.add_input_text(callback=None)

                dpg.add_image("mimir_logo")
