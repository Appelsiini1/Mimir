"""
Mímir Data Getters

Functions that get data from somewhere
"""

# pylint: disable=consider-using-f-string, invalid-name, import-error, unused-argument

import logging
import json

from os import path
from dearpygui.dearpygui import get_value

from src.constants import (
    ENV,
    RECENTS,
    OPEN_IX,
    OPEN_COURSE_PATH,
    COURSE_INFO,
    DISPLAY_TEXTS,
    LANGUAGE,
    WEEK_DATA,
)
from src.common import resource_path


def get_assignment_json(json_path: str) -> dict | None:
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


def get_assignment_code(data_path: str, a_id:str) -> str | None:
    """
    Read code file and return its contents, excluding the ID line. Note that function
    checks whether the assignment ID matches the ID given. Raises an exception if
    they do not match.

    Params:
    data_path: Path to the code file
    a_id: ID of the assignment
    """

    try:
        full_path = path.join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), a_id, data_path)
        with open(full_path, "r", encoding="UTF-8") as code_file:
            code = code_file.read()
            return code
    except OSError:
        logging.exception("Unable to read code file!")
        return None


def read_datafile(filename: str, a_id:str) -> str | None:
    """
    Read a data file of given path and return its data. Returns None on error.
    """
    try:
        full_path = path.join(OPEN_COURSE_PATH.get_subdir(assignment_data=True), a_id, filename)
        with open(full_path, "r", encoding="UTF-8") as _file:
            data = _file.read()
            return data
    except OSError:
        logging.exception("Unable to read code file!")
        return None


def get_texdoc_settings() -> dict:
    """
    Gets TeX document settings from file. Returns a dict.
    """
    _path = path.join(ENV["PROGRAM_DATA"], "document_settings.json")
    with open(_path, "r", encoding="UTF-8") as _file:
        _json = json.loads(_file.read())

    return _json


def get_empty_assignment() -> dict:
    """
    Returns an empty instance of an assignment dictionary
    """
    empty = {}
    empty["title"] = ""
    empty["exp_lecture"] = 0
    empty["exp_assignment_no"] = ""
    empty["level"] = 0
    empty["tags"] = ""
    empty["next"] = []
    empty["previous"] = []
    empty["code_language"] = ""
    empty["instruction_language"] = ""
    empty["variations"] = []

    return empty


def get_empty_variation() -> dict:
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


def get_empty_example_run() -> dict:
    """
    Returns an empty instace of an example run dictionary
    """

    empty = {}
    empty["generate"] = False
    empty["inputs"] = []
    empty["cmd_inputs"] = []
    empty["output"] = ""
    empty["outputfiles"] = []

    return empty


def get_empty_week() -> dict:
    """
    Return a dictionary that contains the correct keys for a week object with no values.
    """
    empty = {}
    empty["title"] = ""
    empty["lecture_no"] = 0
    empty["topics"] = []
    empty["instructions"] = ""
    empty["assignment_count"] = 0
    empty["tags"] = []

    return empty


def get_recents(**args) -> None:
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


def get_week_data() -> dict | None:
    """
    Get week data from json, or return a dict with only course info filled in.
    """

    if WEEK_DATA.get():
        return WEEK_DATA.get()
    weeks = None
    f_path = path.join(OPEN_COURSE_PATH.get(), "weeks.json")

    try:
        with open(f_path, "r", encoding="utf-8") as f:
            data = f.read()
            weeks = json.loads(data)
            WEEK_DATA.set(weeks)
    except FileNotFoundError:
        weeks = {
            "course_id": COURSE_INFO["course_id"],
            "course_title": COURSE_INFO["course_title"],
            "lectures": [],
        }
        WEEK_DATA.set(weeks)
    except OSError:
        logging.exception("Error when reading week data.")

    logging.debug("Week data is: %s", weeks)
    return weeks


def get_pos_convert() -> dict | None:
    """
    Get the 'used in' position conversion table
    """

    _file = resource_path("resource/pos_convert_default.json")
    try:
        with open(_file, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
    except OSError:
        logging.exception("Error in reading position conversion defaults!")
        return None
    return data


def get_header_page(pagenum: int, data: list, perpage=15, week=False) -> list:
    """
    Get a page of assignment headers

    Params:
    pagenum: the number of the page to return
    data: where to extract pages from
    perpage: how many to show per page, default is 20
    """

    if pagenum == 1:
        start = 0
        stop = perpage - 1
    else:
        start = (pagenum - 1) * perpage
        stop = (perpage * pagenum) - 1

    headers = []
    if not week:
        _slice = data[start:stop]
        for item in _slice:
            header = ""
            header += (
                DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()]
                + item["position"].split(";")[0]
            )
            header += DISPLAY_TEXTS["tex_assignment_letter"][LANGUAGE.get()] + "("
            header += item["position"].split(";")[1] + ")"
            header += " - " + item["title"]
            headers.append(header)
    else:
        data.sort(key=lambda a: a["lecture_no"])
        _slice = data[start:stop]
        for item in _slice:
            header = ""
            header += str(item["lecture_no"])
            header += " - "
            if not item["title"]:
                header += DISPLAY_TEXTS["tex_lecture_letter"][LANGUAGE.get()] + str(
                    item["lecture_no"]
                )
                header += " " + DISPLAY_TEXTS["assignments"][LANGUAGE.get()]
            else:
                header += item["title"]
            headers.append(header)

    return headers


def get_variation_index(vars:list, _id:str) -> int|None:
    """
    Return the position of the variation that has the letter as its ID.

    Params:
    vars: list of variations
    letter: the letter to search
    """
    if not vars:
        return -2
    
    letter = get_value(_id).split(" ")[1]
    for i, var in enumerate(vars):
        if var["variation_id"] == letter:
            return i
    return None
