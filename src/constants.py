"""Mímir constants"""

# pylint: disable=import-error
from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG, INFO
import json

from dearpygui.dearpygui import generate_uuid
from src.common import resource_path


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


def _get_texts():
    # TODO Add error handling
    with open(resource_path("resource/texts.json"), "r", encoding="utf-8") as _file:
        _data = _file.read()
        _display_texts = json.loads(_data)
    return _display_texts


DISPLAY_TEXTS = _get_texts()
LANGUAGE = "FI"

VERSION = "0.2.13"
LOG_LEVEL = DEBUG

# Unique UI item tags
UI_ITEM_TAGS = {}
UI_ITEM_TAGS["total_index"] = generate_uuid()
UI_ITEM_TAGS["PREVIOUS_PART_CHECKBOX"] = generate_uuid()
UI_ITEM_TAGS["PREVIOUS_PART_COMBOBOX"] = generate_uuid()
UI_ITEM_TAGS["CODE_LANGUAGE_COMBOBOX"] = generate_uuid()
UI_ITEM_TAGS["INST_LANGUAGE_COMBOBOX"] = generate_uuid()
UI_ITEM_TAGS["VARIATION_GROUP"] = generate_uuid()
UI_ITEM_TAGS["MAIN_WINDOW"] = generate_uuid()
UI_ITEM_TAGS["ADD_ASSIGNMENT_WINDOW"] = generate_uuid()
UI_ITEM_TAGS["OPEN_ADD_ASSINGMENT_BUTTON"] = generate_uuid()
UI_ITEM_TAGS["WARNING_POPUP_ADD_ASSIG_WINDOW"] = generate_uuid()
UI_ITEM_TAGS["ASSIGNMENT_TITLE"] = generate_uuid()
UI_ITEM_TAGS["ASSIGNMENT_LECTURE_WEEK"] = generate_uuid()
UI_ITEM_TAGS["ASSIGNMENT_NO"] = generate_uuid()
UI_ITEM_TAGS["ASSIGNMENT_TAGS"] = generate_uuid()
UI_ITEM_TAGS["COURSE_ID"] = generate_uuid()
UI_ITEM_TAGS["COURSE_TITLE"] = generate_uuid()
UI_ITEM_TAGS["COURSE_WEEKS"] = generate_uuid()

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

VARIATION_TAGS = [

]

EXAMPLE_RUN_TAGS = [

]

# Misc constants

OPEN_IX = None
OPEN_COURSE_PATH = None
COURSE_INFO = {
    "course_title": None,
    "course_id": None,
    "course_weeks": None
}
