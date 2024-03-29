"""
Mímir Data Handlers

Functions for processing data
"""

# pylint: disable=import-error, unused-argument, consider-using-f-string, invalid-name
import json
import logging
from os import path, mkdir, getcwd, remove
from ntpath import split, basename
from tkinter.filedialog import askdirectory
from hashlib import sha256
from shutil import copy2, rmtree

from whoosh import index
from whoosh.qparser import QueryParser
from dearpygui.dearpygui import get_value, configure_item

from src.constants import (
    ENV,
    DISPLAY_TEXTS,
    LANGUAGE,
    OPEN_IX,
    COURSE_INFO,
    OPEN_COURSE_PATH,
    UI_ITEM_TAGS,
    RECENTS,
    INDEX_SCHEMA,
    WEEK_DATA,
    LATEX_SYMBOLS,
)
from src.custom_errors import IndexExistsError, IndexNotOpenError
from src.data_getters import (
    get_pos_convert,
    read_datafile,
    get_assignment_code,
    get_week_data,
    get_number_of_docs,
    get_assignment_json,
    get_saved_assignment_sets,
    get_result_sets
)
from src.popups import popup_ok
from src.window_helper import close_window

########################################


def create_index(force=False, **args):
    """
    Creates an assignment index from schema that is used to store paths to all available
    assingments.
    Sets the created index as a global constant.

    Params:
    force: Force the creation of the index if it already exists.
    """

    ix_path = OPEN_COURSE_PATH.get_subdir(index=True)
    if not path.exists(ix_path):
        mkdir(ix_path)
    name = COURSE_INFO["course_id"]

    if index.exists_in(ix_path, name) and not force:
        raise IndexExistsError("Index '%s' already exists in '%s'" % (name, ix_path))

    try:
        ix = index.create_in(ix_path, INDEX_SCHEMA, name)
    except OSError:
        logging.exception("Unable to save index file.")
    else:
        OPEN_IX.set(ix)
        logging.debug("Index created and set.")


def open_index(**args):
    """
    Opens a previously created assignment index. Sets the opened index as a global constant.
    """

    ix_path = OPEN_COURSE_PATH.get_subdir(index=True)
    name = COURSE_INFO["course_id"]
    try:
        ix = index.open_dir(ix_path, name)
    except (OSError, index.EmptyIndexError):
        logging.exception("Could not open index file.")
        popup_ok(DISPLAY_TEXTS["ui_index_open_error"][LANGUAGE.get()])
        return -1
    else:
        OPEN_IX.set(ix)
        logging.debug("Index set.")
        return 0


def add_assignment_to_index(data: dict, expanding: bool):
    """
    Adds given assignements to the index currently open.

    Params:
    data: a dictionary containing assignment data
    expanding: bool whether the assignment is expanding
    """

    if not OPEN_IX.get():
        raise IndexNotOpenError
    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']};"
    positions += ",".join([str(item) for item in data["exp_assignment_no"]])
    tags = ",".join(data["tags"])
    json_path = data["assignment_id"]  # TODO legacy, should be removed

    writer = ix.writer()
    writer.add_document(
        a_id=data["assignment_id"],
        position=positions,
        tags=tags,
        title=data["title"],
        json_path=json_path,
        is_expanding=expanding,
        level=str(data["level"]),
    )
    writer.commit()


def _save_course_file():
    """
    Save course metadata to file
    """
    f_path = path.join(OPEN_COURSE_PATH.get(), "course_info.mcif")
    try:
        with open(f_path, "w", encoding="utf-8") as f:
            to_write = json.dumps(COURSE_INFO, indent=4)
            f.write(to_write)
    except OSError:
        logging.exception("Unable to save course info file.")
        popup_ok(DISPLAY_TEXTS["ui_error_save_course"][LANGUAGE.get()])


def save_course_info(**args):
    """
    Function to save course information from main window or course creation popup
    """

    new = 0
    if "new" in args.keys():
        new = args["new"]
        tags = args["tags"]
        COURSE_INFO["course_title"] = get_value(tags["title"])
        COURSE_INFO["course_id"] = get_value(tags["id"])
        COURSE_INFO["course_weeks"] = get_value(tags["weeks"])
        COURSE_INFO["course_levels"] = {}
        COURSE_INFO["min_level"] = 0
        COURSE_INFO["max_level"] = 0
    else:
        COURSE_INFO["course_title"] = get_value(UI_ITEM_TAGS["COURSE_TITLE"])
        COURSE_INFO["course_id"] = get_value(UI_ITEM_TAGS["COURSE_ID"])
        COURSE_INFO["course_weeks"] = get_value(UI_ITEM_TAGS["COURSE_WEEKS"])
        levels = {}
        raw = get_value(UI_ITEM_TAGS["COURSE_LEVELS"]).strip().split("\n")
        if raw[0] != "":
            try:
                for item in raw:
                    data = item.split(":")
                    levels[int(data[0])] = [data[1]]
                    if len(data) == 3:
                        levels[int(data[0])].append(data[2])
                COURSE_INFO["course_levels"] = levels
                COURSE_INFO["min_level"] = min(levels.keys())
                COURSE_INFO["max_level"] = max(levels.keys())
            except (IndexError, ValueError):
                logging.exception("Error in course level saving:")
                popup_ok(DISPLAY_TEXTS["ui_level_error"][LANGUAGE.get()])
                return
        else:
            COURSE_INFO["course_levels"] = {}
            COURSE_INFO["min_level"] = 0
            COURSE_INFO["max_level"] = 0

    if new:
        COURSE_INFO["periods"] = {
            "1": "DEFAULT",
            "2": "DEFAULT",
            "3": "DEFAULT",
        }

    if not OPEN_COURSE_PATH.get():
        ask_course_dir()
    _save_course_file()

    if new:
        configure_item(UI_ITEM_TAGS["COURSE_LEVELS"], default_value="")
        configure_item(UI_ITEM_TAGS["total_index"], default_value=0)
        create_index()


def update_index(data: dict, expanding: bool):
    """
    Updates the index with the data from the updated assignment.

    Params:
    data: assignment to update
    expanding: bool whether the assignment is expanding
    """

    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']};"
    positions += ",".join([str(item) for item in data["exp_assignment_no"]])
    tags = ",".join(data["tags"])
    json_path = data["assignment_id"]

    writer = ix.writer()
    writer.update_document(
        a_id=data["assignment_id"],
        position=positions,
        tags=tags,
        title=data["title"],
        json_path=json_path,
        is_expanding=expanding,
        level=str(data["level"]),
    )
    writer.commit()


def format_metadata_json(data: dict):
    """
    Add data of the files in the assignment to the dictionary and return the new one.

    Params:
    data: the dictionary containing original assignment data.
    Note, expects there to be only one variation.
    """
    new = {}
    new["title"] = data["title"]
    new["code_lang"] = data["code_language"]
    new["level"] = data["level"]
    new["a_id"] = data["assignment_id"]
    variation = None
    variation = data["variations"][0]
    new["instructions"] = variation["instructions"]
    example_runs = []
    for i, _ in enumerate(variation["example_runs"]):
        n = {
            "inputs": variation["example_runs"][i]["inputs"],
            "output": variation["example_runs"][i]["output"],
            "CMD": variation["example_runs"][i]["cmd_inputs"],
            "outputfiles": (
                [
                    {
                        "filename": j,
                        "data": read_datafile(
                            j,
                            data["assignment_id"],
                        ),
                    }
                    for j in variation["example_runs"][i]["outputfiles"]
                ]
                if variation["example_runs"][i]["outputfiles"]
                else []
            ),
        }
        example_runs.append(n)
    new["example_runs"] = example_runs
    if variation["datafiles"]:
        new["datafiles"] = []
        for df in variation["datafiles"]:
            new["datafiles"].append(
                {
                    "filename": df,
                    "data": read_datafile(df, data["assignment_id"]),
                }
            )
    new["example_codes"] = []
    for cf in variation["codefiles"]:
        new["example_codes"].append(
            {
                "filename": cf,
                "code": get_assignment_code(cf, data["assignment_id"]),
            }
        )
    if variation["images"]:
        new["images"] = variation["images"]
    return new


def save_next(assignment: dict):
    """
    Saves information on continuing assignments

    Params:
    assignment: a dict containing the assignment information to save
    """
    if not assignment["previous"]:
        return

    for last in assignment["previous"]:
        prev = get_assignment_json(
            path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), last + ".json")
        )
        if not prev["next"]:
            prev["next"] = [assignment["assignment_id"]]
        else:
            if assignment["assignment_id"] not in prev["next"]:
                prev["next"].append(assignment["assignment_id"])

    expanding = get_value(UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"])
    save_assignment_file(prev, False, expanding)


def save_assignment_data(assignment: dict, new: bool):
    """
    Saves assignment to database

    Params:
    assignment: Assignment data to save
    new: whether the assignment is new or existing
    """

    if new:
        assignment["course_id"] = COURSE_INFO["course_id"]
        assignment["course_title"] = COURSE_INFO["course_title"]
        _bytes = json.dumps(assignment).encode()
        _hash = sha256(usedforsecurity=False)
        _hash.update(_bytes)
        _hex = _hash.hexdigest()
        assignment["assignment_id"] = _hex
        save_next(assignment)

        basepath = OPEN_COURSE_PATH.get_subdir(assignment_data=True)
        datapath = path.join(basepath, _hex)
        if not path.exists(basepath):
            mkdir(basepath)
        if not path.exists(datapath):
            mkdir(datapath)
        for item in assignment["variations"]:
            for file in item["codefiles"]:
                copy2(file, datapath)
            leafs = [path_leaf(f_path) for f_path in item["codefiles"]]
            item["codefiles"] = leafs
            for file in item["datafiles"]:
                copy2(file, datapath)
            leafs = [path_leaf(f_path) for f_path in item["datafiles"]]
            item["datafiles"] = leafs
            for exrun in item["example_runs"]:
                for file in exrun["outputfiles"]:
                    copy2(file, datapath)
                leafs = [path_leaf(f_path) for f_path in exrun["outputfiles"]]
                exrun["outputfiles"] = leafs
        expanding = get_value(UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"])
    else:
        assignment["course_id"] = COURSE_INFO["course_id"]
        assignment["course_title"] = COURSE_INFO["course_title"]
        basepath = OPEN_COURSE_PATH.get_subdir(assignment_data=True)
        datapath = path.join(basepath, assignment["assignment_id"])
        save_next(assignment)

        for item in assignment["variations"]:
            for file in item["codefiles"]:
                if split(file)[0]:
                    copy2(file, datapath)
            leafs = [path_leaf(f_path) for f_path in item["codefiles"]]
            item["codefiles"] = leafs
            for file in item["datafiles"]:
                if split(file)[0]:
                    copy2(file, datapath)
            leafs = [path_leaf(f_path) for f_path in item["datafiles"]]
            item["datafiles"] = leafs
            for exrun in item["example_runs"]:
                for file in exrun["outputfiles"]:
                    if split(file)[0]:
                        copy2(file, datapath)
                leafs = [path_leaf(f_path) for f_path in exrun["outputfiles"]]
                exrun["outputfiles"] = leafs
        expanding = get_value(UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"])

    if not path.exists(OPEN_COURSE_PATH.get_subdir(metadata=True)):
        mkdir(OPEN_COURSE_PATH.get_subdir(metadata=True))

    save_assignment_file(assignment, new, expanding)


def save_assignment_file(assignment: dict, new: bool, expanding: bool):
    """
    I/O operation to save assignment file
    """

    _filepath = path.join(
        OPEN_COURSE_PATH.get_subdir(metadata=True),
        assignment["assignment_id"] + ".json",
    )
    _json = json.dumps(assignment, indent=4, ensure_ascii=False)
    try:
        with open(_filepath, "w", encoding="utf-8") as _file:
            _file.write(_json)
        if new:
            add_assignment_to_index(assignment, expanding)
        else:
            update_index(assignment, expanding)
        logging.info(
            "Successfully saved assignment %s to file and index.",
            assignment["assignment_id"],
        )
        configure_item(UI_ITEM_TAGS["total_index"], default_value=get_number_of_docs())
    except OSError:
        logging.exception("Error while saving assignment data!")
        popup_ok("Error saving assignment data into a file!")


def path_leaf(f_path):
    """Return the filename from a filepath"""
    head, tail = split(f_path)
    return tail or basename(head)


def ask_course_dir(**args):
    """
    Ask course directory from user
    """
    _dir = askdirectory(
        initialdir=getcwd(),
        mustexist=False,
        title=DISPLAY_TEXTS["ui_coursedir"][LANGUAGE.get()],
    )

    if _dir != "":
        if not path.exists(_dir):
            mkdir(_dir)
            _subdir = path.join(_dir, "metadata")
            mkdir(_subdir)
        OPEN_COURSE_PATH.set(_dir)
        save_recent()
        logging.info("Course path set as %s", OPEN_COURSE_PATH.get())
        return True
    else:
        return False


def save_recent(**args):
    """
    Save current course to recents
    """
    rec = RECENTS.get()
    if not OPEN_COURSE_PATH.get() in rec:
        if len(rec) < 5:
            try:
                ind = rec.index(OPEN_COURSE_PATH.get())
            except ValueError:
                pass
            else:
                rec.pop(ind)
            rec.reverse()
            rec.append(OPEN_COURSE_PATH.get())
            rec.reverse()
        else:
            try:
                ind = rec.index(OPEN_COURSE_PATH.get())
            except ValueError:
                ind = -1
            rec.pop(ind)
            rec.reverse()
            rec.append(OPEN_COURSE_PATH.get())
            rec.reverse()
    else:
        ind = rec.index(OPEN_COURSE_PATH.get())
        rec.pop(ind)
        rec.reverse()
        rec.append(OPEN_COURSE_PATH.get())
        rec.reverse()
    f_path = path.join(ENV["PROGRAM_DATA"], "recents.txt")
    try:
        with open(f_path, "w", encoding="utf-8") as f:
            for item in rec:
                f.write(item + "\n")
    except OSError:
        logging.exception("Error occured while saving recents to file!")
    RECENTS.set(rec)
    logging.debug("Recent courses set as: %s", rec)


def open_course(**args):
    """
    Opens a course to view
    """
    try:
        _dir = args["dir"]
    except KeyError:
        ask_course_dir()
    else:
        OPEN_COURSE_PATH.set(_dir)
        save_recent()

    if OPEN_COURSE_PATH.get() is not None:
        _file = path.join(OPEN_COURSE_PATH.get(), "course_info.mcif")
    else:
        return

    try:
        with open(_file, "r", encoding="utf-8") as f:
            _data = f.read()
    except OSError:
        logging.exception("Error in reading course info!")
        popup_ok(DISPLAY_TEXTS["ui_error_open_course"][LANGUAGE.get()])
    else:
        _json = json.loads(_data)
        for key in _json.keys():
            COURSE_INFO[key] = _json[key]
        if open_index() == -1:
            return
        configure_item(UI_ITEM_TAGS["COURSE_ID"], default_value=COURSE_INFO["course_id"])
        configure_item(
            UI_ITEM_TAGS["COURSE_TITLE"], default_value=COURSE_INFO["course_title"]
        )
        configure_item(
            UI_ITEM_TAGS["COURSE_WEEKS"], default_value=COURSE_INFO["course_weeks"]
        )
        configure_item(UI_ITEM_TAGS["total_index"], default_value=get_number_of_docs())

        levels = ""
        data = list(COURSE_INFO["course_levels"].keys())
        data.sort()
        for key in data:
            levels += f"{str(key)}:{COURSE_INFO['course_levels'][key][0]}"
            if len(COURSE_INFO["course_levels"][key]) == 2:
                levels += f":{COURSE_INFO['course_levels'][key][1]}"
            levels += "\n"
        configure_item(UI_ITEM_TAGS["COURSE_LEVELS"], default_value=levels)


def close_index() -> None:
    """Closes the open indexes."""

    ix = OPEN_IX.get()
    if ix:
        ix.close()

    logging.info("Indexes closed.")


def save_week_data(week, new) -> bool:
    """
    Save week data to file.

    Params:
    week: single week to save
    new: boolean if week is new
    """
    parent = get_week_data()

    if new:
        for i, item in enumerate(parent["lectures"]):
            if item["lecture_no"] == week["lecture_no"]:
                popup_ok(DISPLAY_TEXTS["ui_error_week_exists"][LANGUAGE.get()])
                return False
        parent["lectures"].append(week)
    else:
        for i, item in enumerate(parent["lectures"]):
            if item["lecture_no"] == week["lecture_no"]:
                parent["lectures"][i] = week
                break
    save_full_week(parent)
    return True


def save_full_week(parent):
    """
    File operation for week saving

    Params:
    parent: the full week data dict
    """

    f_path = path.join(OPEN_COURSE_PATH.get(), "weeks.json")
    try:
        with open(f_path, "w", encoding="utf-8") as f:
            _json = json.dumps(parent, indent=4, ensure_ascii=False)
            f.write(_json)
            WEEK_DATA.set(parent)
    except OSError:
        logging.exception("Error in saving week JSON.")
    else:
        logging.debug("Week data saved: %s", _json)


def year_conversion(data: list, encode: bool) -> list:
    """
    Converts the 'used in' value to number from text or vice versa.
    """
    return []
    if not data:
        return []

    pos_conv = get_pos_convert()[LANGUAGE.get()]
    converted = []
    if not encode:
        for item in data:
            try:
                converted.append(str(pos_conv[item[:-4]] + item[-4:]))
            except KeyError:
                logging.exception(
                    "Unable to convert position value from numeric to text!"
                )
    else:
        for item in data:
            for key in pos_conv.keys():
                if pos_conv[key].lower() == item[:-4].lower():
                    converted.append(str(key + item[-4:]))

    return converted


def search_index(query):
    """
    Search the assignment index. Defaults to searching from the "title" field

    Params:
    query: String to search the index with
    """

    ix = OPEN_IX.get()

    qp = QueryParser("title", ix.schema)
    q = qp.parse(query)

    sr = ix.searcher()
    results = sr.search(q)
    logging.debug("Search results: %s", results)

    typed = []
    for result in results:
        typed.append(dict(result))

    logging.debug("Full result data:\n%s", typed)

    return typed


def get_value_from_browse():
    """
    Extract the correct assignment or week from the browse view
    """

    value = get_value(UI_ITEM_TAGS["LISTBOX"])
    if not value:
        return None
    try:
        lecture = int(value.split(" - ")[0])
    except ValueError:
        title = value.split(" - ")[1]
        results = search_index(title)

        for result in results:
            header = ""
            header += (
                DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()]
                + result["position"].split(";")[0]
            )
            header += DISPLAY_TEXTS["tex_assignment_letter"][LANGUAGE.get()] + "("
            header += result["position"].split(";")[1] + ")"
            header += " - " + result["title"]
            if header == value:
                return result
    else:
        for week in get_week_data()["lectures"]:
            if week["lecture_no"] == lecture:
                return week


def del_prev(s, a, u: dict):
    """
    Delete previous assignment from list
    """

    to_del = get_value(UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"])
    var = u
    if not to_del:
        return

    ind = var["previous"].index(to_del)
    var["previous"].pop(ind)

    prev = get_assignment_json(
        path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), to_del + ".json")
    )
    try:
        ind = prev["next"].index(to_del)
        prev["next"].pop(ind)
    except ValueError:
        pass
    save_assignment_data(prev, False)
    configure_item(UI_ITEM_TAGS["PREVIOUS_PART_LISTBOX"], items=var["previous"])


def gen_result_headers(_set: list, week: int) -> list:
    """
    Generate result window assignment headers
    """

    headers = []

    for i, item in enumerate(_set, start=1):
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
        headers.append(t)

    return headers


def del_result(s, a, u: tuple[int | str, int, list]):
    """
    Delete result from the result set.
    """
    listbox_id = u[0]
    value = get_value(listbox_id)
    index_n = u[1]
    _set = u[2]
    week = u[3]
    assig_index = None
    for i, item in enumerate(_set[index_n], start=1):
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
            assig_index = i - 1
            break
    if assig_index == None:
        return
    _set[index_n].pop(assig_index)
    headers = gen_result_headers(_set[index_n], week)
    configure_item(listbox_id, items=headers)


def del_assignment_files(ID: str) -> bool:
    """
    Delete assignment from disk.
    """
    data_path = path.join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), ID)
    meta_path = path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), ID)

    try:
        if path.exists(data_path):
            rmtree(data_path)
        if path.exists(meta_path):
            rmtree(meta_path)
        return True
    except OSError:
        logging.exception("Unable to delete assignment files!")
        return False


def del_assignment_from_index(ID: str) -> bool:
    """
    Deletes spesified assignment from index.
    """
    writer = OPEN_IX.get().writer()
    res = writer.delete_by_term("a_id", ID)
    writer.commit()
    if res:
        return True
    return False


def format_week_data(data: dict) -> dict:
    """
    Changes week data to include lectures as one dict, with week number as key.
    """

    weeks = data["lectures"]
    new_dict = {}

    for week in weeks:
        new_dict[str(week["lecture_no"])] = week

    return new_dict


def del_week_data(s, a, u: tuple[dict, int]) -> None:
    """
    Delete a week from week data
    """
    parent = u[0]
    _index = u[1]
    window_id = u[2]
    popup_id = u[3]

    close_window(popup_id)
    close_window(window_id)
    del parent["lectures"][_index]
    save_full_week(parent)


def save_new_set(set_UUIDs: dict, sets: list) -> bool:
    """
    Save assignment set to disk.

    Params:
    set_UUIDs: the UUIDs of the set metadata from the result window
    sets: A list of sets to save 
    """

    saved = get_saved_assignment_sets()
    if not saved:
        popup_ok(DISPLAY_TEXTS["ui_error_load_set"][LANGUAGE.get()])
        return

    max_set_id = saved["maxSetID"]
    year = get_value(set_UUIDs["year"])
    period = get_value(set_UUIDs["period"])
    name = get_value(set_UUIDs["name"])

    set_to_save = {
        "id": max_set_id + 1,
        "year": year,
        "period": period,
        "name": name,
        "type": "week" if (len(sets) == 1) else "full",
        "assignments": None,
        "weeks": [],
    }
    for _set in sets:
        tempList = []
        for assig in _set:
            tempAssig = {}
            tempAssig["id"] = assig["assignment_id"]
            tempAssig["variationID"] = assig["variations"][0]["variation_id"]
            tempList.append(tempAssig)
        if set_to_save["type"] == "full":
            set_to_save["weeks"].append(tempList)
        else:
            set_to_save["assignments"] = tempList

    saved["maxSetID"] += 1
    saved["sets"].append(set_to_save)
    update_used(set_to_save)

    res = save_sets_disk(saved)
    return res


def update_used(_set:dict) -> None:
    """
    Add used period to the assignment metadata
    """

    period = f"{_set['year']}/{_set['period']}"
    if _set["type"] == "full":
        data_set = _set["weeks"]
    else:
        data_set = _set["assignments"]
    for assig in data_set:
        a_data = get_assignment_json(path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), assig["id"]+".json"))
        for var in a_data["variations"]:
            if assig["variationID"] == var["variation_id"]:
                if period not in var["used_in"]:
                    var["used_in"].append(period)
                    save_assignment_data(a_data, False)


def save_sets_disk(sets: dict) -> bool:
    """
    Save set data dict to disk.

    Params:
    sets: dictionary containing set information.
    """

    _path = OPEN_COURSE_PATH.get_set_path()

    try:
        with open(_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(sets, ensure_ascii=False, indent=4))
    except OSError:
        logging.exception("Could not save assignment sets to disk!")
        popup_ok(DISPLAY_TEXTS["ui_error_save_set"][LANGUAGE.get()])
        return False
    return True

def update_set(_set:dict, set_UUIDs:dict, assigs:list, window_id:int|str):
    """
    Update assignment set and save sets to disk

    Params:
    _set: set to save
    set_UUIDS: UUIDS of the fields to extract data from
    assigs: the full (modified) assignment set 
    window_id: ID of the window to close
    """

    data = get_saved_assignment_sets()

    _set["year"] = get_value(set_UUIDs["year"])
    _set["period"] = get_value(set_UUIDs["period"])
    _set["name"] = get_value(set_UUIDs["name"])

    for _assig in assigs:
        tempList = []
        for assig in _assig:
            tempAssig = {}
            tempAssig["id"] = assig["assignment_id"]
            tempAssig["variationID"] = assig["variations"][0]["variation_id"]
            tempList.append(tempAssig)
        if _set["type"] == "full":
            _set["weeks"].append(tempList)
        else:
            _set["assignments"] = tempList

    for i, _sets in enumerate(data["sets"]):
        if _sets["id"] == _set["id"]:
            data["sets"][i] = _set
            break

    save_sets_disk(data)
    configure_item(UI_ITEM_TAGS["LISTBOX"], items=get_result_sets())
    close_window(window_id)
    

def escape_latex_symbols(text: str):
    """
    Function to replace special symbols so they do not interfere with PDF generation
    NOTE: this function will not replace { or } characters, or re-escape symbols that are already escaped.
    The function is not a semantic LaTeX analyser though, so it will replace characters even if they are
    inside a special environment.

    Params:
    text: a string of text from which to replace symbols
    """

    for symbol in LATEX_SYMBOLS.keys():
        start = 0
        while True:
            substring = text[start:]
            text2 = text[:start]
            index = substring.find(symbol)
            if index == -1:
                break

            if substring[index - 1] != "\\":
                substring = substring.replace(symbol, LATEX_SYMBOLS[symbol], 1)
                start += index + 2
                text = text2 + substring
            else:
                start += index + 2
                text = text2 + substring

    return text


def _resolve_assignment(assig:dict):
    """
    Resolves a single assignment for result set

    Params:
    assig: dict from the raw result set
    """
    data = get_assignment_json(
        path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), assig["id"] + ".json")
    )
    if not data:
        return []
    for var in data["variations"]:
        if var["variation_id"] == assig["variationID"]:
            data["variations"] = [var]

    return data

def resolve_assignment_set(_set: dict) -> list[dict] | list[list[dict]]:
    """
    Resolves assignment set to get full assignment data

    Params:
    _set: an assignment set to resolve as dict
    """

    if _set["type"] == "week":
        new_set = []
        for assig in _set["assignments"]:
            new_set.append(_resolve_assignment(assig))
    else:
        new_set = []
        for week in _set["weeks"]:
            new_week = []
            for assig in week:
                new_week.append(_resolve_assignment(assig))
            new_set.append(new_week)

    return new_set


def resolve_set_header(header:str) -> dict:
    """
    Get result set based on header
    """

    set_id = int(header.split(" - ")[0])
    return get_result_sets(set_id)


def delete_assignment_set(s, a, u:tuple[int, int|str, int|str]):
    """
    Delete assignment set from set list

    Params:
    set_id: set to remove
    window_id: window to close after removal
    """

    set_id = u[0]
    window_id = u[1]
    popup_id = u[2]

    data = get_saved_assignment_sets()

    for i, _sets in enumerate(data["sets"]):
        if _sets["id"] == set_id:
            del data["sets"][i]
            break

    save_sets_disk(data)
    close_window(popup_id)
    configure_item(UI_ITEM_TAGS["LISTBOX"], items=get_result_sets())
    close_window(window_id)


def delete_files(file_paths:list | str) -> bool:
    """
    Delete files based on path.

    Params:
    file_path: file(s) to remove. Can be either one path or a list of paths
    """

    if isinstance(file_paths, list):
        for _path in file_paths:
            try:
                remove(_path)
            except OSError:
                logging.exception("Error removing files!")
                return False
    else:
        try:
            remove(file_paths)
        except OSError:
            logging.exception("Error removing files!")
            return False
    return True


def check_new_features(data:dict, _type:str) -> None:
    """
    Checks if new features exist in data. If not, the function will do necessary things to fix it.

    Params: 
    data: data to check
    type: what feature to check
    """

    if _type == "image":
        if "images" not in data.keys():
            data["images"] = []
