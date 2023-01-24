"""
Mímir Common module

Functions that are used by multiple modules, moved here to prevent
circular imports
"""

import sys
from os import path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # pylint: disable=protected-access, no-member
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)
