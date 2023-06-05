"""
Mímir Data Handlers

Functions for processing data
"""

# pylint: disable=import-error, unused-argument, consider-using-f-string, invalid-name
import json
import logging
from os import path, mkdir, getcwd
from ntpath import split, basename
from tkinter.filedialog import askdirectory
from hashlib import sha256
from shutil import copy2

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
)
from src.custom_errors import IndexExistsError, IndexNotOpenError
from src.data_getters import (
    get_pos_convert,
    read_datafile,
    get_assignment_code,
    get_week_data,
    get_number_of_docs,
    get_assignment_json,
)

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
    except OSError:
        logging.exception("Could not open index file.")
    else:
        OPEN_IX.set(ix)
        logging.debug("Index set.")


def add_assignment_to_index(data: dict, expanding:bool):
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
    json_path = path.join(
        OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"] + ".json"
    )

    writer = ix.writer()
    writer.add_document(
        a_id=data["assignment_id"],
        position=positions,
        tags=tags,
        title=data["title"],
        json_path=json_path,
        is_expanding=expanding,
    )
    writer.commit()


def _save_course_file():
    """
    Save course metadata to file
    """
    f_path = path.join(OPEN_COURSE_PATH.get(), "course_info.mcif")
    with open(f_path, "w", encoding="utf-8") as f:
        to_write = json.dumps(COURSE_INFO, indent=4)
        f.write(to_write)


def save_course_info(**args):
    """
    Function to save course information from main window
    """

    new = 0
    if COURSE_INFO["course_id"] is None:
        new = 1
    COURSE_INFO["course_title"] = get_value(UI_ITEM_TAGS["COURSE_TITLE"])
    COURSE_INFO["course_id"] = get_value(UI_ITEM_TAGS["COURSE_ID"])
    COURSE_INFO["course_weeks"] = get_value(UI_ITEM_TAGS["COURSE_WEEKS"])

    if not OPEN_COURSE_PATH.get():
        ask_course_dir()
    _save_course_file()

    if new:
        create_index()


def update_index(data: dict, expanding:bool):
    """
    Updates the index with the data from the updated assignment.

    Params:
    data: assignment to update
    expanding: bool whether the assignment is expanding
    """

    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']:02d};"
    positions += ",".join([str(item) for item in data["exp_assignment_no"]])
    tags = ",".join(data["tags"])
    json_path = path.join(
        OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"] + ".json"
    )

    writer = ix.writer()
    writer.update_document(
        a_id=data["assignment_id"],
        position=positions,
        tags=tags,
        title=data["title"],
        json_path=json_path,
        is_expanding=expanding,
    )
    writer.commit()


def format_metadata_json(data: dict):
    """
    Add data of the files in the assignment to the dictionary and return the new one.

    Params:
    data: the dictionary containing original assignment data. Note, expects there to be only one variation.
    """
    new = {}
    new["title"] = data["title"]
    new["code_lang"] = data["code_language"]
    variation = None
    variation = data["variations"][0]
    new["instructions"] = variation["instructions"]
    example_runs = []
    for i, _ in enumerate(variation["example_runs"]):
        n = {
            "inputs": variation["example_runs"][i]["inputs"],
            "output": variation["example_runs"][i]["output"],
            "CMD": variation["example_runs"][i]["cmd_inputs"],
            "outputfiles": [
                {
                    "filename": variation["example_runs"][i]["outputfiles"][j],
                    "data": read_datafile(
                        variation["example_runs"][i]["outputfiles"][j],
                        data["assignment_id"],
                    ),
                }
                for j in variation["example_runs"][i]["outputfiles"]
            ]
            if variation["example_runs"][i]["outputfiles"]
            else [],
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
    return new


def save_assignment_data(assignment: dict, new: bool):
    """
    Saves assignment to database
    """

    if new:
        assignment["course_id"] = COURSE_INFO["course_id"]
        assignment["course_title"] = COURSE_INFO["course_title"]
        _bytes = json.dumps(assignment).encode()
        _hash = sha256(usedforsecurity=False)
        _hash.update(_bytes)
        _hex = _hash.hexdigest()
        assignment["assignment_id"] = _hex

        for last in assignment["previous"]:
            prev = get_assignment_json(
                path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), last + ".json")
            )
            if not prev["next"]:
                prev["next"] = [assignment["assignment_id"]]
            else:
                if assignment["assignment_id"] not in prev["next"]:
                    prev["next"].append(assignment["assignment_id"])

        _filename = _hex + ".json"

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
        _json = json.dumps(assignment, indent=4, ensure_ascii=False)
        add_assignment_to_index(assignment, expanding)
    else:
        assignment["course_id"] = COURSE_INFO["course_id"]
        assignment["course_title"] = COURSE_INFO["course_title"]
        basepath = OPEN_COURSE_PATH.get_subdir(assignment_data=True)
        datapath = path.join(basepath, assignment["assignment_id"])

        _filename = assignment["assignment_id"] + ".json"
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
        _json = json.dumps(assignment, indent=4, ensure_ascii=False)
        update_index(assignment, expanding)

    _filepath = path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), _filename)
    if not path.exists(OPEN_COURSE_PATH.get_subdir(metadata=True)):
        mkdir(OPEN_COURSE_PATH.get_subdir(metadata=True))

    try:
        with open(_filepath, "w", encoding="utf-8") as _file:
            _file.write(_json)
        logging.info(
            "Successfully saved assignment %s to file and index.",
            assignment["assignment_id"],
        )
    except OSError:
        # TODO Popup for user
        logging.exception("Error while saving assignment data!")


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
            ind = rec.index(OPEN_COURSE_PATH.get())
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
    finally:
        _file = path.join(OPEN_COURSE_PATH.get(), "course_info.mcif")

    try:
        with open(_file, "r", encoding="utf-8") as f:
            _data = f.read()
    except OSError:
        logging.exception("Error in reading course info!")
    else:
        _json = json.loads(_data)
        for key in _json.keys():
            COURSE_INFO[key] = _json[key]
        open_index()
        configure_item(
            UI_ITEM_TAGS["COURSE_ID"], default_value=COURSE_INFO["course_id"]
        )
        configure_item(
            UI_ITEM_TAGS["COURSE_TITLE"], default_value=COURSE_INFO["course_title"]
        )
        configure_item(
            UI_ITEM_TAGS["COURSE_WEEKS"], default_value=COURSE_INFO["course_weeks"]
        )
        configure_item(UI_ITEM_TAGS["total_index"], default_value=get_number_of_docs())


def close_index() -> None:
    """Closes the open indexes."""

    ix = OPEN_IX.get()
    if ix:
        ix.close()

    logging.info("Indexes closed.")


def save_week_data(week, new) -> None:
    """
    Save week data to file.
    """
    parent = get_week_data()

    if new:
        parent["lectures"].append(week)
    else:
        for i, item in enumerate(parent["lectures"]):
            if item["lecture_no"] == week["lecture_no"]:
                parent["lectures"][i] = week
                break

    f_path = path.join(OPEN_COURSE_PATH.get(), "weeks.json")
    try:
        with open(f_path, "w", encoding="utf-8") as f:
            _json = json.dumps(parent, indent=4, ensure_ascii=False)
            f.write(_json)
            WEEK_DATA.set(parent)
    except OSError:
        logging.exception("Error in saving week JSON.")
    logging.debug("Week data saved: %s", _json)


def year_conversion(data: list, encode: bool) -> list:
    """
    Converts the 'used in' value to number from text or vice versa.
    """
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
        return
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


def del_prev(s, a, u: tuple[dict, str]):
    """
    Delete previous assignment from list
    """

    var = u[0]
    to_del = u[1]
    if not isinstance(to_del, int):
        return

    ind = var["previous"].index(to_del)
    var["previous"].pop(ind)

    prev = get_assignment_json(path.join(OPEN_COURSE_PATH, to_del + ".json"))

    ind = prev["next"].index(to_del)
    prev["next"].pop(ind)
    save_assignment_data(prev, False)


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
    week = u[3]["lectures"][index_n]["lecture_no"]
    assig_index = None
    for i, item in enumerate(_set[index_n]):
        t = ""
        t += DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()] + str(week)
        t += DISPLAY_TEXTS["tex_assignment_letter"][LANGUAGE.get()] + str(index_n)
        t += " - " + item["title"]
        t += (
            " - "
            + DISPLAY_TEXTS["ui_variation"][LANGUAGE.get()]
            + item["variations"][0]["variation_id"]
        )
        if t == value:
            assig_index = i
    _set[index_n].pop(assig_index)
    headers = gen_result_headers(_set[index_n], week)
    configure_item(listbox_id, items=headers)


def move_up(s, a, u: tuple[int | str, int, list]):
    """
    Move result up in the result set.
    """


def move_down(s, a, u: tuple[int | str, int, list]):
    """
    Move result down in the result set.
    """
