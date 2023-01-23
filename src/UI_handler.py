"""
Mímir UI Handler

Functions to handle UI
"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join
import dearpygui.dearpygui as dpg
from string import ascii_uppercase
from itertools import product

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS
from src.common import resource_path

VARIATIONS = 1
EXAMPLE_RUNS = 1


def _stop():
    logging.info("Stopping program.")
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


def _setup_textures():
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


def setup_ui():
    """
    Shorthand for calling all UI setup functions
    """
    _set_style()
    _setup_textures()

def _help(message):
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

def _toggle_enabled(sender, app_data, item):
    if dpg.is_item_enabled(item):
        dpg.disable_item(item)
    else:
        dpg.enable_item(item)


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
        header1_label = DISPLAY_TEXTS["ui_info"][LANGUAGE]
        with dpg.collapsing_header(label=header1_label, default_open=True):
            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    with dpg.table(header_row=False):
                        dpg.add_table_column(
                            label="Course info one",
                            width_fixed=True,
                            init_width_or_weight=200,
                        )
                        dpg.add_table_column(
                            label="Course info two",
                            width_fixed=True,
                            init_width_or_weight=410,
                        )
                        with dpg.table_row():
                            dpg.add_text(DISPLAY_TEXTS["ui_course_id"][LANGUAGE] + ":")
                            dpg.add_input_text(
                                callback=None, width=400, hint="No course selected"
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_name"][LANGUAGE] + ":"
                            )
                            dpg.add_input_text(callback=None, width=400)
                        with dpg.table_row():
                            dpg.add_text(DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE] + ":")
                            dpg.add_input_int(
                                callback=None, width=150, min_value=0, min_clamped=True
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_assignments_index"][LANGUAGE] + ":"
                            )
                            dpg.add_text("0", tag=UI_ITEM_TAGS["total_index"])
                dpg.add_spacer(width=100)
                dpg.add_image("mimir_logo")
            dpg.add_spacer(height=25)
        header2_label = DISPLAY_TEXTS["ui_assignment_set"][LANGUAGE]
        with dpg.collapsing_header(label=header2_label):
            dpg.add_text("Under construction", indent=25)
        header3_label = DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE]
        with dpg.collapsing_header(label=header3_label):
            dpg.add_text("Under construction", indent=25)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    with dpg.table(header_row=False):
                        dpg.add_table_column(
                            label="Course info one",
                            width_fixed=True,
                            init_width_or_weight=200,
                        )
                        dpg.add_table_column(
                            label="Course info two",
                            width_fixed=True,
                            init_width_or_weight=410,
                        )
                        with dpg.table_row():
                            dpg.add_button(label=DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE], callback=add_assignment_window)

def _add_variation_letter():
    VARIATIONS += 1
    return _get_variation_letter(VARIATIONS)

def _get_variation_letter(var):
    map_size = round(var/676) if var > 676 else 2 if var > 26 else 1
    combinations_map = map(''.join, product(ascii_uppercase, repeat=map_size))
    comb_list = list(combinations_map)
    return comb_list[var-1]


def _add_example_run_header(example_run_no):
    pass

def _add_variation_header(variation_id):
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE] + variation_id
    with dpg.collapsing_header(label=label):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_inst"][LANGUAGE])



def add_assignment_window():
    """
    UI components for "Add assingment" window
    """
    label = (
        "Mímir - {} - {}".format(DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE])
    )
    with dpg.window(label=label, width=750, height=700):
        header1_label = DISPLAY_TEXTS['ui_general'][LANGUAGE]
        with dpg.collapsing_header(label=header1_label, default_open=True):
            dpg.add_spacer(width=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.table(header_row=False):
                    dpg.add_table_column(
                        label="Assignment info one",
                        width_fixed=True,
                        init_width_or_weight=200,
                    )
                    dpg.add_table_column(
                        label="Assignment info two",
                        width_fixed=True,
                        init_width_or_weight=410,
                    )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_assignment_title"][LANGUAGE] + ":")
                        dpg.add_input_text(callback=None, width=400)
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_lecture_week"][LANGUAGE] + ":"
                        )
                        dpg.add_input_int(
                            callback=None, width=150, min_value=0, min_clamped=True
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_assignment_no"][LANGUAGE] + ":")
                        _help(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=150)
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE] + ":"
                        )
                        _help(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=400)
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE] + ":")
                        dpg.add_checkbox(callback=_toggle_enabled, tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"], user_data=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE])
                        dpg.add_combo(("Testi1", "Testi2", "Testi3"), default_value="", enabled=False, tag=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE])
                        dpg.add_combo(("Python", "C"), tag=UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_inst_lang"][LANGUAGE])
                        dpg.add_combo(("Python", "C"), tag=UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"])


