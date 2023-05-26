"""
Mímir Data Handlers

Functions for loading and saving exercise data
"""

# pylint: disable=import-error, unused-argument
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
    INDEX_SCHEMA
)
from src.custom_errors import IndexExistsError, IndexNotOpenError

# pylint: disable=consider-using-f-string
# pylint: disable=invalid-name


def data_path_handler(directory_path: str):
    """
    Takes a general path to the cache directory and returns a dictionary of paths
    to the files in that directory, separated into 'general', 'metadata' and 'assignment'.
    Individual files can be accessed via assignment ID keys.
    For example:
    files['assignment']['L01T1']

    Params:
    directory_path: A path to the root DATA directory in cache
    """


def get_assignment_json(json_path: str) -> dict|None:
    """
    Read JSON and use the data to get example code from its file.
    Returns a dictionary with all the assignment data or None if an exception
    is raised.

    Params:
    json_path: path to the json file to be read
    """

    try:
        with open(json_path, "r", encoding="UTF-8") as json_file:
            raw_data = json_file.read()
            json_data = json.loads(raw_data)
    except OSError:
        logging.exception("Unable to read JSON file!")
        return None
    else:
        return json_data


def get_assignment_code(data_path: str, a_id: str):
    """
    Read code file and return its contents, excluding the ID line. Note that function
    checks whether the assignment ID matches the ID given. Raises an exception if
    they do not match.

    Params:
    data_path: Path to the code file
    a_id: ID of the assignment
    """

    try:
        with open(data_path, "r", encoding="UTF-8") as code_file:
            code = code_file.read()
            # TODO uncomment
            # if not code.startswith(a_id):
            #    raise ConflictingAssignmentID
            code = code.strip(a_id)
            return code
    except OSError:
        logging.exception("Unable to read code file!")
        return None


def read_datafile(filename: str):
    try:
        with open(filename, "r", encoding="UTF-8") as _file:
            data = _file.read()
            return data
    except OSError:
        logging.exception("Unable to read code file!")
        return None


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
    json_path = path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"]+".json")
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


def get_expanding_assignments():
    """
    Returns a list of assignment objects that have 'is_expanding' argument set to TRUE.

    Params:
    a_index: The assignment index from where to search
    """


def update_index(data:dict):
    """
    Updates the index with the data from the updated assignment.

    Params:
    data: assignment to update
    """

    ix = OPEN_IX.get()

    positions = f"{data['exp_lecture']:02d};"
    positions += ",".join(data["exp_assignment_no"])
    tags = ",".join(data["tags"])
    json_path = path.join(OPEN_COURSE_PATH.get_subdir(metadata=True), data["assignment_id"]+".json")
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


def get_texdoc_settings():
    """
    Gets TeX document settings from file. Returns a dict.
    """
    _path = path.join(ENV["PROGRAM_DATA"], "document_settings.json")
    with open(_path, "r", encoding="UTF-8") as _file:
        _json = json.loads(_file.read())

    return _json


def format_general_json(data: dict, lecture_no: int):
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
    for i, ex_run in enumerate(variation["example_runs"]):
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
        logging.info("Successfully saved assignment %s to file and index.", assignment["assignment_id"])
    except OSError:
        # TODO Popup for user
        logging.exception("Error while saving assignment data!")


def get_empty_assignment():
    """
    Returns an empty instance of an assignment dictionary
    """
    empty = {}
    empty["title"] = ""
    empty["tags"] = ""
    empty["exp_lecture"] = 0
    empty["exp_assignment_no"] = ""
    empty["next, last"] = ""
    empty["code_language"] = ""
    empty["instruction_language"] = ""
    empty["variations"] = []

    return empty


def get_empty_variation():
    """
    Returns an empty instance of an assignment variation dictionary
    """

    empty = {}
    empty["variation_id"] = ""
    empty["instructions"] = ""
    empty["example_runs"] = []
    empty["codefiles"] = []
    empty["datafiles"] = []
    empty["used_in"] = []

    return empty


def get_empty_example_run():
    """
    Returns an empty instace of an example run dictionary
    """

    empty = {}
    empty["generate"] = None
    empty["inputs"] = []
    empty["cmd_inputs"] = []
    empty["output"] = []
    empty["outputfiles"] = []

    return empty


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
    if not OPEN_COURSE_PATH in rec:
        if len(rec) < 5:
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
    logging.info("Recent courses set as: %s", rec)


def get_recents(**args):
    """
    Get a list of recent courses
    """
    f_path = path.join(ENV["PROGRAM_DATA"], "recents.txt")
    if path.exists(f_path):
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                paths = f.read().split("\n")
                for i, p in enumerate(paths):
                    if p == "":
                        paths.pop(i)
                RECENTS.set(paths)
        except OSError:
            logging.exception("Error occured while getting recent courses.")
    logging.info("Set recent course list as: %s", RECENTS.get())


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
        configure_item(
            UI_ITEM_TAGS["total_index"], default_value=get_number_of_docs()
        )

def get_all_indexed_assignments() -> list:
    """Returns a list of all the documents in the index."""

    ix = OPEN_IX.get()

    docs = []
    with ix.searcher() as srcr:
        _all = srcr.documents()
        docs = list(_all)

    return docs

def get_number_of_docs() -> int:
    """Returns the number of documents in the course index."""

    ix = OPEN_IX.get()

    if ix:
        with ix.searcher() as sr:
            no = sr.doc_count()
        return no
    return 0

def close_index() -> None:
    """Closes the open indexes."""

    ix = OPEN_IX.get()
    if ix:
        ix.close()

    logging.info("Indexes closed.")
