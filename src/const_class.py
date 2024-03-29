"""Mímir classes for constants"""

from os.path import join, abspath
from whoosh.index import FileIndex

# pylint: disable=invalid-name, missing-class-docstring, missing-function-docstring


class COURSE_PATH:
    _path = None

    def get(self):
        return self._path
    
    def get_set_path(self):
        return join(self._path, "assignment_sets.json")

    def get_subdir(self, metadata=False, index=False, assignment_data=False):
        if metadata:
            return join(self._path, "metadata")
        if index:
            return join(self._path, "index")
        if assignment_data:
            return join(self._path, "assignment_data")
        return None

    def set(self, path):
        self._path = abspath(path)


class RECENTS_LIST:
    _recents = []

    def get(self):
        return self._recents

    def set(self, new):
        self._recents = new


class IX:
    _open_ix = None

    def get(self) -> FileIndex:
        return self._open_ix

    def set(self, new):
        self._open_ix = new


class LANG:
    _lang = "FI"
    _langs = ["FI", "ENG"]

    def get(self):
        return self._lang

    def get_all(self):
        return self._langs

    def set(self, new):
        self._lang = new

    def set_all(self, new):
        self._langs = new


class WEEK:
    _week_data = {}

    def get(self):
        return self._week_data
    def set(self, new):
        self._week_data = new