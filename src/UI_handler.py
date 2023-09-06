"""
Mímir UI Handler

Functions to handle UI
"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string, expression-not-assigned
import logging
from os.path import join
import dearpygui.dearpygui as dpg

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
    get_value_from_browse,
    del_prev,
    gen_result_headers,
    del_result,
    move_down,
    move_up,
    del_assignment_files,
    del_assignment_from_index,
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
    get_variation_index,
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
    save_result_popup,
)
from src.popups import popup_ok, popup_confirmation
from src.popups2 import popup_create_course
from src.common import round_up
from src.set_generator import generate_one_set, format_set, generate_full_set
from src.tex_generator import tex_gen
from pprint import pprint

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

    label = "Mímir - " + DISPLAY_TEXTS["ui_main"][LANGUAGE.get()]
    with dpg.window(
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
            with dpg.menu(label=DISPLAY_TEXTS["ui_menu_language"][LANGUAGE.get()]):
                for key in LANGUAGE.get_all():
                    dpg.add_menu_item(
                        label=DISPLAY_TEXTS["languages"][key],
                        user_data=key,
                        callback=reopen_main,
                    )

            dpg.add_menu_item(
                label=DISPLAY_TEXTS["menu_exit"][LANGUAGE.get()], callback=_stop
            )

        dpg.add_text(label)
        # Info header
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
                                hint=DISPLAY_TEXTS["popup_nocourse"][LANGUAGE.get()],
                                tag=UI_ITEM_TAGS["COURSE_ID"],
                                default_value=COURSE_INFO["course_id"]
                                if COURSE_INFO["course_id"] is not None
                                else "",
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_name"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_text(
                                callback=None,
                                width=400,
                                tag=UI_ITEM_TAGS["COURSE_TITLE"],
                                default_value=COURSE_INFO["course_title"]
                                if COURSE_INFO["course_title"] is not None
                                else "",
                            )
                        with dpg.table_row():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_input_int(
                                callback=None,
                                width=150,
                                min_value=1,
                                min_clamped=True,
                                tag=UI_ITEM_TAGS["COURSE_WEEKS"],
                                default_value=COURSE_INFO["course_weeks"],
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
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_course_levels"][LANGUAGE.get()] + ":"
                            )
                            help_(DISPLAY_TEXTS["help_course_levels"][LANGUAGE.get()])
                            dpg.add_input_text(
                                width=400,
                                tag=UI_ITEM_TAGS["COURSE_LEVELS"],
                                default_value=COURSE_INFO["course_levels"]
                                if COURSE_INFO["course_levels"] is not None
                                else "",
                                multiline=True,
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

        # Assignment set creation header
        header2_label = DISPLAY_TEXTS["ui_assignment_set"][LANGUAGE.get()]
        with dpg.collapsing_header(label=header2_label):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_create_new_set"][LANGUAGE.get()])
                    dpg.add_spacer(height=5)
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=15)

                        with dpg.group():
                            dpg.add_text(
                                DISPLAY_TEXTS["ui_one_week"][LANGUAGE.get()] + ":"
                            )
                            with dpg.group(horizontal=True):
                                dpg.add_text(
                                    DISPLAY_TEXTS["ui_week"][LANGUAGE.get()] + ":"
                                )
                                week_input_tag = dpg.generate_uuid()
                                dpg.add_input_int(
                                    callback=None,
                                    width=150,
                                    min_value=1,
                                    min_clamped=True,
                                    tag=week_input_tag,
                                )
                            with dpg.group(horizontal=True):
                                dpg.add_text(
                                    DISPLAY_TEXTS["ui_excl_exp"][LANGUAGE.get()]
                                )
                                checkbox_tag = dpg.generate_uuid()
                                dpg.add_checkbox(tag=checkbox_tag)
                            dpg.add_spacer(height=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_create"][LANGUAGE.get()]
                                + "...",
                                callback=create_one_set_callback,
                                user_data=(
                                    week_input_tag,
                                    checkbox_tag,
                                ),
                            )
                            dpg.bind_item_theme(
                                dpg.last_item(), "alternate_button_theme"
                            )

                            dpg.add_spacer(height=10)
                            dpg.add_separator()
                            dpg.add_spacer(height=10)

                            dpg.add_text(
                                DISPLAY_TEXTS["ui_full_course"][LANGUAGE.get()] + ":"
                            )
                            dpg.add_spacer(height=5)
                            with dpg.group(horizontal=True):
                                dpg.add_text(
                                    DISPLAY_TEXTS["ui_excl_exp"][LANGUAGE.get()]
                                )
                                checkbox_tag2 = dpg.generate_uuid()
                                dpg.add_checkbox(tag=checkbox_tag2)
                            dpg.add_spacer(height=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_create"][LANGUAGE.get()]
                                + "...",
                                callback=create_all_sets_callback,
                                user_data=checkbox_tag2,
                            )
                            dpg.bind_item_theme(
                                dpg.last_item(), "alternate_button_theme"
                            )
                            dpg.add_spacer(height=10)

        # Assignment management header
        header3_label = DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()]
        with dpg.collapsing_header(label=header3_label):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
                            callback=lambda s, a, u: open_new_assignment_window(),
                            tag=UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"],
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_add_week"][LANGUAGE.get()],
                            callback=lambda s, a, u: open_new_week_window(),
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")

                    dpg.add_spacer(height=10)
                    dpg.add_separator()
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_open_assignment_browse"][
                                LANGUAGE.get()
                            ],
                            callback=open_assignment_browse,
                            user_data=(True, False, None, None),
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_open_week_browse"][LANGUAGE.get()],
                            callback=open_week_browse,
                            user_data=(False, None),
                        )
                        dpg.bind_item_theme(dpg.last_item(), "alternate_button_theme")
            dpg.add_spacer(height=10)

        ##### DEV buttons
        with dpg.collapsing_header(label="DEV"):
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Current index (TEMP)",
                        callback=lambda s, a, u: pprint(get_all_indexed_assignments()),
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label="Tehtävävalitsin",
                        callback=temp_selector_wrapper,
                        user_data=True,
                    )
                    dpg.add_spacer(width=5)
                    dpg.add_button(
                        label="Viikkovalitsin",
                        callback=temp_selector_wrapper,
                        user_data=False,
                    )


def temp_selector_wrapper(s, a, u: bool):
    """DEV only"""
    if u:
        selected = []
        open_assignment_browse(None, None, (True, True, selected))
    else:
        selected = []
        open_week_browse(None, None, (True, selected))


def _add_example_run_window(
    sender, app_data, user_data: tuple[dict, int, int | str, bool]
):
    """
    Adds an example run input window
    """

    var = user_data[0]
    ex_listbox = user_data[2]
    val = dpg.get_value(ex_listbox).split(" ")
    ix = None
    if len(val) != 1:
        ix = int(val[1]) - 1
    new = user_data[1]
    if not new:
        ex_run = var["example_runs"][ix]
    elif new:
        ex_run = get_empty_example_run()
        ix = len(var["example_runs"])
    else:
        return
    select = user_data[3]

    UUIDs = {"{}".format(i): dpg.generate_uuid() for i in EXAMPLE_RUN_KEY_LIST}
    label = DISPLAY_TEXTS["ex_run"][LANGUAGE.get()] + " " + str(ix + 1)
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
                    multiline=True,
                    height=150,
                    tab_input=True,
                    tag=UUIDs["INPUTS"],
                    enabled=select,
                    default_value="\n".join([str(item) for item in ex_run["inputs"]]),
                )
                dpg.add_spacer(height=5)

                # Command line inputs
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE.get()])
                dpg.add_input_text(
                    tag=UUIDs["CMD_INPUTS"],
                    enabled=select,
                    tab_input=True,
                    default_value=", ".join(
                        [str(item) for item in ex_run["cmd_inputs"]]
                    ),
                )

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
                        default_value=ex_run["generate"],
                    )

                # Output text
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE.get()])
                dpg.add_input_text(
                    tag=UUIDs["OUTPUT"],
                    multiline=True,
                    height=150,
                    enabled=select,
                    tab_input=True,
                    default_value=ex_run["output"],
                )
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
                                user_data=(
                                    ex_run,
                                    UUIDs["OUTPUT_FILES"],
                                    "outputfiles",
                                ),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_remove_selected"][
                                    LANGUAGE.get()
                                ],
                                callback=remove_selected,
                                user_data=(
                                    UUIDs["OUTPUT_FILES"],
                                    ex_run,
                                    "outputfiles",
                                ),
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
                        user_data=(UUIDs, ex_run, var, new, ix, ex_listbox),
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
        var_index = get_variation_index(*user_data[1])
        data = parent_data["variations"][var_index]

    select = user_data[2]
    if select:
        select = False
    else:
        select = True

    var_letter = (
        get_variation_letter(len(parent_data["variations"]) + 1)
        if user_data[1] == -1
        else data["variation_id"]
    )
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()] + " " + var_letter
    UUIDs = {"{}".format(i): dpg.generate_uuid() for i in VARIATION_KEY_LIST}

    with dpg.window(
        label=label, tag=UUIDs["WINDOW_ID"], width=750, height=750, no_close=True
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
                    enabled=select,
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
                            user_data=(data, True, UUIDs["EXAMPLE_LISTBOX"], select),
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
                            False,
                            UUIDs["EXAMPLE_LISTBOX"],
                            select,
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
                    enabled=select,
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

    if not var_data:
        var = get_empty_assignment()
        new = True
    else:
        var = var_data
        new = False

    if select:
        enable = False
        label = "Mímir - {} - {}".format(
            DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()],
            DISPLAY_TEXTS["ui_show_assignment"][LANGUAGE.get()],
        )
    else:
        enable = True
        label = "Mímir - {} - {}".format(
            DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()],
            DISPLAY_TEXTS["ui_add_assignment"][LANGUAGE.get()],
        )

    with dpg.window(
        label=label,
        width=750,
        height=750,
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
                            enabled=enable,
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
                            enabled=enable,
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
                            default_value=", ".join(
                                [str(item) for item in var["exp_assignment_no"]]
                            ),
                            enabled=enable,
                        )

                    # Assignment level
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_assignment_level"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_input_int(
                            width=150,
                            min_value=COURSE_INFO["min_level"],
                            max_value=COURSE_INFO["max_level"],
                            max_clamped=True,
                            min_clamped=True,
                            tag=UI_ITEM_TAGS["ASSIGNMENT_LEVEL"],
                            default_value=var["level"],
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
                            enabled=enable,
                        )

                    # Previous part checkbox
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_checkbox(
                            callback=toggle_enabled,
                            tag=UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
                            user_data=(
                                UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"],
                                UI_ITEM_TAGS["PREV_PART_ADD"],
                                UI_ITEM_TAGS["PREV_PART_SHOW"],
                                UI_ITEM_TAGS["PREV_PART_DEL"],
                            ),
                            default_value=False if not var["previous"] else True,
                            enabled=enable,
                        )

                    # Code language
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            ("Python", "C"),
                            tag=UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"],
                            default_value=var["code_language"],
                            enabled=enable,
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
                            default_value=var["instruction_language"],
                            enabled=enable,
                        )
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)

                # Previous part input
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE.get()])
                    prev = [] if not var["previous"] else var["previous"]
                    dpg.add_listbox(
                        prev,
                        num_items=2,
                        enabled=enable,
                        tag=UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"],
                    )

                    # Previous part listbox buttons
                    dpg.add_spacer(height=5)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                            callback=show_prev_part,
                            tag=UI_ITEM_TAGS["PREV_PART_SHOW"],
                            enabled=False if not var["previous"] else True,
                        )
                        if enable:
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_add"][LANGUAGE.get()],
                                callback=add_prev,
                                user_data=var,
                                tag=UI_ITEM_TAGS["PREV_PART_ADD"],
                                enabled=False if not var["previous"] else True,
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_remove_selected"][
                                    LANGUAGE.get()
                                ],
                                callback=del_prev,
                                user_data=var,
                                tag=UI_ITEM_TAGS["PREV_PART_DEL"],
                                enabled=False if not var["previous"] else True,
                            )

            dpg.add_spacer(height=5)
            dpg.add_separator()
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

            # Variation listbox buttons
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                if not select:
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_add_variation"][LANGUAGE.get()],
                        callback=_add_variation_window,
                        user_data=(var, -1, select),
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
                        (
                            var["variations"],
                            UI_ITEM_TAGS["VARIATION_GROUP"],
                        ),
                        select,
                    ),
                )
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
                    if not new:
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_delete"][LANGUAGE.get()],
                            callback=popup_confirmation,
                            user_data=(
                                DISPLAY_TEXTS["ui_confirm"][LANGUAGE.get()],
                                delete_assignment,
                                (
                                    var,
                                    UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"],
                                ),
                            ),
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


def assignment_browse_window(
    search=True, select=False, select_save=None, listbox_id=None
):
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
                        user_data=select,
                    )
                    dpg.add_spacer(width=340)
                    dpg.add_button(
                        label="<- " + DISPLAY_TEXTS["ui_previous"][LANGUAGE.get()],
                        width=120,
                        enabled=True,
                        callback=swap_page,
                        user_data=(pagenum, get_all_indexed_assignments(), "-", False),
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
                        user_data=(pagenum, get_all_indexed_assignments(), "+", False),
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
                            user_data=(select_save, listbox_id),
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


def open_assignment_browse(s, a, u: tuple[bool, bool, list, int | str]):
    """
    Shorthand to check and open the assingment browse window.
    """

    if not dpg.does_item_exist(UI_ITEM_TAGS["LIST_WINDOW"]):
        if OPEN_COURSE_PATH.get():
            if COURSE_INFO["course_id"]:
                assignment_browse_window(
                    search=u[0], select=u[1], select_save=u[2], listbox_id=u[3]
                )
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


def _assignment_edit_callback(s, a, u: bool):
    value = get_value_from_browse()
    _json = get_assignment_json(
        join(OPEN_COURSE_PATH.get_subdir(metadata=True), value["a_id"] + ".json")
    )
    if u:
        show_prev_part(None, None, _json)
    else:
        open_new_assignment_window(_json, False)


def show_prev_part(s, a, u: dict | None):
    """
    Open an assignment for view. Used only with previous part listbox in assignment edit.
    """

    if not u:
        val = dpg.get_value(UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"])
        if not val:
            return
        var = get_assignment_json(
            join(OPEN_COURSE_PATH.get_subdir(metadata=True), val + ".json")
        )
    else:
        var = u

    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assignment_management"][LANGUAGE.get()],
        DISPLAY_TEXTS["ui_show_assignment"][LANGUAGE.get()],
    )
    enable = False
    window_id = dpg.generate_uuid()

    with dpg.window(label=label, width=750, height=700, no_close=True, tag=window_id):
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
                            default_value=var["title"],
                            enabled=enable,
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
                            default_value=var["exp_lecture"],
                            enabled=enable,
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
                            default_value=", ".join(
                                [str(item) for item in var["exp_assignment_no"]]
                            ),
                            enabled=enable,
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
                            default_value=", ".join(var["tags"]),
                            enabled=enable,
                        )

                    # Previous part checkbox
                    with dpg.table_row():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_exp_assignment"][LANGUAGE.get()] + ":"
                        )
                        dpg.add_checkbox(
                            callback=toggle_enabled,
                            user_data=UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"],
                            default_value=False
                            if not var["next"] or not var["previous"]
                            else True,
                            enabled=enable,
                        )

                    # Code language
                    with dpg.table_row():
                        dpg.add_text(DISPLAY_TEXTS["ui_code_lang"][LANGUAGE.get()])
                        dpg.add_combo(
                            ("Python", "C"),
                            default_value=var["code_language"],
                            enabled=enable,
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
                            default_value=var["instruction_language"],
                            enabled=enable,
                        )
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=25)
                with dpg.group():
                    dpg.add_spacer(height=5)

                    # Previous part input
                    with dpg.group():
                        dpg.add_text(DISPLAY_TEXTS["ui_prev_part"][LANGUAGE.get()])
                        prev = [] if not var["previous"] else var["previous"]
                        listbox_tag = dpg.generate_uuid()
                        dpg.add_listbox(
                            prev, num_items=2, enabled=enable, tag=listbox_tag
                        )

                        # Previous part listbox buttons
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                                callback=show_prev_part,
                                user_data=dpg.get_value(listbox_tag),
                            )

                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
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
                        var_tag = dpg.generate_uuid()
                        dpg.add_listbox(_vars, tag=var_tag)

                    # Listbox buttons
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                        callback=show_var,
                        user_data=(
                            var,
                            -2
                            if not var["variations"]
                            else (
                                var["variations"],
                                var_tag,
                            ),
                        ),
                    )
                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)

                    # Window buttons
                    dpg.add_button(
                        label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                        callback=lambda s, a, u: close_window(u),
                        user_data=window_id,
                    )


def show_var(s, a, user_data):
    """
    Shows variation data. Mainly used with assignment previous part show structure.
    """

    parent_data = user_data[0]

    if user_data[1] == -1:
        data = get_empty_variation()
    elif user_data[1] == -2:
        return
    else:
        var_index = get_variation_index(*user_data[1])
        data = parent_data["variations"][var_index]

    select = False

    var_letter = (
        get_variation_letter(len(parent_data["variations"]) + 1)
        if user_data[1] == -1
        else data["variation_id"]
    )
    label = DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()] + " " + var_letter
    window_id = dpg.generate_uuid()

    with dpg.window(label=label, tag=window_id, width=750, height=700, no_close=True):
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
                    enabled=select,
                )
                dpg.add_spacer(width=5)

                # Example run list box and its buttons
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_ex_runs"][LANGUAGE.get()])
                    with dpg.group():
                        runs = (
                            []
                            if not data["example_runs"]
                            else [
                                "{} {}".format(
                                    DISPLAY_TEXTS["ex_run"][LANGUAGE.get()], i
                                )
                                for i, _ in enumerate(data["example_runs"], start=1)
                            ]
                        )
                        exrun_id = dpg.generate_uuid()
                        dpg.add_listbox(runs, tag=exrun_id)
                    dpg.add_spacer(height=5)

                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                            callback=show_exrun,
                            user_data=(
                                data,
                                1
                                if not data["example_runs"]
                                else int(dpg.get_value(exrun_id).split(" ")[1]) - 1,
                            ),
                        )

                # Used in text box
                with dpg.group():
                    dpg.add_spacer(height=5)
                    dpg.add_text(DISPLAY_TEXTS["ui_used_in"][LANGUAGE.get()])
                    help_(DISPLAY_TEXTS["help_used_in"][LANGUAGE.get()])
                    dpg.add_input_text(
                        default_value=", ".join(
                            year_conversion(data["used_in"], False)
                        ),
                        enabled=select,
                    )
                    dpg.add_spacer(width=5)

                # Code files listbox and its buttons
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_codefiles"][LANGUAGE.get()])
                    files = (
                        []
                        if not data["codefiles"]
                        else [path_leaf(f_p) for f_p in data["codefiles"]]
                    )
                    dpg.add_listbox(files)
                    dpg.add_spacer(height=5)

                # Datafiles listbox and its buttons
                with dpg.group():
                    dpg.add_text(DISPLAY_TEXTS["ui_datafiles"][LANGUAGE.get()])
                    files = (
                        []
                        if not data["datafiles"]
                        else [path_leaf(f_p) for f_p in data["datafiles"]]
                    )
                    dpg.add_listbox(files)
                    dpg.add_spacer(height=5)

                # Window buttons
                dpg.add_separator()
                dpg.add_spacer(height=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                    callback=lambda s, a, u: close_window(u),
                    user_data=window_id,
                )


def show_exrun(s, a, user_data):
    """
    Shows an example run
    """

    var = user_data[0]
    ix = user_data[1]
    try:
        ex_run = var["example_runs"][ix]
    except IndexError:
        ex_run = get_empty_example_run()

    select = False

    label = DISPLAY_TEXTS["ex_run"][LANGUAGE.get()] + " " + str(user_data[1])
    window_id = dpg.generate_uuid()
    with dpg.window(label=label, tag=window_id, width=750, height=700, no_close=True):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                # Inputs
                dpg.add_text(DISPLAY_TEXTS["ex_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_inputs"][LANGUAGE.get()])
                dpg.add_input_text(
                    multiline=True,
                    height=150,
                    tab_input=True,
                    enabled=select,
                    default_value="\n".join([str(item) for item in ex_run["inputs"]]),
                )
                dpg.add_spacer(height=5)

                # Command line inputs
                dpg.add_text(DISPLAY_TEXTS["cmd_input"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_cmd_inputs"][LANGUAGE.get()])
                dpg.add_input_text(
                    enabled=select,
                    default_value=", ".join(
                        [str(item) for item in ex_run["cmd_inputs"]]
                    ),
                )

                # Generate ex run checkbox
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text(DISPLAY_TEXTS["ui_gen_ex_checkbox"][LANGUAGE.get()])
                    help_(DISPLAY_TEXTS["help_gen_ex_checkbox"][LANGUAGE.get()])
                    dpg.add_checkbox(
                        callback=toggle_enabled,
                        enabled=select,
                        default_value=ex_run["generate"],
                    )

                # Output text
                dpg.add_text(DISPLAY_TEXTS["ex_output"][LANGUAGE.get()])
                help_(DISPLAY_TEXTS["help_ex_output"][LANGUAGE.get()])
                dpg.add_input_text(
                    multiline=True,
                    height=150,
                    enabled=select,
                    default_value=ex_run["output"],
                )
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
                    dpg.add_listbox(files)
                    dpg.add_spacer(height=5)

                dpg.add_spacer(height=10)

                # Window buttons
                dpg.add_separator()
                dpg.add_spacer(height=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_close"][LANGUAGE.get()],
                    callback=lambda s, a, u: close_window(u),
                    user_data=window_id,
                )


def add_prev(s, a, u: dict):
    """
    Add a previous assignment to the current
    """
    open_assignment_browse(
        None, None, (True, True, [u], UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"])
    )


def create_one_set_callback(s, a, u):
    """
    Callback function for main window button
    """

    week_n = dpg.get_value(u[0])
    exc_exp = dpg.get_value(u[1])
    all_weeks = get_week_data().copy()
    week = False
    for w in all_weeks["lectures"]:
        if w["lecture_no"] == week_n:
            all_weeks["lectures"] = [w]
            week = True
            break

    if week:
        _set = generate_one_set(
            all_weeks["lectures"][0]["lecture_no"],
            all_weeks["lectures"][0]["assignment_count"],
            exclude_expanding=exc_exp,
        )
        formatted = format_set(_set)
        result_window(formatted, all_weeks)


def create_all_sets_callback(s, a, u):
    """
    Callback function for main window button
    """

    exc_exp = dpg.get_value(u)
    _sets = generate_full_set(exclude_expanding=exc_exp)
    formatted = [format_set(_set) for _set in _sets]
    weeks = get_week_data()
    result_window(formatted, weeks)


def result_window(orig_set: list, weeks: dict):
    """
    The result preview window for generated sets
    """

    label = "Mímir - {} - {}".format(
        DISPLAY_TEXTS["ui_assig_set_creation"][LANGUAGE.get()],
        DISPLAY_TEXTS["ui_results"][LANGUAGE.get()],
    )

    window_id = dpg.generate_uuid()

    if not isinstance(orig_set[0], dict):
        UUIDs = [dpg.generate_uuid() for i in range(0, len(orig_set))]
        _set = orig_set
    else:
        _set = [orig_set]
        UUIDs = [dpg.generate_uuid()]

    # if week == None:
    #     weeks = get_week_data()
    #     weeks["lectures"].sort(key=lambda a: a["lecture_no"])
    # else:
    #     weeks = [week]

    with dpg.window(
        label=label,
        width=1400,
        height=725,
        tag=window_id,
        no_close=True,
        no_collapse=True,
        no_resize=True,
    ):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            with dpg.group():
                i = 0
                for i, _id in enumerate(UUIDs):
                    with dpg.group():
                        dpg.add_text(
                            DISPLAY_TEXTS["ui_week"][LANGUAGE.get()]
                            + " "
                            + str(weeks["lectures"][i]["lecture_no"])
                        )
                        items = gen_result_headers(
                            _set[i], weeks["lectures"][i]["lecture_no"]
                        )
                        dpg.add_listbox(
                            items,
                            tag=_id,
                            num_items=weeks["lectures"][i]["assignment_count"],
                        )
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                                callback=show_result_assig,
                                user_data=(
                                    _id,
                                    i,
                                    _set,
                                    weeks["lectures"][i]["lecture_no"],
                                ),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_delete"][LANGUAGE.get()],
                                callback=del_result,
                                user_data=(_id, i, _set, weeks),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_add"][LANGUAGE.get()],
                                callback=add_result,
                                user_data=(_id, i, _set, weeks),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_change"][LANGUAGE.get()],
                                callback=change_result,
                                user_data=(_id, i, _set, weeks),
                            )
                        dpg.add_spacer(height=5)
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_move_up"][LANGUAGE.get()],
                                callback=move_up,
                                user_data=(_id, i, _set),
                            )
                            dpg.add_spacer(width=5)
                            dpg.add_button(
                                label=DISPLAY_TEXTS["ui_move_down"][LANGUAGE.get()],
                                callback=move_down,
                                user_data=(_id, i, _set),
                            )

                with dpg.group():
                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    if i == 0:
                        dpg.add_spacer(height=325)
                        dpg.add_separator()
                        dpg.add_spacer(height=5)
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_accept"][LANGUAGE.get()],
                            callback=accept_result_set,
                            user_data=(_set, weeks),
                        )
                        dpg.add_spacer(width=5)
                        dpg.add_button(
                            label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                            callback=lambda s, a, u: close_window(u),
                            user_data=window_id,
                        )


def add_result(s, a, u: tuple[int | str, int, list]):
    """
    Add result to result set
    """
    listbox_id = u[0]
    index = u[1]
    _set = u[2]
    week = u[3]["lectures"][index]["lecture_no"]

    result_popup(None, "", (_set, index, len(_set[index]), listbox_id, week))


def change_result(s, a, u: tuple[int | str, int, list]):
    """
    Change result in set
    """
    listbox_id = u[0]
    value = dpg.get_value(listbox_id)
    index = u[1]
    _set = u[2]
    week = u[3]["lectures"][index]["lecture_no"]
    correct = None
    assig_index = None
    for i, item in enumerate(_set[index], start=1):
        t = ""
        t += DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()] + str(week)
        t += DISPLAY_TEXTS["tex_assignment_letter"][LANGUAGE.get()] + str(i)
        t += " - " + item["title"]
        t += (
            " - "
            + DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()]
            + " "
            + item["variations"][0]["variation_id"]
        )
        if t == value:
            correct_item = item
            assig_index = i - 1

    correct = get_assignment_json(
        join(
            OPEN_COURSE_PATH.get_subdir(metadata=True),
            correct_item["assignment_id"] + ".json",
        )
    )
    meta = (_set, index, assig_index, listbox_id, week)
    result_popup(correct, correct_item["variations"][0]["variation_id"], meta)


def show_result_assig(s, a, u):
    """
    Show resulting assignment from result window
    """
    listbox_id = u[0]
    value = dpg.get_value(listbox_id)
    index = u[1]
    _set = u[2]
    week = u[3]
    for i, item in enumerate(_set[index], start=1):
        t = ""
        t += DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()] + str(week)
        t += DISPLAY_TEXTS["tex_assignment_letter"][LANGUAGE.get()] + str(i)
        t += " - " + item["title"]
        t += (
            " - "
            + DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()]
            + " "
            + item["variations"][0]["variation_id"]
        )
        if t == value:
            correct_item = item

    correct = get_assignment_json(
        join(
            OPEN_COURSE_PATH.get_subdir(metadata=True),
            correct_item["assignment_id"] + ".json",
        )
    )
    show_prev_part(None, None, correct)


def accept_result_set(s, a, u: tuple[list, dict]):
    """
    Create instruction papers from accepted set
    """
    tex_gen(u)


def result_popup(
    data: dict | None, var_id: str, meta: tuple[list, int, int, int | str, int]
):
    """
    Open result change/add popup
    """

    field_ids = {
        "popup": dpg.generate_uuid(),
        "title": dpg.generate_uuid(),
        "var": dpg.generate_uuid(),
    }
    select = []
    with dpg.window(
        tag=field_ids["popup"],
        no_close=True,
        no_collapse=True,
        no_title_bar=True,
        autosize=True,
    ):
        with dpg.group():
            dpg.add_spacer(height=2)
        with dpg.group():
            dpg.add_text(label=DISPLAY_TEXTS["ui_current_assig"][LANGUAGE.get()] + ":")
            dpg.add_input_text(
                enabled=False,
                default_value="" if not data else data["title"],
                tag=field_ids["title"],
            )
            dpg.add_spacer(height=3)
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_change"][LANGUAGE.get()],
                callback=open_assignment_browse,
                user_data=(True, True, select, (meta, field_ids)),
            )
            dpg.add_spacer(height=5)
            dpg.add_text(DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()] + ":")
            dpg.add_combo(
                [] if not data else [a["variation_id"] for a in data["variations"]],
                tag=field_ids["var"],
                default_value=var_id,
            )
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_show"][LANGUAGE.get()],
                callback=show_var_result,
                user_data=(select, field_ids),
            )
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                    callback=save_result_popup,
                    user_data=(data, meta, select, field_ids),
                )
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                    callback=lambda s, a, u: close_window(u),
                    user_data=field_ids["popup"],
                )


def show_var_result(s, a, u: tuple[list, dict]):
    """
    Show variation from result change popup
    """

    value = dpg.get_value(u[1]["var"])
    if value:
        i = -1
        for i, a in enumerate(u[0][0]["variations"]):
            if a["variation_id"] == value:
                break
        if i != -1:
            show_var(None, None, (u[0][0], i))


def delete_assignment(s, a, u: tuple[str, str | int, str | int]):
    """
    Shorthand for deleting assignment from both disk and index.
    """

    assignment_id = u[0]["assignment_id"]
    window_id = u[1]
    popup_id = u[2]

    close_window(popup_id)

    res = del_assignment_files(assignment_id)
    if not res:
        popup_ok(DISPLAY_TEXTS["ui_del_error_disk"][LANGUAGE.get()])
    else:
        res = del_assignment_from_index(assignment_id)
        if not res:
            popup_ok(DISPLAY_TEXTS["ui_del_error_index"][LANGUAGE.get()])
        else:
            popup_ok(DISPLAY_TEXTS["ui_del_ok"][LANGUAGE.get()])

    dpg.configure_item(UI_ITEM_TAGS["total_index"], default_value=get_number_of_docs())
    clear_search_bar(None, None, [1])
    close_window(window_id)


def reopen_main(s, a, lang: str):
    """
    Reopens the main window after language selection. Sets the new language.
    """

    LANGUAGE.set(lang)
    close_window(UI_ITEM_TAGS["MAIN_WINDOW"])
    # for window in dpg.get_windows():
    #     print(window)
    #     close_window(window)
    main_window()
    dpg.set_primary_window(UI_ITEM_TAGS["MAIN_WINDOW"], True)
