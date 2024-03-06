"""Mímir UI helper functions for callbacks"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join
from os import getcwd
from string import ascii_uppercase
from tkinter.filedialog import askopenfilenames
import dearpygui.dearpygui as dpg

from src.constants import (
    FILETYPES,
    DISPLAY_TEXTS,
    LANGUAGE,
    UI_ITEM_TAGS,
    OPEN_COURSE_PATH,
    COURSE_INFO,
)
from src.data_handler import (
    path_leaf,
    save_course_info,
    ask_course_dir,
    save_assignment_data,
    save_week_data,
    year_conversion,
    search_index,
    get_value_from_browse,
    gen_result_headers,
    delete_files
)
from src.data_getters import (
    get_header_page,
    get_all_indexed_assignments,
    get_assignment_json,
    get_variation_index,
    get_period_default,
)
from src.common import resource_path, round_up
from src.window_helper import close_window
from src.popups import popup_ok

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
            resource_path(join("resource", "source-sans-pro", "SourceSansPro-Bold.ttf")),
            24,
        )

    return _fonts


def set_style():
    """
    Set colours, fonts etc.
    """
    fonts = _load_fonts()
    dpg.bind_font(fonts["default"])
    logging.debug("Fonts loaded.")

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

    with dpg.theme(tag="alternate_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)

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
    logging.debug("Texture registry added, with %d textures inside." % i)


def setup_ui():
    """
    Shorthand for calling all UI setup functions
    """
    set_style()
    setup_textures()


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


def get_variation_letter(var):
    base = len(ascii_uppercase)
    result = ""
    while var > 0:
        result = ascii_uppercase[(var - 1) % base] + result
        var = (var - 1) // base
    return result


def extract_variation_data(s, a, u: tuple[dict, str, dict, dict, int]):
    """
    Gets values from variation input fields and saves the data to parent dict
    """
    UUIDS = u[0]
    var_letter = u[1]
    parent_data = u[2]
    data = u[3]
    ix = u[4]

    data["instructions"] = dpg.get_value(UUIDS["INSTRUCTIONS"]).strip()
    data["used_in"] = year_conversion(
        [item.strip() for item in dpg.get_value(UUIDS["USED_IN"]).split(",")], True
    )

    if ix == -1:
        data["variation_id"] = var_letter
        parent_data["variations"].append(data)
        _vars = (
            []
            if not parent_data["variations"]
            else [
                "{} {}".format(
                    DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()], item["variation_id"]
                )
                for item in parent_data["variations"]
            ]
        )
        dpg.configure_item(UI_ITEM_TAGS["VARIATION_GROUP"], items=_vars)
    else:
        new_index = get_variation_index(*ix)
        parent_data["variations"][new_index] = data

    close_window(UUIDS["WINDOW_ID"])


def extract_exrun_data(s, a, u: tuple[dict, dict, dict, bool, int, int | str]):
    """
    Gets values from exrun input fields and saves the data to the parent dict.
    """
    UUIDS = u[0]
    ex_run = u[1]
    var = u[2]
    new = u[3]
    ix = u[4]
    ex_listbox = u[5]

    ex_run["generate"] = dpg.get_value(UUIDS["GEN_EX"])
    ex_run["inputs"] = dpg.get_value(UUIDS["INPUTS"]).split("\n")
    ex_run["cmd_inputs"] = [
        i.strip() for i in dpg.get_value(UUIDS["CMD_INPUTS"]).split(",")
    ]
    if not ex_run["generate"]:
        ex_run["output"] = dpg.get_value(UUIDS["OUTPUT"])

    if new:
        var["example_runs"].append(ex_run)
        runs = (
            []
            if not var["example_runs"]
            else [
                "{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE.get()], i)
                for i, _ in enumerate(var["example_runs"], start=1)
            ]
        )
        dpg.configure_item(ex_listbox, items=runs)
    else:
        var["example_runs"][ix] = ex_run

    close_window(UUIDS["WINDOW_ID"])


def get_files(s, a, u: tuple[dict, int | str, str]):
    """
    Gets file paths from the user and adds them to the spesified list box

    Params:
    u: A tuple that contains the dict to save to, listbox UUID and file type group name
    """
    save_to = u[0]
    listbox = u[1]
    f_type = u[2]

    if f_type == "codefile":
        files = openfilebrowser(f_type)
        save_to["codefiles"] += files
        files = save_to["codefiles"]
    elif f_type == "datafiles":
        files = openfilebrowser("textfile")
        save_to["datafiles"] += files
        files = save_to["datafiles"]
    elif f_type == "outputfiles":
        files = openfilebrowser("textfile")
        save_to["outputfiles"] += files
        files = save_to["outputfiles"]

    leafs = [path_leaf(i) for i in files]
    dpg.configure_item(listbox, items=leafs)


def openfilebrowser(f_type: str) -> list:
    """
    Opens the filebrowser with f_type file extensions available.
    Allows the selection of multiple files. Returns a list of paths of the selected files.
    """
    if f_type not in FILETYPES["types"]:
        raise TypeError("Filetype not found")
    if f_type != "any":
        extensions = FILETYPES[f_type] + FILETYPES["any"]
    else:
        extensions = FILETYPES[f_type]
    file_paths = askopenfilenames(initialdir=getcwd(), filetypes=extensions)
    return list(file_paths)

def delete_wrapper(old, data, aID):
    """
    Wrapper for deletion function.
    """

    result = delete_files(join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), aID, old))
    if not result:
        data.append(old)
        popup_ok(DISPLAY_TEXTS["ui_error_delete"][LANGUAGE.get()])


def remove_selected(s, a, u):
    """
    Removes the selected item from the listbox.

    Params:
    u: A tuple that contains:
        0. The listbox to remove from
        1. The data structure to remove from
        2. The type of data to remove
        3. Assignment ID (or None)
    """
    selected = dpg.get_value(u[0])
    data = u[1]
    i_type = u[2]
    aID = u[3]
    final = []

    if selected == "":
        return

    if i_type == "variation":
        for i, item in enumerate(data["variations"]):
            if item["variation_id"] == selected.split(" ")[1]:
                old = data["variations"].pop(i)
                final = data["variations"]
                if aID:
                    to_delete = []
                    (to_delete.append(join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), aID, x)) for x in old["codefiles"])
                    (to_delete.append(join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), aID, x)) for x in old["datafiles"])
                    for y in old["example_runs"]:
                        for x in y["outputfiles"]:
                            to_delete.append(join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), aID, x))
                    delete_files(to_delete)
                break
    elif i_type == "datafiles":
        for i, item in enumerate(data["datafiles"]):
            if path_leaf(item) == selected:
                old = data["datafiles"].pop(i)
                if aID:
                    delete_wrapper(old, data["datafiles"], aID)
                final = [path_leaf(i) for i in data["datafiles"]]
                break
    elif i_type == "codefiles":
        for i, item in enumerate(data["codefiles"]):
            if path_leaf(item) == selected:
                old = data["codefiles"].pop(i)
                if aID:
                    delete_wrapper(old, data["codefiles"], aID)
                final = [path_leaf(i) for i in data["codefiles"]]
                break
    elif i_type == "outputfiles":
        for i, item in enumerate(data["outputfiles"]):
            if path_leaf(item) == selected:
                old = data["outputfiles"].pop(i)
                if aID:
                    delete_wrapper(old, data["outputfiles"], aID)
                final = [path_leaf(i) for i in data["outputfiles"]]

                break
    elif i_type == "ex_run":
        index = int(selected.split(" ")[1]) - 1
        old = data["example_runs"].pop(index)
        if aID:
            to_delete = [join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), aID, x) for x in old["outputfiles"]]
            result = delete_files(to_delete)
            if not result:
                popup_ok(DISPLAY_TEXTS["ui_error_delete"][LANGUAGE.get()])
        final = [
            "{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE.get()], i)
            for i, _ in enumerate(data["example_runs"], start=1)
        ]

    dpg.configure_item(u[0], items=final)


def toggle_enabled(sender, app_data, item: int | str | tuple):
    """
    Toggles item on or off depending on its previous state
    """
    if isinstance(item, tuple):
        for i in item:
            if dpg.is_item_enabled(i):
                dpg.disable_item(i)
            else:
                dpg.enable_item(i)

    else:
        if dpg.is_item_enabled(item):
            dpg.disable_item(item)
        else:
            dpg.enable_item(item)


def move_info(s, a, u: list):
    """
    Move course information to main window from popup and close it
    """
    if dpg.get_value(u["id"]):
        dpg.configure_item(
            UI_ITEM_TAGS["COURSE_ID"], default_value=dpg.get_value(u["id"])
        )
        dpg.configure_item(
            UI_ITEM_TAGS["COURSE_TITLE"], default_value=dpg.get_value(u["title"])
        )
        dpg.configure_item(
            UI_ITEM_TAGS["COURSE_WEEKS"], default_value=dpg.get_value(u["weeks"])
        )
        ask_course_dir()
        save_course_info()
    close_window(u["popup"])


def save_assignment(s, a, u: tuple[dict, bool]):
    """Save assignment data and close window"""

    assig = u[0]
    assig["title"] = dpg.get_value(UI_ITEM_TAGS["ASSIGNMENT_TITLE"]).strip().replace("*", "")
    assig["tags"] = [
        i.strip() for i in dpg.get_value(UI_ITEM_TAGS["ASSIGNMENT_TAGS"]).split(",")
    ]
    assig["exp_assignment_no"] = [
        int(i.strip()) for i in dpg.get_value(UI_ITEM_TAGS["ASSIGNMENT_NO"]).split(",")
    ]
    assig["level"] = dpg.get_value(UI_ITEM_TAGS["ASSIGNMENT_LEVEL"])
    assig["code_language"] = dpg.get_value(UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"])
    logging.debug("Assignment code language: %s", assig["code_language"])
    assig["instruction_language"] = dpg.get_value(UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"])
    logging.debug("Assignment instruction language: %s", assig["instruction_language"])
    assig["exp_lecture"] = dpg.get_value(UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"])

    save_assignment_data(assig, u[1])
    close_window(UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"])


def save_week(s, a, u: tuple[dict, bool, dict]) -> None:
    """
    Extract week data, save it and close the window.
    """
    week = u[0]
    new = u[1]
    UUIDs = u[2]

    week["lecture_no"] = dpg.get_value(UUIDs["LECTURE_NO"])
    week["title"] = dpg.get_value(UUIDs["TITLE"]).strip().replace("*", "")
    week["assignment_count"] = dpg.get_value(UUIDs["A_COUNT"])
    week["topics"] = [i.strip() for i in dpg.get_value(UUIDs["TOPICS"]).split("\n")]
    week["instructions"] = dpg.get_value(UUIDs["INSTRUCTIONS"]).strip()
    week["tags"] = [i.strip() for i in dpg.get_value(UUIDs["TAGS"]).split(",")]

    result = save_week_data(week, new)
    if result:
        close_window(UI_ITEM_TAGS["ADD_WEEK"])


def swap_page(s, a, u: tuple[list, list, str, bool]):
    """
    Change the visible page in listbox

    Params:
    u: a tuple of the page number (as a list), the data to show and the operation
    """

    orig_page = u[0]
    page = orig_page
    data = u[1]
    listbox_id = UI_ITEM_TAGS["LISTBOX"]
    text_id = UI_ITEM_TAGS["PAGENUM"]
    operation = u[2]
    week = u[3]

    if operation == "+":
        page[0] += 1
    else:
        if page[0] == 1:
            return
        page[0] -= 1

    headers = get_header_page(page[0], data, week=week)
    if not headers:
        page = orig_page
        return

    dpg.configure_item(listbox_id, items=headers)
    dpg.configure_item(
        text_id,
        default_value=str(page[0])
        + "/"
        + str(1 if len(data) == 0 else round_up(len(data) / 15)),
    )


def clear_search_bar(s, a, u: list):
    """
    Clears the search bar in week or assignment list windows
    and returns the listbox to default view

    Params:
    u: page number as list
    """

    dpg.configure_item(UI_ITEM_TAGS["SEARCH_BAR"], default_value="")
    u[0] = 1
    headers = get_header_page(1, get_all_indexed_assignments())
    dpg.configure_item(UI_ITEM_TAGS["LISTBOX"], items=headers)


def save_select(s, a, u: tuple[list, int | str | dict | tuple]):
    """
    Save the selected to the list and close browse window.
    """

    result = get_value_from_browse()

    if u[1] == UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"]:  # Previous part
        data = u[0][0]

        if not data["previous"]:
            data["previous"] = [result["a_id"]]
        else:
            data["previous"].append(result["a_id"])
        dpg.configure_item(UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"], items=data["previous"])
        close_window(UI_ITEM_TAGS["LIST_WINDOW"])

    elif u[1] == UI_ITEM_TAGS["PROJECT_WORK_DISPLAY"]:  # Project work
        dpg.configure_item(
            UI_ITEM_TAGS["PROJECT_WORK_DISPLAY"], default_value=result["a_id"]
        )
        close_window(UI_ITEM_TAGS["LIST_WINDOW"])

    else:  # Whatever the fuck this was...
        field_ids = u[1][1]
        data = get_assignment_json(
            join(OPEN_COURSE_PATH.get_subdir(metadata=True), result["a_id"] + ".json")
        )
        u[0].append(data)
        dpg.configure_item(field_ids["title"], default_value=data["title"])
        dpg.configure_item(
            field_ids["var"], items=[a["variation_id"] for a in data["variations"]]
        )
        close_window(UI_ITEM_TAGS["LIST_WINDOW"])


def assignment_search_wrapper(s, a, u: list):
    """
    Wrapper for calling search_index with the search query value
    """

    value = dpg.get_value(UI_ITEM_TAGS["SEARCH_BAR"]).strip()

    results = search_index(value)

    u[0] = 1
    headers = get_header_page(u[0], results)

    dpg.configure_item(UI_ITEM_TAGS["LISTBOX"], items=headers)


def save_result_popup(s, a, u: tuple[dict, tuple, list, dict]):
    """
    Save changed assignment from result popup
    """

    meta = u[1]
    select = u[2]
    _set = meta[0]
    index = meta[1]
    assig_index = meta[2]
    listbox_id = meta[3]
    week = meta[4]
    field_ids = u[3]

    var_value = dpg.get_value(field_ids["var"])
    if not var_value:
        return
    if not select:
        title = dpg.get_value(field_ids["title"])
        for item in _set[index]:
            if item["title"] == title:
                select.append(item)
                break

    select[0] = get_assignment_json(
        join(
            OPEN_COURSE_PATH.get_subdir(metadata=True),
            select[0]["assignment_id"] + ".json",
        )
    )
    for item in select[0]["variations"]:
        if item["variation_id"] == var_value:
            select[0]["variations"] = [item]
            break

    if len(_set[index]) - 1 <= assig_index:
        _set[index].append(select[0])
    else:
        _set[index][assig_index] = select[0]
    headers = gen_result_headers(_set[index], week)

    dpg.configure_item(listbox_id, items=headers)
    close_window(field_ids["popup"])


def configure_period_text(s: None | str | int, a: None, u: str | int) -> None:
    """
    Configure period text item

    Params:
    s: the sending (calling) function UUID or None
    a: not used
    u: text uuid
    """

    if not s:
        value = 1
    else:
        value = dpg.get_value(s)
    if value <= 3:
        if COURSE_INFO["periods"][str(value)] == "DEFAULT":
            period_name = get_period_default(value)
        else:
            period_name = COURSE_INFO["periods"][str(value)]
    else:
        period_name = COURSE_INFO["periods"][str(value)]

    dpg.set_value(u, period_name)
