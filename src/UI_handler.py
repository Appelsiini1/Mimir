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

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS, COURSE_GENERAL_TAGS, VARIATION_KEY_LIST
from src.data_handler import FILEPATHCARRIER, save_course_info, save_assignment, get_empty_variation
from src.set_generator import temp_creator
from src.ui_helper import VARIATION, set_style, setup_textures, help_, add_variation, cancel_variation, close_window


def _stop():
    logging.info("Stopping program.")
    dpg.stop_dearpygui()
    dpg.destroy_context()


def setup_ui():
    """
    Shorthand for calling all UI setup functions
    """
    set_style()
    setup_textures()


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



def _add_example_run_header(
    sender: int | str, app_data, user_data: tuple[VARIATION, int | str, int | str]
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
                help_(DISPLAY_TEXTS["help_inputs"][LANGUAGE])
                dpg.add_input_text(
                    multiline=True, height=150, tab_input=True, tag=ex_run.add_uuid()
                )
                dpg.add_spacer(height=5)
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE])
                dpg.add_input_text(tag=ex_run.add_uuid())
                output_text_id = ex_run.add_uuid()
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE])
                    help_(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE])
                    dpg.add_checkbox(
                        tag=ex_run.add_uuid(),
                        callback=_toggle_enabled,
                        user_data=output_text_id,
                    )
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE])
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
                help_(DISPLAY_TEXTS["help_output_filename"][LANGUAGE])
                dpg.add_input_text(tag=ex_run.add_uuid())
        dpg.add_spacer(height=5)


def _add_variation_window(sender, app_data, user_data: tuple):
    variation_id, var_letter = add_variation(user_data[0])
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE] + " " + var_letter
    user_data[1].append(label)
    ex_run_group_uuid = user_data[0].get_variation(variation_id).get_ex_run_group()
    UUIDs = {'{}'.format(i):dpg.generate_uuid() for i in VARIATION_KEY_LIST}

    with dpg.window(
        label=label, tag=variation_id, width=750, height=700, no_close=True
    ):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_inst"][LANGUAGE])
                dpg.add_input_text(multiline=True, height=150, tab_input=True)
                dpg.add_spacer(width=5)
                with dpg.group(tag=ex_run_group_uuid):
                    _add_example_run_header(
                        None, None, (user_data[0], variation_id, ex_run_group_uuid)
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
        help_(DISPLAY_TEXTS["help_used_in"][LANGUAGE])
        dpg.add_input_text()
        dpg.add_spacer(width=5)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_import_codefiles"][LANGUAGE], callback=None
            )
            dpg.add_spacer(width=5)
            dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE])
        dpg.add_spacer(height=5)
        with dpg.group():
            dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=None, user_data=VARIATION)
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE],
                callback=cancel_variation,
                user_data=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
            )


def _assignment_window(sender, app_data, user_data):
    """
    UI components for "Add assingment" window
    """
    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE],
    )
    var = VARIATION()
    variation_listbox = None
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
                        help_(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=150, tag=UI_ITEM_TAGS["ASSIGNMENT_NO"])
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE] + ":"
                        )
                        help_(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE])
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
                    items = []
                    dpg.add_listbox(items)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE],
                    callback=_add_variation_window,
                    user_data=(var, variation_listbox),
                )
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=None, user_data=var)
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
