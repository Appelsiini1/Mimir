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

from whoosh import index
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
)
from src.custom_errors import IndexExistsError, IndexNotOpenError
from src.data_getters import get_pos_convert, read_datafile, get_assignment_code, get_week_data, get_number_of_docs

########################################

def create_index(force=False, **args):
    """
    Creates an assignment index from schema that is used to store paths to all available
    assingments.
    Sets the created index as a global constant.

    Params:
    force: Force the creation of the index if it already exists.
    """

    ix_path = OPEN_COURSE_PATH.get()
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

    ix_path = OPEN_COURSE_PATH.get()
    name = COURSE_INFO["course_id"]
    try:
        ix = index.open_dir(ix_path, name)
    except OSError:
        logging.exception("Could not open index file.")
    else:
        OPEN_IX.set(ix)
        logging.debug("Index set.")


def add_assignment_to_index(data: dict):
    """
    Adds given assignements to the index currently open.

    Params:
    data: a dictionary containing assignment data
    """

    if not OPEN_IX.get():
        raise IndexNotOpenError
    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']};"
    positions += ",".join(data["exp_assignment_no"])
    tags = ",".join(data["tags"])
    json_path = path.join(
        OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"] + ".json"
    )
    try:
        expanding = bool(data["next, last"][0] or data["next, last"][1])
    except IndexError:
        expanding = False

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
        to_write = json.dumps(COURSE_INFO)
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


def update_index(data: dict):
    """
    Updates the index with the data from the updated assignment.

    Params:
    data: assignment to update
    """

    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']:02d};"
    positions += ",".join(data["exp_assignment_no"])
    tags = ",".join(data["tags"])
    json_path = path.join(
        OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"] + ".json"
    )
    expanding = bool(data["next, last"][0] or data["next, last"][1])

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


def format_week_json(data: dict, lecture_no: int):
    general = {}
    general["course_id"] = data["course_id"]
    general["course_name"] = data["course_name"]
    general["lecture"] = lecture_no
    general["topics"] = data["lectures"][lecture_no - 1]["topics"]
    general["instructions"] = data["lectures"][lecture_no - 1]["instructions"]
    return general


def format_metadata_json(data: dict):
    # TODO Format better later
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
                # TODO Add handling for multiple output files
                {
                    "filename": variation["example_runs"][i]["outputfiles"][0],
                    "data": read_datafile(
                        variation["example_runs"][i]["outputfiles"][0]
                    ),
                }
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
                    "data": read_datafile(df),
                }
            )
    new["example_codes"] = []
    for cf in variation["codefiles"]:
        new["example_codes"].append(
            {
                "filename": cf,
                "code": get_assignment_code(
                    cf, data["assignment_id"] + variation["variation_id"]
                ),
            }
        )
    return new


def save_assignment_data(assignment, new):
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

        _json = json.dumps(assignment, indent=4, ensure_ascii=False)
        _filename = _hex + ".json"
        add_assignment_to_index(assignment)
    else:
        assignment["course_id"] = COURSE_INFO["course_id"]
        assignment["course_title"] = COURSE_INFO["course_title"]

        _filename = assignment["assignment_id"] + ".json"
        _json = json.dumps(assignment, indent=4, ensure_ascii=False)
        update_index(assignment)

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
    except OSError:
        logging.exception("Error in saving week JSON.")
    logging.debug("Week data saved: %s", _json)


def year_conversion(data: list, encode:bool) -> list:
    """
    Converts the 'used in' value to number from text or vice versa.
    """
    if not data:
        raise ValueError("Data cannot be empty")

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
