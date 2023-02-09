"""
Mímir Excersise Set Generator
Functions to handle the creation of pseudorandom exercise sets
"""

# pylint: disable=import-error

from os import getcwd
from tkinter.filedialog import askopenfilename, askopenfilenames

import src.data_handler as DH
from src.tex_generator import gen_one_week

def _openfilebrowser(_, app_data, carrier:DH.FILEPATHCARRIER) -> list:
    file_paths = askopenfilenames(filetypes=carrier.extensions)
    print(file_paths)
    return file_paths

def temp_creator(_, app_data, user_data):
    """Temp"""
    files = DH.FILEPATHCARRIER()
    files.json_files()
    files.filepaths = _openfilebrowser(None, None, files)
    print(files.filepaths)
    dicts = []
    formatted = []
    for ex in files.filepaths:
        dicts.append(DH.get_assignment_json(ex))
    for dict_ in dicts:
        formatted.append(DH.format_metadata_json(dict_))
    general = askopenfilename()
    print(general)
    general = DH.format_general_json(DH.get_assignment_json(general), 5)

    gen_one_week(general, formatted, True, "output.tex")
    gen_one_week(general, formatted, False, "output2.tex")