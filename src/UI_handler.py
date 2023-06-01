"""
Mímir UI Handler

Functions to handle UI
"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
import dearpygui.dearpygui as dpg
from pprint import pprint

from src.constants import (
    DISPLAY_TEXTS,
    LANGUAGE,
    UI_ITEM_TAGS,
    VARIATION_KEY_LIST,
    EXAMPLE_RUN_KEY_LIST,
    WEEK_WINDOW_KEY_LIST,
    RECENTS,
    OPEN_COURSE_PATH,
    COURSE_INFO,
)
from src.data_handler import (
    save_course_info,
    path_leaf,
    open_course,
    close_index,
    year_conversion,
    get_value_from_browse
)
from src.data_getters import (
    get_empty_variation,
    get_empty_assignment,
    get_empty_example_run,
    get_empty_week,
    get_all_indexed_assignments,
    get_header_page,
    get_number_of_docs,
    get_week_data,
    get_assignment_json,
    get_variation_index
)

from src.ui_helper import (
    help_,
    get_variation_letter,
    close_window,
    get_files,
    remove_selected,
    extract_exrun_data,
    extract_variation_data,
    toggle_enabled,
    save_assignment,
    save_week,
    swap_page,
    assignment_search_wrapper,
    clear_search_bar,
    save_select,
)
from src.popups import popup_ok, popup_create_course
from src.common import round_up

#############################################################


def _stop():
    logging.info("Stopping program.")
    close_index()
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
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_create"][LANGUAGE.get()],
                    callback=popup_create_course,
                )
                dpg.add_menu_item(
                    label=DISPLAY_TEXTS["menu_open"][LANGUAGE.get()],
                    callback=open_course,
                )
                with dpg.menu(label=DISPLAY_TEXTS["menu_open_recent"][LANGUAGE.get()]):
                    for item in RECENTS.get():
                        dpg.add_menu_item(
                            label=path_leaf(item),
                            callback=lambda s, a, item: open_course(dir=item),
                            user_data=item,
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
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_id"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_text(
                                callback=None,
                                width=400,
                                hint="No course selected",
                                tag=UI_ITEM_TAGS["COURSE_ID"],
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_name"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_text(
                                callback=None,
                                width=400,
                                tag=UI_ITEM_TAGS["COURSE_TITLE"],
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_int(
                                callback=None,
                                width=150,
                                min_value=0,
                                min_clamped=True,
                                tag=UI_ITEM_TAGS["COURSE_WEEKS"],
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_assignments_index"][LANGUAGE.get()]
                                + ":"
                            )
                            dpg.add_text(
                                str(get_number_of_docs()),
                                tag=UI_ITEM_TAGS["total_index"],
                            )
                        with dpg.table_row():
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                                callback=save_course_info,
                                user_data=None,
                            )
                dpg.add_spacer(width=50)
                dpg.add_image("mimir_logo")
            dpg.add_spacer(height=25)
        header2_label = DISPLAY_TEXTS["ui_assignment_set"][LANGUAGE.get()]
        with dpg.collapsing_header(label=header2_label):
            dpg.add_text("Under construction", indent=25)

            # dpg.add_button(label="Avaa...", callback=_openfilebrowser, user_data=files)
            dpg.add_button(label="Luo tehtäväpaperi", callback=None, user_data=None)
        header3_label = DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()]
        with dpg.collapsing_header(label=header3_label):
            dpg.add_text("Under construction", indent=25)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
                            callback=lambda s, a, u: open_new_assignment_window(),
                            tag=UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"],
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_add_week"][LANGUAGE.get()],
                            callback=lambda s, a, u: open_new_week_window(),
                        )
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_open_assignment_browse"][
                                LANGUAGE.get()
                            ],
                            callback=open_assignment_browse,
                            user_data=(True, False, None),
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_open_week_browse"][LANGUAGE.get()],
                            callback=open_week_browse,
                            user_data=(False, None),
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")

                    ###### temp buttons
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Current index (TEMP)",
                            callback=lambda s, a, u: pprint(
                                get_all_indexed_assignments()
                            ),
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label="Tehtävävalitsin",
                            callback=temp_selector_wrapper,
                            user_data=True
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label="Viikkovalitsin",
                            callback=temp_selector_wrapper,
                            user_data=False
                        )


def temp_selector_wrapper(s, a, u:bool):
    if u:
        selected = []
        open_assignment_browse(None, None, (True, True, selected))
    else:
        selected = []
        open_week_browse(None, None, (True, selected))


def _add_example_run_window(sender, app_data, user_data: tuple[dict, int, int | str, bool]):
    """
    Adds an example run input window
    """
    var = user_data[0]
    ix = user_data[1]
    var_listbox = user_data[2]
    new = False
    print(var)
    try:
        ex_run = var["example_runs"][ix]
        print("here")
    except IndexError:
        ex_run = get_empty_example_run()
        new = True

    print(ex_run)
    select = True
    if user_data[3]:
        select = False

    UUIDs = {"{}".format(i): dpg.generate_uuid() for i in EXAMPLE_RUN_KEY_LIST}
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
                    multiline=True, height=150, tab_input=True, tag=UUIDs["INPUTS"], enabled=select, default_value="\n".join([str(item) for item in ex_run["inputs"]]),
                )
                dpg.add_spacer(height=5)

                # Command line inputs
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE.get()])
                dpg.add_input_text(tag=UUIDs["CMD_INPUTS"], enabled=select, default_value=", ".join([str(item) for item in ex_run["cmd_inputs"]]))

                # Generate ex run checkbox
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE.get()])
                    help_(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE.get()])
                    dpg.add_checkbox(
                        tag=UUIDs["GEN_EX"],
                        callback=toggle_enabled,
                        user_data=UUIDs["OUTPUT"],
                        enabled=select,
                        default_value=ex_run["generate"]
                    )

                # Output text
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE.get()])
                dpg.add_input_text(tag=UUIDs["OUTPUT"], multiline=True, height=150, enabled=select, default_value=ex_run["output"])
                dpg.add_spacer(height=5)

                # Output files
                dpg.add_text(DISPLAY_TEXTS["ui_output_filename"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_output_filename"][LANGUAGE.get()])
                with dpg.group():
                    files = (
                        []
                        if not ex_run["outputfiles"]
                        else [path_leaf(f_p) for f_p in ex_run["outputfiles"]]
                    )
                    dpg.add_listbox(files, tag=UUIDs["OUTPUT_FILES"])
                    dpg.add_spacer(height=5)

                    if select:
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_import_outputfiles"][
                                    LANGUAGE.get()
                                ],
                                callback=get_files,
                                user_data=(ex_run, UUIDs["OUTPUT_FILES"], "outputfiles"),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()],
                                callback=remove_selected,
                                user_data=(UUIDs["OUTPUT_FILES"], ex_run, "outputfiles"),
                            )
        dpg.add_spacer(height=10)

        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            if select:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                        callback=extract_exrun_data,
                        user_data=(UUIDs, ex_run, var, new, ix, var_listbox),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UUIDs["WINDOW_ID"],
                    )
            else:
                dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UUIDs["WINDOW_ID"],
                    )


def _add_variation_window(sender, app_data, user_data: tuple[dict, int, bool]):
    parent_data = user_data[0]

    if user_data[1] == -1:
        data = get_empty_variation()
    elif user_data[1] == -2:
        return
    else:
        data = parent_data["variations"][user_data[1]]

    select = True
    if user_data[2]:
        select = False

    var_letter = get_variation_letter(len(parent_data["variations"]) + 1)
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()] + " " + var_letter
    UUIDs = {"{}".format(i): dpg.generate_uuid() for i in VARIATION_KEY_LIST}

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
                dpg.add_input_text(
                    multiline=True,
                    height=150,
                    tab_input=True,
                    default_value=data["instructions"],
                    tag=UUIDs["INSTRUCTIONS"],
                    enabled=select
                )
                dpg.add_spacer(width=5)

        # Example run list box and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_ex_runs"][LANGUAGE.get()])
                with dpg.group():
                    runs = (
                        []
                        if not data["example_runs"]
                        else [
                            "{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE.get()], i)
                            for i, _ in enumerate(data["example_runs"], start=1)
                        ]
                    )
                    dpg.add_listbox(runs, tag=UUIDs["EXAMPLE_LISTBOX"])
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    if select:
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_add_ex_run"][LANGUAGE.get()],
                            callback=_add_example_run_window,
                            user_data=(
                                data,
                                len(data["example_runs"]) + 1,
                                UUIDs["EXAMPLE_LISTBOX"],
                            ),
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()],
                            callback=remove_selected,
                            user_data=(UUIDs["EXAMPLE_LISTBOX"], data, "ex_run"),
                        )
                        dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()]
                        if select
                        else DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                        callback=_add_example_run_window,
                        user_data=(
                            data,
                            1
                            if not data["example_runs"]
                            else int(dpg.get_value(UUIDs["EXAMPLE_LISTBOX"]).split(" ")[1])-1,
                            UUIDs["EXAMPLE_LISTBOX"],
                            user_data[2]
                        ),
                    )

        # Used in text box
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_spacer(height=5)
                dpg.add_text(DISPLAY_TEXTS["ui_used_in"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_used_in"][LANGUAGE.get()])
                dpg.add_input_text(
                    tag=UUIDs["USED_IN"],
                    default_value=", ".join(year_conversion(data["used_in"], False)),
                    enabled=select
                )
                dpg.add_spacer(width=5)

        # Code files listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_codefiles"][LANGUAGE.get()])
                files = (
                    []
                    if not data["codefiles"]
                    else [path_leaf(f_p) for f_p in data["codefiles"]]
                )
                dpg.add_listbox(files, tag=UUIDs["CODEFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                if select:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_import_codefiles"][LANGUAGE.get()],
                            callback=get_files,
                            user_data=(data, UUIDs["CODEFILE_LISTBOX"], "codefile"),
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()],
                            callback=remove_selected,
                            user_data=(UUIDs["CODEFILE_LISTBOX"], data, "codefiles"),
                        )
                    dpg.add_spacer(height=5)

        # Datafiles listbox and its buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                dpg.add_text(DISPLAY_TEXTS["ui_datafiles"][LANGUAGE.get()])
                files = (
                    []
                    if not data["datafiles"]
                    else [path_leaf(f_p) for f_p in data["datafiles"]]
                )
                dpg.add_listbox(files, tag=UUIDs["DATAFILE_LISTBOX"])
                dpg.add_spacer(height=5)

                if select:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_import_datafiles"][LANGUAGE.get()],
                            callback=get_files,
                            user_data=(data, UUIDs["DATAFILE_LISTBOX"], "datafiles"),
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()],
                            callback=remove_selected,
                            user_data=(UUIDs["DATAFILE_LISTBOX"], data, "datafiles"),
                        )
                    dpg.add_spacer(height=5)

        # Window buttons
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            if select:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                        callback=extract_variation_data,
                        user_data=(UUIDs, var_letter, parent_data, data, user_data[1]),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UUIDs["WINDOW_ID"],
                    )
            else:
                dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UUIDs["WINDOW_ID"],
                    )


def _assignment_window(var_data=None, select=False):
    """
    UI components for "Add assingment" window
    """
    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()],
        DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
    )
    print(var_data)
    if not var_data:
        var = get_empty_assignment()
        new = True
    else:
        var = var_data
        new = False

    enable = True
    if select:
        enable = False
    
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

                    # Assignment title
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_title"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_input_text(
                            callback=None,
                            width=430,
                            tag=UI_ITEM_TAGS["ASSIGNMENT_TITLE"],
                            default_value=var["title"],
                            enabled=enable
                        )

                    # Lecture week
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_lecture_week"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_input_int(
                            callback=None,
                            width=150,
                            min_value=0,
                            min_clamped=True,
                            tag=UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"],
                            default_value=var["exp_lecture"],
                            enabled=enable
                        )

                    # Assignment number
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_no"][LANGUAGE.get()] + ":"
                        )
                        help_(DISPLAY_TEXTS["help_assignment_no"][LANGUAGE.get()])
                        dpg.add_input_text(
                            callback=None,
                            width=150,
                            tag=UI_ITEM_TAGS["ASSIGNMENT_NO"],
                            default_value=", ".join([str(item) for item in var["exp_assignment_no"]]),
                            enabled=enable
                        )

                    # Assignment tags
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_tags"][LANGUAGE.get()] + ":"
                        )
                        help_(DISPLAY_TEXTS["help_assignment_tags"][LANGUAGE.get()])
                        dpg.add_input_text(
                            callback=None,
                            width=430,
                            tag=UI_ITEM_TAGS["ASSIGNMENT_TAGS"],
                            default_value=", ".join(var["tags"]),
                            enabled=enable
                        )

                    # Previous part checkbox
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_checkbox(
                            callback=toggle_enabled,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
                            user_data=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                            default_value=False if not var["next, last"] else True,
                            enabled=enable
                        )

                    # Previous part input
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE.get()])
                        dpg.add_combo(
                            # TODO Previous part combobox
                            ("Testi1", "Testi2", "Testi3"),
                            default_value="",
                            enabled=enable,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
                        )

                    # Code language
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            ("Python", "C"), tag=UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"], enabled=enable
                        )

                    # Instruction language
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_inst_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            # TODO do dynamically
                            (
                                DISPLAY_TEXTS["language_FI"][LANGUAGE.get()],
                                DISPLAY_TEXTS["language_ENG"][LANGUAGE.get()],
                            ),
                            tag=UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"],
                            enabled=enable
                        )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)

                # Variation listbox
                with dpg.group():
                    _vars = (
                        []
                        if not var["variations"]
                        else [
                            "{} {}".format(
                                DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()],
                                item["variation_id"],
                            )
                            for item in var["variations"]
                        ]
                    )
                    dpg.add_listbox(_vars, tag=UI_ITEM_TAGS["VARIATION_GROUP"])
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Listbox buttons
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                if not select:
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE.get()],
                        callback=_add_variation_window,
                        user_data=(var, -1),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_remove_selected"][LANGUAGE.get()],
                        user_data=(UI_ITEM_TAGS["VARIATION_GROUP"], var, "variation"),
                        callback=remove_selected,
                    )
                    dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()]
                        if not select
                        else DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                    callback=_add_variation_window,
                    user_data=(
                        var,
                        -2
                        if not var["variations"]
                        else get_variation_index(var["variations"], dpg.get_value(UI_ITEM_TAGS["VARIATION_GROUP"]).split(" ")[1]),
                        select
                        ),
                    ),
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Window buttons
            if not select:
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                        callback=save_assignment,
                        user_data=(var, new),
                    )
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
                    )
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_delete"][LANGUAGE.get()], callback=None
                    )
            else:
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                    callback=lambda s, a, u: close_window(u),
                    user_data=UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
                )


def open_new_assignment_window(parent=None, select=False):
    """
    A function to check whether the 'Add assingment' window is already open.
    If it is not, open it.

    Params:
    parent: Assignment data to edit
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                _assignment_window(var_data=parent, select=select)
            else:
                popup_ok(DISPLAY_TEXTS["popup_courseinfo_missing"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()])


def _add_week_window(parent=None, index=None, select=False):
    """
    UI components for "Add week" window.
    """

    if not select:
        label = "Mímir - {} - {}".format(
            DISPLAY_TEXTS["ui_week_management"][LANGUAGE.get()],
            DISPLAY_TEXTS["ui_add_week"][LANGUAGE.get()],
        )
    else:
        label = "Mímir - {} - {}".format(
            DISPLAY_TEXTS["ui_week_management"][LANGUAGE.get()],
            DISPLAY_TEXTS["ui_show_week"][LANGUAGE.get()],
        )
    if parent:
        week = parent["lectures"][index]
        new = False
    else:
        week = get_empty_week()
        new = True
    multiline_width = 430
    enable = True
    if select:
        enable = False

    UUIDs = {"{}".format(i): dpg.generate_uuid() for i in WEEK_WINDOW_KEY_LIST}
    with dpg.window(
        label=label, width=750, height=700, tag=UI_ITEM_TAGS["ADD_WEEK"], no_close=True
    ):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                # Week title
                dpg.add_text(DISPLAY_TEXTS["ui_week_title"][LANGUAGE.get()] + ":")
                help_(DISPLAY_TEXTS["help_week_title"][LANGUAGE.get()])
                dpg.add_input_text(
                    width=multiline_width,
                    tag=UUIDs["TITLE"],
                    default_value=week["title"],
                    enabled=enable,
                )
                dpg.add_spacer(height=5)

                with dpg.table(header_row=False):
                    dpg.add_table_column(width_fixed=True, init_width_or_weight=200)
                    dpg.add_table_column(width_fixed=True, init_width_or_weight=250)
                    # Week number
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_week_no"][LANGUAGE.get()])
                        dpg.add_input_int(
                            width=150,
                            min_value=0,
                            min_clamped=True,
                            tag=UUIDs["LECTURE_NO"],
                            default_value=week["lecture_no"],
                            enabled=enable,
                        )
                    # dpg.add_spacer(height=5)

                    # Assignment count
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_no_assignments"][LANGUAGE.get()])
                        dpg.add_input_int(
                            width=150,
                            min_value=1,
                            min_clamped=True,
                            tag=UUIDs["A_COUNT"],
                            default_value=week["assignment_count"],
                            enabled=enable,
                        )
                    # dpg.add_spacer(height=5)

                # Week topics
                dpg.add_text(DISPLAY_TEXTS["ui_week_topics"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_week_topics"][LANGUAGE.get()])
                dpg.add_input_text(
                    width=multiline_width,
                    tag=UUIDs["TOPICS"],
                    default_value="\n".join(week["topics"]),
                    multiline=True,
                    enabled=enable,
                )
                dpg.add_spacer(height=5)

                # Week instructions
                dpg.add_text(DISPLAY_TEXTS["ui_inst"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_week_inst"][LANGUAGE.get()])
                dpg.add_input_text(
                    width=multiline_width,
                    tag=UUIDs["INSTRUCTIONS"],
                    default_value=week["instructions"],
                    multiline=True,
                    enabled=enable,
                )
                dpg.add_spacer(height=5)

                # Week tags
                dpg.add_text(DISPLAY_TEXTS["ui_week_tags"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_week_tags"][LANGUAGE.get()])
                dpg.add_input_text(
                    width=multiline_width,
                    tag=UUIDs["TAGS"],
                    default_value=", ".join(week["tags"]),
                    enabled=enable,
                )

                # Window buttons
                dpg.add_spacer(height=5)
                dpg.add_separator()
                dpg.add_spacer(height=5)
                if select:
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=UI_ITEM_TAGS["ADD_WEEK"],
                        width=90,
                    )
                else:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                            callback=save_week,
                            user_data=(week, new, UUIDs),
                            width=90,
                        )
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                            callback=lambda s, a, u: close_window(u),
                            user_data=UI_ITEM_TAGS["ADD_WEEK"],
                            width=90,
                        )


def open_new_week_window(parent=None, index=None, select=False):
    """
    A function to check if 'Add week' window is already open.
    If it is not, open it.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["ADD_WEEK"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                _add_week_window(parent=parent, index=index, select=select)
            else:
                popup_ok(DISPLAY_TEXTS["popup_courseinfo_missing"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()])


def assignment_browse_window(search=True, select=False, select_save=None):
    """
    Create a window for listing assignments.

    Params:
    search: A bool whether to include the search bar
    select: A bool whether to include a 'Select' button in addition to 'Close'
    """

    label = "Mímir - {}".format(DISPLAY_TEXTS["ui_assignment_browse"][LANGUAGE.get()])
    if not search:
        height = 695
    else:
        height = 710

    with dpg.window(
        label=label,
        width=1400,
        height=height,
        tag=UI_ITEM_TAGS["LIST_WINDOW"],
        no_close=True,
        no_collapse=True,
        no_resize=True,
    ):
        pagenum = [1]
        dpg.add_spacer(height=25)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():

                # Search bar
                if search:
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(
                            width=1040,
                            hint=DISPLAY_TEXTS["ui_search_hint"][LANGUAGE.get()],
                            tag=UI_ITEM_TAGS["SEARCH_BAR"],
                        )
                        dpg.add_spacer(width=6)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_search_button"][LANGUAGE.get()],
                            callback=assignment_search_wrapper,
                            width=75,
                            user_data=pagenum,
                        )
                        dpg.add_spacer(width=6)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_clear_search"][LANGUAGE.get()],
                            callback=clear_search_bar,
                            width=140,
                            user_data=pagenum,
                        )

                # Listbox header
                dpg.add_spacer(height=10)
                dpg.add_text(
                    DISPLAY_TEXTS["ui_assignments_in_index"][LANGUAGE.get()] + ":"
                )

                # Assignment listbox
                dpg.add_spacer(height=5)
                headers = get_header_page(pagenum[0], get_all_indexed_assignments())
                dpg.add_listbox(
                    headers, tag=UI_ITEM_TAGS["LISTBOX"], width=1300, num_items=15
                )
                dpg.add_spacer(height=5)

                # Page browse buttons + Assignment show button
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()]
                        if not select
                        else DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                        width=150,
                        callback=_assignment_edit_callback,
                        user_data=select
                    )
                    dpg.add_spacer(width=340)
                    dpg.add_button(
                        label="<- " + DISPLAY_TEXTS["ui_previous"][LANGUAGE.get()],
                        width=120,
                        enabled=True,
                        callback=swap_page,
                        user_data=(pagenum, get_all_indexed_assignments(), "-", True),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_text(
                        str(pagenum[0])
                        + "/"
                        + str(
                            1
                            if get_number_of_docs() == 0
                            else round_up(get_number_of_docs() / 15)
                        ),
                        tag=UI_ITEM_TAGS["PAGENUM"],
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_next"][LANGUAGE.get()] + " ->",
                        width=120,
                        enabled=True,
                        callback=swap_page,
                        user_data=(pagenum, get_all_indexed_assignments(), "+", True),
                    )

                dpg.add_spacer(height=10)
                dpg.add_separator()
                dpg.add_spacer(height=5)

                # Window buttons
                if select:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_select"][LANGUAGE.get()],
                            width=80,
                            callback=save_select,
                            user_data=select_save,
                        )
                        dpg.add_spacer(width=6)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                            width=80,
                            callback=lambda s, a, u: close_window(u),
                            user_data=UI_ITEM_TAGS["LIST_WINDOW"],
                        )
                else:
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        width=90,
                        callback=lambda s, a, u: close_window(u),
                        user_data=UI_ITEM_TAGS["LIST_WINDOW"],
                    )


def open_assignment_browse(s, a, u: tuple[bool, bool, list]):
    """
    Shorthand to check and open the assingment browse window.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["LIST_WINDOW"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                assignment_browse_window(search=u[0], select=u[1], select_save=u[2])
            else:
                popup_ok(DISPLAY_TEXTS["popup_courseinfo_missing"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()])


def week_browse_window(select=False, select_save=None):
    """
    Window to browse saved week data
    """

    label = "Mímir - {}".format(DISPLAY_TEXTS["ui_week_management"][LANGUAGE.get()])

    with dpg.window(
        label=label,
        width=1400,
        height=695,
        tag=UI_ITEM_TAGS["LIST_WINDOW"],
        no_close=True,
        no_collapse=True,
        no_resize=True,
    ):
        pagenum = [1]
        dpg.add_spacer(height=10)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():

                # Listbox header
                dpg.add_spacer(height=10)
                dpg.add_text(DISPLAY_TEXTS["ui_weeks_saved"][LANGUAGE.get()] + ":")

                # Week listbox
                dpg.add_spacer(height=5)
                headers = get_header_page(
                    pagenum[0], get_week_data()["lectures"], week=True
                )
                dpg.add_listbox(
                    headers, tag=UI_ITEM_TAGS["LISTBOX"], width=1300, num_items=15
                )
                dpg.add_spacer(height=5)

                # Page browse buttons + Week show button
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_show_edit"][LANGUAGE.get()]
                        if not select
                        else DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                        width=150,
                        callback=week_show_callback,
                        user_data=select,
                    )
                    dpg.add_spacer(width=340)
                    dpg.add_button(
                        label="<- " + DISPLAY_TEXTS["ui_previous"][LANGUAGE.get()],
                        width=120,
                        enabled=True,
                        callback=swap_page,
                        user_data=(pagenum, get_week_data()["lectures"], "-", True),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_text(
                        str(pagenum[0])
                        + "/"
                        + str(
                            1
                            if len(get_week_data()["lectures"]) == 0
                            else round_up(len(get_week_data()["lectures"]) / 15)
                        ),
                        tag=UI_ITEM_TAGS["PAGENUM"],
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_next"][LANGUAGE.get()] + " ->",
                        width=120,
                        enabled=True,
                        callback=swap_page,
                        user_data=(pagenum, get_week_data()["lectures"], "+", True),
                    )

                dpg.add_spacer(height=10)
                dpg.add_separator()
                dpg.add_spacer(height=5)

                # Window buttons

                if select:
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_select"][LANGUAGE.get()],
                            width=90,
                            callback=save_select,
                            user_data=select_save,
                        )
                        dpg.add_spacer(width=6)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                            width=90,
                            callback=lambda s, a, u: close_window(u),
                            user_data=UI_ITEM_TAGS["LIST_WINDOW"],
                        )
                else:
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        width=90,
                        callback=lambda s, a, u: close_window(u),
                        user_data=UI_ITEM_TAGS["LIST_WINDOW"],
                    )


def open_week_browse(s, a, u: tuple[bool, list]):
    """
    Shorthand to check and open the week browse window.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["LIST_WINDOW"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                week_browse_window(select=u[0], select_save=u[1])
            else:
                popup_ok(DISPLAY_TEXTS["popup_courseinfo_missing"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()])


def week_show_callback(s, a, u: bool):
    """
    Callback to get the right week and pass it to week edit window.
    """

    value = dpg.get_value(UI_ITEM_TAGS["LISTBOX"])
    if not value:
        return
    lecture = int(value.split(" - ")[0])

    weeks = get_week_data()["lectures"]
    for i, week in enumerate(weeks):
        if week["lecture_no"] == lecture:
            ind = i
            break

    open_new_week_window(parent=get_week_data(), index=ind, select=u)


def _assignment_edit_callback(s, a, u:bool):

    value = get_value_from_browse()
    _json = get_assignment_json(value["json_path"])
    open_new_assignment_window(parent=_json, select=u)