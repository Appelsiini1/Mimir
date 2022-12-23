"""
Mímir Data Handlers
Functions for loading and saving exercise data
"""

import json
import logging
from os import path

from constants import ENV
from custom_errors import ConflictingAssignmentID


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

def get_assignment_code(data_path:str, ID:str):
    """
    Read code file and return its contents, excluding the ID line. Note that function checks whether the assignment ID
    matches the ID given. Raises an exception if they do not match.

    Params:
    data_path: Path to the code file
    ID: ID of the assignment
    """

    try:
        with open(data_path, "r", encoding="UTF-8") as code_file:
            code = code_file.read()
            if not code.startswith(ID):
                raise ConflictingAssignmentID
            code = code.strip(ID)
            return code
    except OSError:
        logging.exception("Unable to read code file!")
        return None
