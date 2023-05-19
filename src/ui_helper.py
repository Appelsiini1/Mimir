"""Mímir UI helper functions for callbacks"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join
from os import getcwd
from string import ascii_uppercase
from tkinter.filedialog import askopenfilenames
import dearpygui.dearpygui as dpg

from src.constants import FILETYPES, DISPLAY_TEXTS, LANGUAGE
from src.data_handler import path_leaf
from src.common import resource_path

################################

class VARIATION:
    def __init__(self) -> None:
        self.variations = []

    def get_all_variations(self) -> list:
        """Get current list of variations"""
        return self.variations

    def get_var_count(self) -> int:
        """Returns how many variations are saved"""
        return len(self.variations)

    def add(self, data:dict) -> None:
        """Add variation dict to list"""
        self.variations.append(data)

    def update(self, data:dict) -> None:
        """Updates variation with new data if it already exists"""
        # TODO

    def delete(self, var_letter) -> None:
        found = next((i for i, item in enumerate(self.variations) if item["variation_id"] == var_letter), None)
        if found:
            self.variations.remove(found)

################################

def _load_fonts():
    """
    Loads default fonts. Returns a dict of loaded fonts.
    """
    _fonts = {}
    with dpg.font_registry():
        _fonts["default"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Regular.ttf")
            ),
            24,
        )
        _fonts["italic"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Italic.ttf")
            ),
            24,
        )
        _fonts["bold"] = dpg.add_font(
            resource_path(
                join("resource", "source-sans-pro", "SourceSansPro-Bold.ttf")
            ),
            24,
        )

    return _fonts


def set_style():
    """
    Set colours, fonts etc.
    """
    fonts = _load_fonts()
    dpg.bind_font(fonts["default"])
    logging.info("Fonts loaded.")

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(
                dpg.mvThemeCol_Button, (105, 90, 138), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_TitleBg, (157, 0, 255), category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_color(
                dpg.mvThemeCol_ButtonHovered,
                (105, 90, 138, 162),
                category=dpg.mvThemeCat_Core,
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core
            )

    dpg.bind_theme(global_theme)
    logging.info("Theme setup finished.")


def setup_textures():
    """
    Setup textures and texture registry
    """
    dpg.add_texture_registry(
        label="Mimir Texture Container", tag="__main_texture_container"
    )

    width, height, _, data = dpg.load_image(resource_path("resource/logoV3.png"))
    dpg.add_static_texture(
        width=width,
        height=height,
        default_value=data,
        tag="mimir_logo",
        label="Mímir Logo",
        parent="__main_texture_container",
    )
    i = 1  # number of textures added so far
    logging.info("Texture registry added, with %d textures inside." % i)

def help_(message):
    """
    Display help popup "(?)" next to the title with 'message' in it.
    From DearPyGUI demo
    """
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text("(?)", color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)

def get_variation_letter(var):
    base = len(ascii_uppercase)
    result = ""
    while var > 0:
        result = ascii_uppercase[(var - 1) % base] + result
        var = (var - 1) // base
    return result


def close_window(sender: None, app_data: None, window_id: int | str):
    """
    Closes a UI window.

    Params:
    sender: Not used.
    app_data: Not used.
    window_id: The UUID of the window to close.
    """
    dpg.delete_item(window_id)

def extract_variation_data(var:dict, data:dict, UUIDS:list):
    pass

def get_files(s, a, u:tuple):
    """
    Gets file paths from the user and adds them to the spesified list box

    Params:
    u: A tuple that contains the dict to save to, listbox UUID and file type group name
    """
    save_to = u[0]
    listbox = u[1]
    f_type = u[2]

    if f_type == "codefile":
        files = openfilebrowser(f_type)
        save_to["codefiles"] = list(files)
    elif f_type == "datafiles":
        files = openfilebrowser("textfile")
        save_to["datafiles"] = files

    leafs = [path_leaf(i) for i in files]
    dpg.configure_item(listbox, items=leafs)

def openfilebrowser(f_type:str) -> list:
    """
    Opens the filebrowser with f_type file extensions available.
    Allows the selection of multiple files. Returns a list of paths of the selected files.
    """
    if f_type not in FILETYPES["types"]:
        raise TypeError("Filetype not found")
    if f_type != "any":
        extensions = FILETYPES[f_type] + FILETYPES["any"]
    else:
        extensions = FILETYPES[f_type]
    file_paths = askopenfilenames(initialdir=getcwd(), filetypes=extensions)
    return list(file_paths)

def remove_selected(s, a, u):
    """
    Removes the selected item from the listbox.

    Params:
    u: A tuple that contains:
        0. The listbox to remove from
        1. The data structure to remove from
        2. The type of data to remove
    """
    selected = dpg.get_value(u[0])
    data = u[1]
    i_type = u[2]
    final = []

    if selected == "":
        return

    if i_type == "variation":
        for i, item in enumerate(data["variations"]):
            if item["variation_id"] == selected.split(" ")[1]:
                data["variations"].pop(i)
                final = data["variations"]
                break
    elif i_type == "datafiles":
        for i, item in enumerate(data["datafiles"]):
            if path_leaf(item) == selected:
                data["datafiles"].pop(i)
                final = [path_leaf(i) for i in data["datafiles"]]
                break
    elif i_type == "codefiles":
        for i, item in enumerate(data["codefiles"]):
            if path_leaf(item) == selected:
                data["codefiles"].pop(i)
                final = [path_leaf(i) for i in data["codefiles"]]
                break
    elif i_type == "ex_run":
        index = selected.split(" ")[1]-1
        data["example_runs"].pop(index)
        final = ["{} {}".format(DISPLAY_TEXTS["ex_run"][LANGUAGE], i) for i, _ in enumerate(data["example_runs"])]


    dpg.configure_item(u[0], items=final)
