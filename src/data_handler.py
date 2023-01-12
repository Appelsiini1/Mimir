"""
Mímir Data Handlers
Functions for loading and saving exercise data
"""

import json
import logging
import sys
from os import path, mkdir
from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, BOOLEAN, STORED

from constants import ENV
from custom_errors import ConflictingAssignmentID, IndexExistsError

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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # pylint: disable=protected-access, no-member
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


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
            if not code.startswith(a_id):
                raise ConflictingAssignmentID
            code = code.strip(a_id)
            return code
    except OSError:
        logging.exception("Unable to read code file!")
        return None


def create_index(ix_path: str, name: str, force=False):
    """
    Creates an assignment index and its schema that are used to store paths to all available
    assingments.
    Returns an index object.

    Params:
    path: A path where to create the index
    name: Name of the created index
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

    return ix


def open_index(ix_path: str, name: str):
    """
    Opens a previously created assignment index. Returns an index object.

    Params:
    path: Path to the index
    name: Name of the index
    """

    try:
        ix = index.open_dir(ix_path, name)
    except OSError:
        logging.exception("Could not open index file.")
        return None

    return ix


def add_assignment_to_index(ix: index.FileIndex, data: Assignment):
    """
    Adds given assignements to index.

    Params:
    ix: FileIndex object where to index the assignment to
    data: an Assignment object containing assignment data
    """

    positions = ",".join(f"L{data.lecture:02d}T{i:02d}" for i in data.a_pos)
    tags = ",".join(data.tags)
    used_in = ",".join(data.used_in)

    try:
        mtime = path.getmtime(data.json_path)
    except OSError:
        logging.exception("Could not get modification time(s) for assignment data file(s)")
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
        mtimes=mtime
    )
    writer.commit()
    return True


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
            ind_json_path = fields['json_path']

            if not path.exists(ind_json_path):
                deleted.append(fields['a_id'])
            else:
                ind_times = fields['mtimes']
                ind_json_time = ind_times.split(",")[0]
                json_time = path.getmtime(ind_json_path)

                if json_time > ind_json_time:
                    to_index.append(fields['a_id'])
    #TODO Add document updating logic
