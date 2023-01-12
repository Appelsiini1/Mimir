"""Mímir constants"""

from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG
import json

from data_handler import resource_path


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
    with open(resource_path("texts.json"), "r", encoding="utf-8") as _file:
        _data = _file.read()
        _display_texts = json.loads(_data)
    return _display_texts

DISPLAY_TEXTS = _get_texts()
LANGUAGE = "FI"

VERSION = "0.0.5"
LOG_LEVEL = DEBUG
