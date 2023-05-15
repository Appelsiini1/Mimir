"""
Mímir UI Handler

Functions to handle UI
"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join
from os import getcwd
from string import ascii_uppercase
from tkinter import filedialog
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS, COURSE_GENERAL_TAGS
from src.data_handler import FILEPATHCARRIER, save_course_info, save_assignment
from src.common import resource_path
from src.set_generator import temp_creator


class _EX_RUN_UUIDS:
    def __init__(self) -> None:
        self.uuid = dpg.generate_uuid()
        self.item_uuids = []

    def add_uuid(self) -> int | str:
        """Adds item UUID to the internal list and returns the generated UUID"""
        new_id = dpg.generate_uuid()
        self.item_uuids.append(new_id)
        return new_id

    def get_group_uuid(self) -> int | str:
        """Returns the parent UUID"""
        return self.uuid

    def get_item_uuids(self) -> list:
        """Returns a list of item UUIDs inside the parent"""
        return self.item_uuids


class _VARIATION_UUIDS:
    def __init__(self) -> None:
        self.variation_uuid = dpg.generate_uuid()
        self.ex_run_group_uuid = dpg.generate_uuid()
        self.letter = ""
        self.example_runs = []

    def add_ex_run(self) -> _EX_RUN_UUIDS:
        """Adds an example run and returns an example run instance"""
        new_ex_run = _EX_RUN_UUIDS()
        self.example_runs.append(new_ex_run)
        return new_ex_run

    def get_ex_runs(self) -> list:
        """Returns a list of all example runs"""
        return self.example_runs

    def get_ex_run_group(self):
        """Returns the parent ID of the example run header group"""
        return self.ex_run_group_uuid

    def get_run_number(self):
        """Returns amount of example runs currently present"""
        return len(self.example_runs)

    def get_uuid(self) -> int | str:
        """Returns the variation uuid"""
        return self.variation_uuid


class _VARIATION:
    def __init__(self) -> None:
        self.variations = []

    def get_all_variations(self) -> list:
        """Get current list of variations"""
        return self.variations

    def get_var_count(self) -> int:
        """Returns how many variations are saved"""
        return len(self.variations)

    def get_variation(self, v_id) -> _VARIATION_UUIDS:
        """Returns variation with variation id 'v_id'"""
        for var in self.variations:
            if var.get_uuid() == v_id:
                return var
        return None

    def add_variation(self) -> int | str:
        """Add one to variations and return the new variation id"""
        new = _VARIATION_UUIDS()
        new_id = new.get_uuid()
        self.variations.append(new)
        return new_id


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

# def _create_AA_warning_popup():
#     """
#     Creates warning popup for "Add assignment" window ready for use later.
#     """

#     with dpg.popup(
#         parent=UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"],
#         mousebutton=dpg.mvMouseButton_Left,
#         tag=UI_ITEM_TAGS["WARNING_POPUP_ADD_ASSIG_WINDOW"],
#         modal=True,
#     ):
#         dpg.add_spacer(height=5)
#         dpg.add_text(DISPLAY_TEXTS["ui_assig_man_warning_popup"][LANGUAGE])
#         dpg.add_spacer(height=5)
#         dpg.add_separator()
#         dpg.add_spacer(height=5)
#         dpg.add_button(
#             label=DISPLAY_TEXTS["ui_ok"][LANGUAGE],
#             callback=lambda: dpg.configure_item(UI_ITEM_TAGS["WARNING_POPUP_ADD_ASSIG_WINDOW"], show=False),
#             user_data=UI_ITEM_TAGS["WARNING_POPUP_ADD_ASSIG_WINDOW"],
#             width=75,
#         )

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
    # TODO Move label to a normal text bc primary window hides title bar
    label = "Mímir - " + DISPLAY_TEXTS["ui_main"][LANGUAGE]
    with dpg.window(
        label=label,
        width=1484,
        height=761,
        menubar=True,
        no_close=True,
        no_move=True,
        tag=UI_ITEM_TAGS["MAIN_WINDOW"],
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
                            init_width_or_weight=230,
                        )
                        dpg.add_table_column(
                            label="Course info two",
                            width_fixed=True,
                            init_width_or_weight=410,
                        )
                        with dpg.table_row():
                            dpg.add_text(DISPLAY_TEXTS["ui_course_id"][LANGUAGE] + ":")
                            dpg.add_input_text(
                                callback=None, width=400, hint="No course selected", tag=UI_ITEM_TAGS["COURSE_ID"]
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_name"][LANGUAGE] + ":"
                            )
                            dpg.add_input_text(callback=None, width=400, tag=UI_ITEM_TAGS["COURSE_TITLE"])
                        with dpg.table_row():
                            dpg.add_text(DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE] + ":")
                            dpg.add_input_int(
                                callback=None, width=150, min_value=0, min_clamped=True, tag=UI_ITEM_TAGS["COURSE_WEEKS"]
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_assignments_index"][LANGUAGE] + ":"
                            )
                            dpg.add_text("0", tag=UI_ITEM_TAGS["total_index"])
                        with dpg.table_row():
                            dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=save_course_info, user_data=COURSE_GENERAL_TAGS)
                dpg.add_spacer(width=50)
                dpg.add_image("mimir_logo")
            dpg.add_spacer(height=25)
        header2_label = DISPLAY_TEXTS["ui_assignment_set"][LANGUAGE]
        with dpg.collapsing_header(label=header2_label):
            dpg.add_text("Under construction", indent=25)

            #dpg.add_button(label="Avaa...", callback=_openfilebrowser, user_data=files)
            dpg.add_button(label="Luo tehtäväpaperi", callback=temp_creator, user_data=None)
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
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE],
                                callback=open_new_assignment_window,
                                tag=UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"],
                                user_data=False
                            )


def _add_variation(var: _VARIATION) -> tuple[int | str, str]:
    new_id = var.add_variation()
    letter = _get_variation_letter(var.get_var_count())
    var.get_variation(new_id)
    return new_id, letter


def _get_variation_letter(var):
    base = len(ascii_uppercase)
    result = ""
    while var > 0:
        result = ascii_uppercase[(var - 1) % base] + result
        var = (var - 1) // base
    return result


def _add_example_run_header(
    sender: int | str, app_data, user_data: tuple[_VARIATION, int | str, int | str]
):
    var = user_data[0].get_variation(user_data[1])
    parent_group = user_data[2]
    ex_run = var.add_ex_run()
    label = DISPLAY_TEXTS["ex_run"][LANGUAGE] + " " + str(var.get_run_number())
    with dpg.collapsing_header(
        label=label, parent=parent_group, tag=ex_run.get_group_uuid()
    ):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ex_input"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_inputs"][LANGUAGE])
                dpg.add_input_text(
                    multiline=True, height=150, tab_input=True, tag=ex_run.add_uuid()
                )
                dpg.add_spacer(height=5)
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE])
                dpg.add_input_text(tag=ex_run.add_uuid())
                output_text_id = ex_run.add_uuid()
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE])
                    _help(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE])
                    dpg.add_checkbox(
                        tag=ex_run.add_uuid(),
                        callback=_toggle_enabled,
                        user_data=output_text_id,
                    )
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_ex_output"][LANGUAGE])
                dpg.add_input_text(tag=output_text_id, multiline=True, height=150)
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_import_datafiles"][LANGUAGE],
                        callback=None,
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE])
                # TODO Add selectable file list
                dpg.add_text(DISPLAY_TEXTS["ui_output_filename"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_output_filename"][LANGUAGE])
                dpg.add_input_text(tag=ex_run.add_uuid())
        dpg.add_spacer(height=5)


def _add_variation_header(sender, app_data, user_data: _VARIATION):
    variation_id, var_letter = _add_variation(user_data)
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE] + " " + var_letter
    ex_run_group_uuid = user_data.get_variation(variation_id).get_ex_run_group()
    with dpg.collapsing_header(
        label=label, parent=UI_ITEM_TAGS["VARIATION_GROUP"], tag=variation_id
    ):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE])
                _help(DISPLAY_TEXTS["help_inst"][LANGUAGE])
                dpg.add_input_text(multiline=True, height=150, tab_input=True)
                dpg.add_spacer(width=5)
                with dpg.group(tag=ex_run_group_uuid):
                    _add_example_run_header(
                        None, None, (user_data, variation_id, ex_run_group_uuid)
                    )
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        dpg.add_button(
            label=DISPLAY_TEXTS["ui_add_ex_run"][LANGUAGE],
            callback=_add_example_run_header,
            user_data=(user_data, variation_id, ex_run_group_uuid),
        )
        dpg.add_spacer(height=5)
        dpg.add_text(DISPLAY_TEXTS["ui_used_in"][LANGUAGE])
        _help(DISPLAY_TEXTS["help_used_in"][LANGUAGE])
        dpg.add_input_text()
        dpg.add_spacer(width=5)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_import_codefiles"][LANGUAGE], callback=None
            )
            dpg.add_spacer(width=5)
            dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE])
        dpg.add_spacer(height=5)


def _assignment_window(sender, app_data, user_data):
    """
    UI components for "Add assingment" window
    """
    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE],
    )
    var = _VARIATION()
    with dpg.window(
        label=label,
        width=750,
        height=700,
        tag=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
        no_close=True,
    ):
        header1_label = DISPLAY_TEXTS["ui_general"][LANGUAGE]
        with dpg.collapsing_header(label=header1_label, default_open=True):
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.table(header_row=False):
                    dpg.add_table_column(
                        label="Assignment info one",
                        width_fixed=True,
                        init_width_or_weight=220,
                    )
                    dpg.add_table_column(
                        label="Assignment info two",
                        width_fixed=True,
                        init_width_or_weight=450,
                    )
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_title"][LANGUAGE] + ":"
                        )
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TITLE"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_lecture_week"][LANGUAGE] + ":")
                        dpg.add_input_int(
                            callback=None, width=150, min_value=0, min_clamped=True, tag=UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"]
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_assignment_no"][LANGUAGE] + ":")
                        _help(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=150, tag=UI_ITEM_TAGS["ASSIGNMENT_NO"])
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE] + ":"
                        )
                        _help(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TAGS"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE] + ":")
                        dpg.add_checkbox(
                            callback=_toggle_enabled,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
                            user_data=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE])
                        dpg.add_combo(
                            # TODO Previous part combobox
                            ("Testi1", "Testi2", "Testi3"),
                            default_value="",
                            enabled=False,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE])
                        dpg.add_combo(
                            ("Python", "C"), tag=UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"]
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_inst_lang"][LANGUAGE])
                        dpg.add_combo(
                            #TODO do dynamically
                            (DISPLAY_TEXTS['language_FI'][LANGUAGE], DISPLAY_TEXTS['language_ENG'][LANGUAGE]),
                            tag=UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"],
                        )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group(tag=UI_ITEM_TAGS["VARIATION_GROUP"]):
                    _add_variation_header(None, None, var)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE],
                    callback=_add_variation_header,
                    user_data=var,
                )
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=None, user_data=_VARIATION)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE],
                    callback=close_window,
                    user_data=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
                )
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_delete"][LANGUAGE], callback=None
                )


def open_new_assignment_window():
    """
    A function to check whether the 'Add assingment' window is already open.
    If it is not, open it.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"]):
        _assignment_window(None, None, None)



def close_window(sender: None, app_data: None, window_id: int | str):
    """
    Closes a UI window.

    Params:
    sender: Not used.
    app_data: Not used.
    window_id: The UUID of the window to close.
    """
    dpg.delete_item(window_id)




