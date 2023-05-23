"""Mímir classes for constants"""

from os.path import join

class COURSE_PATH:
    _path = None
    def get(self):
        return self._path
    def get_subdir(self, metadata=False):
        if metadata:
            return join(self._path, "metadata")
    def set(self, path):
        self._path = path

class RECENTS_LIST:
    _recents = []
    def get(self):
        return self._recents
    def set(self, new):
        self._recents = new

class IX:
    _open_ix = None
    def get(self):
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