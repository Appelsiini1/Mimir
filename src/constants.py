"""Mímir constants"""

# pylint: disable=import-error
from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG, INFO
from sys import exit as sysexit
import json

from dearpygui.dearpygui import generate_uuid
from src.common import resource_path

def _get_texts():
    try:
        with open(resource_path("resource/texts.json"), "r", encoding="utf-8") as _file:
            _data = _file.read()
            _display_texts = json.loads(_data)
    except OSError:
        sysexit(1)
    return _display_texts

#################################
# Environment spesific variables
# OS = operating system name
# PROGRAM_DATA = path to data/cache folder
ENV = {}
if OSname == "nt":
    ENV["OS"] = "nt"
    ENV["PROGRAM_DATA"] = join(getenv("APPDATA"), "MimirData")
elif OSname == "POSIX":
    ENV["OS"] = "POSIX"
    ENV["PROGRAM_DATA"] = join(getenv("HOME"), "MimirData")

DISPLAY_TEXTS = _get_texts()
LANGUAGE = "FI"

VERSION = "0.2.13"
LOG_LEVEL = DEBUG

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
    "USED_IN"
    "EXAMPLE_LISTBOX",
    "CODEFILE_LISTBOX",
    "DATAFILE_LISTBOX"
]

UI_ITEM_TAGS = {'{}'.format(i):generate_uuid() for i in _GENERAL_KEY_LIST}

#################################
# Item tag lists
COURSE_GENERAL_TAGS = [
    UI_ITEM_TAGS["COURSE_ID"],
    UI_ITEM_TAGS["COURSE_TITLE"],
    UI_ITEM_TAGS["COURSE_WEEKS"]
]

GENERAL_ASSIGNMENT_TAGS = [
    UI_ITEM_TAGS["ASSIGNMENT_TITLE"],
    UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"],
    UI_ITEM_TAGS["ASSIGNMENT_NO"],
    UI_ITEM_TAGS["ASSIGNMENT_TAGS"],
    UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"],
    UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"],
    UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"],
    UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"]
    
]

#################################
# Misc constants
OPEN_IX = None
OPEN_COURSE_PATH = None
COURSE_INFO = {
    "course_title": None,
    "course_id": None,
    "course_weeks": None
}
