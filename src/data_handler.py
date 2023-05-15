"""
Mímir Data Handlers

Functions for loading and saving exercise data
"""

# pylint: disable=import-error
import json
import logging
from os import path, mkdir
from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, BOOLEAN, STORED
from dearpygui.dearpygui import get_values

from src.constants import ENV, DISPLAY_TEXTS, LANGUAGE, GENERAL_ASSIGNMENT_TAGS, OPEN_IX, COURSE_INFO, OPEN_COURSE_PATH
from src.custom_errors import ConflictingAssignmentID, IndexExistsError, IndexNotOpenError

# pylint: disable=consider-using-f-string
# pylint: disable=invalid-name


class Assignment:
    """
    Class to hold basic assignment data.

    Params:
    a_id:   Assignment ID. Should include variation ID too.
    title:  Assignment title
    tags:   List of tags the assignment has
    lecture: A tuple containing the lecture number and a list of positions
                where the assignment can be assinged to
    paths:  List containing the json and code path
    used_in: A list of dates when the assignment has been previously used in
    exp:    A boolean whether the assignment is expanding or not. Defaults to False.
    """

    def __init__(self, a_id, title, tags, lecture, jsonpath, used_in, exp=False):
        self.a_id = a_id
        self.title = title
        self.tags = tags
        self.lecture = lecture[0]
        self.a_pos = lecture[1]
        self.json_path = jsonpath
        self.used_in = used_in
        self.is_expanding = exp


class FILEPATHCARRIER:
    """
    A class to carry extension information to file browser and bring back
    the selected files as paths
    """

    def __init__(self) -> None:
        self.filepaths = []
        self.extensions = []

    def c_files(self):
        """Set extensions to C-code files"""
        self.extensions = [[DISPLAY_TEXTS["file_c"][LANGUAGE], [".c", ".h"]]]

    def text_files(self):
        """Set extensions to text files"""
        self.extensions = [[DISPLAY_TEXTS["file_text"][LANGUAGE], [".txt"]]]

    def any_files(self):
        """Set extensions to any"""
        self.extensions = [[DISPLAY_TEXTS["file_any"][LANGUAGE], [".*"]]]

    def json_files(self):
        """Set extensions to json"""
        self.extensions = [[DISPLAY_TEXTS["file_json"][LANGUAGE], [".json"]]]


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


def get_assignment_json(json_path: str):
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


def create_index(ix_path: str, name: str, force=False):
    """
    Creates an assignment index and its schema that are used to store paths to all available
    assingments.
    Sets the created index as a global constant.

    Params:
    path: A path where to create the index
    name: Name of the created index
    force: Force the creation of the index if it already exists.
    """

    data_path = path.join(ix_path, "data")

    schema = Schema(
        a_id=ID(stored=True, unique=True),
        position=KEYWORD(stored=True, commas=True),
        tags=KEYWORD(stored=True, commas=True, lowercase=True, field_boost=2.0),
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        json_path=STORED,
        is_expanding=BOOLEAN,
        used_in=KEYWORD(stored=True, commas=True),
        mtimes=ID,
    )

    if not path.exists(data_path):
        mkdir(data_path)

    if index.exists_in(ix_path, name) and not force:
        raise IndexExistsError("Index '%s' already exists in '%s'" % (name, ix_path))

    try:
        ix = index.create_in(ix_path, schema, name)
    except OSError:
        logging.exception("Unable to save index file.")
        return None

    OPEN_IX = ix


def open_index(ix_path: str, name: str):
    """
    Opens a previously created assignment index. Sets the opened index as a global constant.

    Params:
    path: Path to the index
    name: Name of the index
    """

    try:
        ix = index.open_dir(ix_path, name)
    except OSError:
        logging.exception("Could not open index file.")
        return None

    OPEN_IX = ix


def add_assignment_to_index(data: Assignment):
    """
    Adds given assignements to the index currently open.

    Params:
    data: an Assignment object containing assignment data
    """

    if not OPEN_IX:
        raise IndexNotOpenError
    ix = OPEN_IX

    positions = ",".join(f"L{data.lecture:02d}T{i:02d}" for i in data.a_pos)
    tags = ",".join(data.tags)
    used_in = ",".join(data.used_in)

    try:
        mtime = path.getmtime(data.json_path)
    except OSError:
        logging.exception(
            "Could not get modification time(s) for assignment data file(s)"
        )
        return False

    writer = ix.writer()

    writer.add_document(
        a_id=data.a_id,
        position=positions,
        tags=tags,
        title=data.title,
        json_path=data.json_path,
        is_expanding=data.is_expanding,
        used_in=used_in,
        mtimes=mtime,
    )
    writer.commit()
    return True

def _save_course_file():
    """
    Save course metadata to file
    """
    f_path = path.join(OPEN_COURSE_PATH, COURSE_INFO["course_id"])
    with open(f_path, "w", encoding="utf-8") as f:
        to_write = json.dumps(COURSE_INFO)
        f.write(to_write)


def save_course_info(s, a, u:list):
    """
    Function to save course information from main window

    Params:
    s: not in use
    a: not in use
    u: list of item tags
    """
    if OPEN_COURSE_PATH:
        values = get_input_values(None, None, u)
        COURSE_INFO["course_title"] = values[1]
        COURSE_INFO["course_id"] = values[0]
        COURSE_INFO["course_weeks"] = values[2]

        _save_course_file()


def get_expanding_assignments(a_ix: index.FileIndex):
    """
    Returns a list of assignment objects that have 'is_expanding' argument set to TRUE.

    Params:
    a_index: The assignment index from where to search
    """


def update_index(a_ix: index.FileIndex):
    """
    Updates the index if the files have changed. Uses modification time of the files.
    If the files are deleted, returns a list of them. If no files were found to be deleted,
    return an empty list.

    Params:
    a_ix: FileIndex object that has the index to update.
    """

    deleted = []
    to_index = []

    with a_ix.searcher() as searcher:

        for fields in searcher.all_stored_fields():
            ind_json_path = fields["json_path"]

            if not path.exists(ind_json_path):
                deleted.append(fields["a_id"])
            else:
                ind_times = fields["mtimes"]
                ind_json_time = ind_times.split(",")[0]
                json_time = path.getmtime(ind_json_path)

                if json_time > ind_json_time:
                    to_index.append(fields["a_id"])
    # TODO Add document updating logic


def get_texdoc_settings():
    """
    Gets TeX document settings from file. Returns a dict.
    """
    _path = path.join(ENV["PROGRAM_DATA"], "document_settings.json")
    with open(_path, "r", encoding="UTF-8") as _file:
        _json = json.loads(_file.read())

    return _json


def create_course(sender, user_data, app_data):
    """
    Initializes a course.
    """
    pass


def format_general_json(data: dict, lecture_no: int):
    general = {}
    general["course_id"] = data["course_id"]
    general["course_name"] = data["course_name"]
    general["lecture"] = lecture_no
    general["topics"] = data["lectures"][lecture_no-1]["topics"]
    general["instructions"] = data["lectures"][lecture_no-1]["instructions"]
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
            "inputs": variation["example_runs"][i][
                "inputs"
            ],
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

def save_assignment(s, a, u):
    general_values = get_input_values(None, None, GENERAL_ASSIGNMENT_TAGS)



def get_input_values(s, a, u:list):
    """
    Gets input values and returns them as a list.

    Params:
    u: A list of UUIDs to get inputs from
    """
    
    values = get_values(u)
    return values

def get_empty_assignment():
    """
    Returns an empty instance of an assignment dictionary
    """
    empty = {}
    empty["title"] = ""
    empty["tags"] = ""
    empty["exp_lecture"] = ""
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
