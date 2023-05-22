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

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS, COURSE_GENERAL_TAGS, VARIATION_KEY_LIST, EXAMPLE_RUN_KEY_LIST
from src.data_handler import save_course_info, save_assignment, get_empty_variation, path_leaf, get_empty_assignment, get_empty_example_run
from src.set_generator import temp_creator
from src.ui_helper import set_style, setup_textures, help_, get_variation_letter, close_window, get_files, remove_selected, extract_exrun_data, extract_variation_data


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


def _toggle_enabled(sender, app_data, item:int|str):
    """
    Toggles item on or off depending on its previous state
    """
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



def _add_example_run_window(
    sender, app_data, user_data: tuple[dict, int]
):
    """
    Adds an example run input window
    """
    var = user_data[0]
    ix = user_data[1]
    new = False
    try:
        ex_run = var["example_runs"][ix]
    except IndexError:
        ex_run = get_empty_example_run()
        new = True
    
    UUIDs = {'{}'.format(i):dpg.generate_uuid() for i in EXAMPLE_RUN_KEY_LIST}
    window_id = dpg.generate_uuid()
    label = DISPLAY_TEXTS["ex_run"][LANGUAGE] + " " + str(user_data[1])
    with dpg.window(
        label=label, tag=window_id, width=750, height=700, no_close=True
    ):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():

                # Inputs
                dpg.add_text(DISPLAY_TEXTS["ex_input"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_inputs"][LANGUAGE])
                dpg.add_input_text(
                    multiline=True, height=150, tab_input=True, tag=UUIDs["INPUTS"]
                )
                dpg.add_spacer(height=5)

                # Command line inputs
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE])
                dpg.add_input_text(tag=UUIDs["CMD_INPUTS"])
                
                # Generate ex run checkbox
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE])
                    help_(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE])
                    dpg.add_checkbox(
                        tag=UUIDs["GEN_EX"],
                        callback=_toggle_enabled,
                        user_data=UUIDs["OUTPUT"],
                    )
                
                # Output text
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE])
                dpg.add_input_text(tag=UUIDs["OUTPUT"], multiline=True, height=150)
                dpg.add_spacer(height=5)
                
                # Output files
                dpg.add_text(DISPLAY_TEXTS["ui_output_filename"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_output_filename"][LANGUAGE])
                with dpg.group():
                    files = [] if not ex_run["outputfiles"] else [path_leaf(f_p) for f_p in ex_run["outputfiles"]]
                    dpg.add_listbox(files, tag=UUIDs["OUTPUT_FILES"])
                    dpg.add_spacer(height=5)

                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_import_outputfiles"][LANGUAGE],
                            callback=get_files,
                            user_data=(UUIDs["OUTPUT_FILES"], ex_run, "outputfiles")
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE], callback=remove_selected, user_data=(UUIDs["OUTPUT_FILES"], ex_run, "outputfiles"))
        dpg.add_spacer(height=10)
            
        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=extract_exrun_data, user_data=(UUIDs, ex_run, var, new, ix))
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE],
                    callback=close_window,
                    user_data=window_id,
                )


def _add_variation_window(sender, app_data, user_data: tuple[dict, int]):
    parent_data = user_data[0]
    var_letter = get_variation_letter(len(parent_data["variations"]))
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE] + " " + var_letter
    UUIDs = {'{}'.format(i):dpg.generate_uuid() for i in VARIATION_KEY_LIST}
    window_id = dpg.generate_uuid()
    
    if user_data[1] == -1:
        data = get_empty_variation()
    else:
        data = parent_data["variations"][user_data[1]]

    with dpg.window(
        label=label, tag=window_id, width=750, height=700, no_close=True
    ):
        dpg.add_spacer(height=5)

        # Instruction textbox
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_inst"][LANGUAGE])
                dpg.add_input_text(multiline=True, height=150, tab_input=True, default_value=data["instructions"], tag=UUIDs["INSTRUCTIONS"])
                dpg.add_spacer(width=5)

        # Example run list box and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_ex_runs"][LANGUAGE])
                with dpg.group():
                    runs = [] if not data["example_runs"] else ["{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE], i) for i, _ in enumerate(data["example_runs"])]
                    dpg.add_listbox(runs, tag=UUIDs["EXAMPLE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_add_ex_run"][LANGUAGE],
                        callback=_add_example_run_window,
                        user_data=(data, len(data["example_runs"])+1)
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE], callback=remove_selected, user_data=(UUIDs["EXAMPLE_LISTBOX"], data, "ex_run"))
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE], callback=_add_example_run_window, user_data=(data, 1 if not data["example_runs"] else data["example_runs"].index(dpg.get_value(UUIDs["EXAMPLE_LISTBOX"]))))
    
        # Used in text box
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_spacer(height=5)
                dpg.add_text(DISPLAY_TEXTS["ui_used_in"][LANGUAGE])
                help_(DISPLAY_TEXTS["help_used_in"][LANGUAGE])
                dpg.add_input_text(tag=UUIDs["USED_IN"], default_value=", ".join(data["used_in"]))
                dpg.add_spacer(width=5)
        
        # Code files listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_codefiles"][LANGUAGE])
                files = [] if not data["codefiles"] else [path_leaf(f_p) for f_p in data["codefiles"]]
                dpg.add_listbox(files, tag=UUIDs["CODEFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_import_codefiles"][LANGUAGE], callback=get_files, user_data=(data, UUIDs["CODEFILE_LISTBOX"], "codefile")
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE], callback=remove_selected, user_data=(UUIDs["CODEFILE_LISTBOX"], data, "codefiles"))
                dpg.add_spacer(height=5)

        # Datafiles listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_datafiles"][LANGUAGE])
                files = [] if not data["datafiles"] else [path_leaf(f_p) for f_p in data["datafiles"]]
                dpg.add_listbox(files, tag=UUIDs["DATAFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_import_datafiles"][LANGUAGE],
                        callback=get_files,
                        user_data=(data, UUIDs["DATAFILE_LISTBOX"], "datafiles")
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE], callback=remove_selected, user_data=(UUIDs["DATAFILE_LISTBOX"], data, "datafiles"))
                dpg.add_spacer(height=5)

        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE], callback=extract_variation_data, user_data=(UUIDs, var_letter, parent_data, data, user_data[1]))
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE],
                    callback=close_window,
                    user_data=window_id,
                )


def _assignment_window(sender, app_data, user_data):
    """
    UI components for "Add assingment" window
    """
    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE],
    )
    if not user_data:
        var = get_empty_assignment()
    else:
        var = user_data
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
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TITLE"], default_value=var["title"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_lecture_week"][LANGUAGE] + ":")
                        dpg.add_input_int(
                            callback=None, width=150, min_value=0, min_clamped=True, tag=UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"], default_value=var["exp_lecture"]
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_assignment_no"][LANGUAGE] + ":")
                        help_(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=150, tag=UI_ITEM_TAGS["ASSIGNMENT_NO"], default_value=", ".join(var["exp_assignment_no"]))
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE] + ":"
                        )
                        help_(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE])
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TAGS"], default_value=", ".join(var["tags"]))
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE] + ":")
                        dpg.add_checkbox(
                            callback=_toggle_enabled,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
                            user_data=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                            default_value=False if not var["next, last"] else True
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
                with dpg.group():
                    dpg.add_listbox(var["variations"], tag=UI_ITEM_TAGS["VARIATION_GROUP"])
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE],
                    callback=_add_variation_window,
                    user_data=(var, -1),
                )
                dpg.add_spacer(width=5)
                dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE], user_data=(UI_ITEM_TAGS["VARIATION_GROUP"], var, "variation"), callback=remove_selected)
                dpg.add_spacer(width=5)
                dpg.add_button(label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE], callback=_add_variation_window, user_data=(var, -1 if not var["variations"] else var["variations"].index(dpg.get_value(UI_ITEM_TAGS["VARIATION_GROUP"]))))
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
