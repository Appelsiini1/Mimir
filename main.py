"""
Mímir Main
Functions to start Mímir
"""

from os import environ
environ['KIVY_HOME'] = "./config"   # set Kivy config path

from kivy import require            #pylint: disable=wrong-import-position
require('2.1.0')                    # sets the minimum version of UI library and raises an
                                    # exception if the installed version is less than required

from kivy.app import App            #pylint: disable=wrong-import-position
from kivy.uix.label import Label    #pylint: disable=wrong-import-position


class Mimir(App):
    """Base class and starting script for Mímir program"""
    def build(self):
        return Label(text='Hello world!')


if __name__ == "__main__":
    app = Mimir()
    app.run()
