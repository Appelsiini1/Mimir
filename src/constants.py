"""Mímir constants"""

# pylint: disable=import-error
from os import name as OSname
from os import getenv
from os.path import join
from logging import DEBUG, INFO
import json

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
    with open(resource_path("resource/texts.json"), "r", encoding="utf-8") as _file:
        _data = _file.read()
        _display_texts = json.loads(_data)
    return _display_texts

DISPLAY_TEXTS = _get_texts()
LANGUAGE = "FI"

VERSION = "0.1.0"
LOG_LEVEL = DEBUG
