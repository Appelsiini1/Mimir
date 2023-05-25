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

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS, VARIATION_KEY_LIST, EXAMPLE_RUN_KEY_LIST, RECENTS, OPEN_COURSE_PATH, COURSE_INFO
from src.data_handler import save_course_info, save_assignment, get_empty_variation, path_leaf, get_empty_assignment, get_empty_example_run, open_course
from src.set_generator import temp_creator
from src.ui_helper import help_, get_variation_letter, close_window, get_files, remove_selected, extract_exrun_data, extract_variation_data, toggle_enabled
from src.popups import popup_ok, popup_create_course

#############################################################

def _stop():
    logging.info("Stopping program.")
    dpg.stop_dearpygui()
    dpg.destroy_context()


def main_window():
    """
    Create main window
    """
    # TODO Move label to a normal text bc primary window hides title bar
    label = "Mímir - " + DISPLAY_TEXTS["ui_main"][LANGUAGE.get()]
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
            with dpg.menu(label=DISPLAY_TEXTS["menu_file"][LANGUAGE.get()]):
                # TODO Add callbacks
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_create"][LANGUAGE.get()], callback=popup_create_course
                )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_open"][LANGUAGE.get()], callback=open_course
                )
                with dpg.menu(label=DISPLAY_TEXTS["menu_open_recent"][LANGUAGE.get()]):
                    for item in RECENTS.get():
                        dpg.add_menu_item(
                            label=path_leaf(item), callback=lambda s, a, item: open_course(dir=item), user_data=item
                        )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_update"][LANGUAGE.get()], callback=None
                )

            dpg.add_menu_item(
                label=DISPLAY_TEXTS["menu_exit"][LANGUAGE.get()], callback=_stop
            )
        header1_label = DISPLAY_TEXTS["ui_info"][LANGUAGE.get()]
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
                            dpg.add_text(DISPLAY_TEXTS["ui_course_id"][LANGUAGE.get()] + ":")
                            dpg.add_input_text(
                                callback=None, width=400, hint="No course selected", tag=UI_ITEM_TAGS["COURSE_ID"],
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_name"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_text(callback=None, width=400, tag=UI_ITEM_TAGS["COURSE_TITLE"])
                        with dpg.table_row():
                            dpg.add_text(DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE.get()] + ":")
                            dpg.add_input_int(
                                callback=None, width=150, min_value=0, min_clamped=True, tag=UI_ITEM_TAGS["COURSE_WEEKS"],
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_assignments_index"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_text("0", tag=UI_ITEM_TAGS["total_index"])
                        with dpg.table_row():
                            dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()], callback=save_course_info, user_data=None)
                dpg.add_spacer(width=50)
                dpg.add_image("mimir_logo")
            dpg.add_spacer(height=25)
        header2_label = DISPLAY_TEXTS["ui_assignment_set"][LANGUAGE.get()]
        with dpg.collapsing_header(label=header2_label):
            dpg.add_text("Under construction", indent=25)

            #dpg.add_button(label="Avaa...", callback=_openfilebrowser, user_data=files)
            dpg.add_button(label="Luo tehtäväpaperi", callback=temp_creator, user_data=None)
        header3_label = DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()]
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
                                label=DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
                                callback=open_new_assignment_window,
                                tag=UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"],
                                user_data=False
                            )



def _add_example_run_window(
    sender, app_data, user_data: tuple[dict, int, int|str]
):
    """
    Adds an example run input window
    """
    var = user_data[0]
    ix = user_data[1]
    var_listbox = user_data[2]
    new = False
    try:
        ex_run = var["example_runs"][ix]
    except IndexError:
        ex_run = get_empty_example_run()
        new = True
    
    UUIDs = {'{}'.format(i):dpg.generate_uuid() for i in EXAMPLE_RUN_KEY_LIST}
    label = DISPLAY_TEXTS["ex_run"][LANGUAGE.get()] + " " + str(user_data[1])
    with dpg.window(
        label=label, tag=UUIDs["WINDOW_ID"], width=750, height=700, no_close=True
    ):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():

                # Inputs
                dpg.add_text(DISPLAY_TEXTS["ex_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_inputs"][LANGUAGE.get()])
                dpg.add_input_text(
                    multiline=True, height=150, tab_input=True, tag=UUIDs["INPUTS"]
                )
                dpg.add_spacer(height=5)

                # Command line inputs
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE.get()])
                dpg.add_input_text(tag=UUIDs["CMD_INPUTS"])
                
                # Generate ex run checkbox
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE.get()])
                    help_(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE.get()])
                    dpg.add_checkbox(
                        tag=UUIDs["GEN_EX"],
                        callback=toggle_enabled,
                        user_data=UUIDs["OUTPUT"],
                    )
                
                # Output text
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE.get()])
                dpg.add_input_text(tag=UUIDs["OUTPUT"], multiline=True, height=150)
                dpg.add_spacer(height=5)
                
                # Output files
                dpg.add_text(DISPLAY_TEXTS["ui_output_filename"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_output_filename"][LANGUAGE.get()])
                with dpg.group():
                    files = [] if not ex_run["outputfiles"] else [path_leaf(f_p) for f_p in ex_run["outputfiles"]]
                    dpg.add_listbox(files, tag=UUIDs["OUTPUT_FILES"])
                    dpg.add_spacer(height=5)

                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_import_outputfiles"][LANGUAGE.get()],
                            callback=get_files,
                            user_data=(ex_run, UUIDs["OUTPUT_FILES"], "outputfiles")
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()], callback=remove_selected, user_data=(UUIDs["OUTPUT_FILES"], ex_run, "outputfiles"))
        dpg.add_spacer(height=10)
            
        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()], callback=extract_exrun_data, user_data=(UUIDs, ex_run, var, new, ix, var_listbox))
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                    callback=lambda s, a, u:close_window(u),
                    user_data=UUIDs["WINDOW_ID"],
                )


def _add_variation_window(sender, app_data, user_data: tuple[dict, int]):
    parent_data = user_data[0]
    var_letter = get_variation_letter(len(parent_data["variations"]))
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()] + " " + var_letter
    UUIDs = {'{}'.format(i):dpg.generate_uuid() for i in VARIATION_KEY_LIST}
    
    if user_data[1] == -1:
        data = get_empty_variation()
    else:
        data = parent_data["variations"][user_data[1]]

    with dpg.window(
        label=label, tag=UUIDs["WINDOW_ID"], width=750, height=700, no_close=True
    ):
        dpg.add_spacer(height=5)

        # Instruction textbox
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_inst"][LANGUAGE.get()])
                dpg.add_input_text(multiline=True, height=150, tab_input=True, default_value=data["instructions"], tag=UUIDs["INSTRUCTIONS"])
                dpg.add_spacer(width=5)

        # Example run list box and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_ex_runs"][LANGUAGE.get()])
                with dpg.group():
                    runs = [] if not data["example_runs"] else ["{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE.get()], i) for i, _ in enumerate(data["example_runs"])]
                    dpg.add_listbox(runs, tag=UUIDs["EXAMPLE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_add_ex_run"][LANGUAGE.get()],
                        callback=_add_example_run_window,
                        user_data=(data, len(data["example_runs"])+1, UUIDs["EXAMPLE_LISTBOX"])
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()], callback=remove_selected, user_data=(UUIDs["EXAMPLE_LISTBOX"], data, "ex_run"))
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()], callback=_add_example_run_window, user_data=(data, 1 if not data["example_runs"] else data["example_runs"].index(dpg.get_value(UUIDs["EXAMPLE_LISTBOX"]))))
    
        # Used in text box
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_spacer(height=5)
                dpg.add_text(DISPLAY_TEXTS["ui_used_in"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_used_in"][LANGUAGE.get()])
                dpg.add_input_text(tag=UUIDs["USED_IN"], default_value=", ".join(data["used_in"]))
                dpg.add_spacer(width=5)
        
        # Code files listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_codefiles"][LANGUAGE.get()])
                files = [] if not data["codefiles"] else [path_leaf(f_p) for f_p in data["codefiles"]]
                dpg.add_listbox(files, tag=UUIDs["CODEFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_import_codefiles"][LANGUAGE.get()], callback=get_files, user_data=(data, UUIDs["CODEFILE_LISTBOX"], "codefile")
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()], callback=remove_selected, user_data=(UUIDs["CODEFILE_LISTBOX"], data, "codefiles"))
                dpg.add_spacer(height=5)

        # Datafiles listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_datafiles"][LANGUAGE.get()])
                files = [] if not data["datafiles"] else [path_leaf(f_p) for f_p in data["datafiles"]]
                dpg.add_listbox(files, tag=UUIDs["DATAFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_import_datafiles"][LANGUAGE.get()],
                        callback=get_files,
                        user_data=(data, UUIDs["DATAFILE_LISTBOX"], "datafiles")
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()], callback=remove_selected, user_data=(UUIDs["DATAFILE_LISTBOX"], data, "datafiles"))
                dpg.add_spacer(height=5)

        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()], callback=extract_variation_data, user_data=(UUIDs, var_letter, parent_data, data, user_data[1]))
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                    callback=lambda s, a, u:close_window(u),
                    user_data=UUIDs["WINDOW_ID"],
                )


def _assignment_window(sender, app_data, user_data):
    """
    UI components for "Add assingment" window
    """
    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
    )
    if not user_data:
        var = get_empty_assignment()
        new = True
    else:
        var = user_data
        new = False
    with dpg.window(
        label=label,
        width=750,
        height=700,
        tag=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
        no_close=True,
    ):
        header1_label = DISPLAY_TEXTS["ui_general"][LANGUAGE.get()]
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
                            DISPLAY_TEXTS["ui_assignment_title"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TITLE"], default_value=var["title"])
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_lecture_week"][LANGUAGE.get()] + ":")
                        dpg.add_input_int(
                            callback=None, width=150, min_value=0, min_clamped=True, tag=UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"], default_value=var["exp_lecture"]
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_assignment_no"][LANGUAGE.get()] + ":")
                        help_(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE.get()])
                        dpg.add_input_text(callback=None, width=150, tag=UI_ITEM_TAGS["ASSIGNMENT_NO"], default_value=", ".join(var["exp_assignment_no"]))
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE.get()] + ":"
                        )
                        help_(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE.get()])
                        dpg.add_input_text(callback=None, width=430, tag=UI_ITEM_TAGS["ASSIGNMENT_TAGS"], default_value=", ".join(var["tags"]))
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE.get()] + ":")
                        dpg.add_checkbox(
                            callback=toggle_enabled,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
                            user_data=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                            default_value=False if not var["next, last"] else True
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE.get()])
                        dpg.add_combo(
                            # TODO Previous part combobox
                            ("Testi1", "Testi2", "Testi3"),
                            default_value="",
                            enabled=False,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            ("Python", "C"), tag=UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"]
                        )
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_inst_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            #TODO do dynamically
                            (DISPLAY_TEXTS['language_FI'][LANGUAGE.get()], DISPLAY_TEXTS['language_ENG'][LANGUAGE.get()]),
                            tag=UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"],
                        )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    _vars = [] if not var["variations"] else ["{} {}".format(DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()], item["variation_id"]) for item in var["variations"]]
                    dpg.add_listbox(_vars, tag=UI_ITEM_TAGS["VARIATION_GROUP"])
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE.get()],
                    callback=_add_variation_window,
                    user_data=(var, -1),
                )
                dpg.add_spacer(width=5)
                dpg.add_button(label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()], user_data=(UI_ITEM_TAGS["VARIATION_GROUP"], var, "variation"), callback=remove_selected)
                dpg.add_spacer(width=5)
                dpg.add_button(label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()], callback=_add_variation_window, user_data=(var, -1 if not var["variations"] else var["variations"].index(dpg.get_value(UI_ITEM_TAGS["VARIATION_GROUP"]))))
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()], callback=save_assignment, user_data=(var, new))
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                    callback=lambda s, a, u:close_window(u),
                    user_data=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
                )
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_delete"][LANGUAGE.get()], callback=None
                )

def open_new_assignment_window():
    """
    A function to check whether the 'Add assingment' window is already open.
    If it is not, open it.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                _assignment_window(None, None, None)
            else:
                popup_ok(DISPLAY_TEXTS["popup_courseinfo_missing"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()])
