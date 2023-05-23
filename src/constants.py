"""Mímir constants"""

# pylint: disable=import-error, missing-function-docstring
from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG, INFO
from sys import exit as sysexit
import json

from dearpygui.dearpygui import generate_uuid
from src.common import resource_path
from src.const_class import COURSE_PATH, RECENTS_LIST, IX, LANG

def _get_texts():
    try:
        with open(resource_path("resource/texts.json"), "r", encoding="utf-8") as _file:
            _data = _file.read()
            _display_texts = json.loads(_data)
    except OSError:
        sysexit(1)
    return _display_texts

def _get_filetypes():
    try:
        with open(resource_path("resource/filetypes.json"), "r", encoding="utf-8") as _file:
            _data = json.loads(_file.read())
            _data["any"][0][0] = DISPLAY_TEXTS["file_any"][LANGUAGE.get()] # not a great solution
    except OSError:
        sysexit(1)
    return _data

#################################
# Version

VERSION = "0.3.1"

#################################
# Environment spesific constants
# OS = operating system name
# PROGRAM_DATA = path to data/cache folder
ENV = {}
if OSname == "nt":
    ENV["OS"] = "nt"
    ENV["PROGRAM_DATA"] = join(getenv("APPDATA"), "MimirData")
elif OSname == "POSIX":
    ENV["OS"] = "POSIX"
    ENV["PROGRAM_DATA"] = join(getenv("HOME"), "MimirData")

################################
# UI constants

DISPLAY_TEXTS = _get_texts()
LANGUAGE = LANG()

#################################
# Unique UI item tags

_GENERAL_KEY_LIST = [
    "total_index",
    "PREVIOUS_PART_CHECKBOX",
    "PREVIOUS_PART_COMBOBOX",
    "CODE_LANGUAGE_COMBOBOX",
    "INST_LANGUAGE_COMBOBOX",
    "VARIATION_GROUP",
    "MAIN_WINDOW",
    "ADD_ASSIGNMENT_WINDOW",
    "OPEN_ADD_ASSINGMENT_BUTTON",
    "WARNING_POPUP_ADD_ASSIG_WINDOW",
    "ASSIGNMENT_TITLE",
    "ASSIGNMENT_LECTURE_WEEK",
    "ASSIGNMENT_NO",
    "ASSIGNMENT_TAGS",
    "COURSE_ID",
    "COURSE_TITLE",
    "COURSE_WEEKS",

]
VARIATION_KEY_LIST = [
    "INSTRUCTIONS",
    "USED_IN",
    "EXAMPLE_LISTBOX",
    "CODEFILE_LISTBOX",
    "DATAFILE_LISTBOX"
]

EXAMPLE_RUN_KEY_LIST = [
    "INPUTS",
    "CMD_INPUTS",
    "OUTPUT",
    "OUTPUT_FILES",
    "GEN_EX"
]

UI_ITEM_TAGS = {'{}'.format(i):generate_uuid() for i in _GENERAL_KEY_LIST}

#################################
# Misc constants
OPEN_IX = None
OPEN_COURSE_PATH = COURSE_PATH()
COURSE_INFO = {
    "course_title": None,
    "course_id": None,
    "course_weeks": None
}
FILETYPES = _get_filetypes()
LOG_LEVEL = DEBUG
RECENTS = RECENTS_LIST()
