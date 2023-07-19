"""Mímir UI popups"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE
from src.window_helper import close_window


def popup_ok(msg: str, **args):
    """
    Creates a popup with "OK" button.

    Params:
    msg: Message to display
    """

    popup_id = dpg.generate_uuid()
    with dpg.window(
        modal=True,
        tag=popup_id,
        no_close=True,
        no_title_bar=True,
        autosize=True,
    ):
        dpg.add_spacer(height=5)
        dpg.add_text(msg)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        dpg.add_button(
            label=DISPLAY_TEXTS["ui_ok"][LANGUAGE.get()],
            callback=lambda s, a, u: close_window(u),
            user_data=popup_id,
            width=75,
        )


def popup_confirmation(s, a, u):
    """
    Creates a popup with "OK" and "Cancel" buttons.

    Params:
    msg: message to display
    function: function to call
    parameters: a tuple containing parameters to pass on to the callable function
    """

    msg = u[0]
    function = u[1]

    popup_id = dpg.generate_uuid()
    parameters = u[2] + (popup_id,)

    with dpg.window(
        modal=True,
        tag=popup_id,
        no_close=True,
        no_title_bar=True,
        autosize=True,
    ):
        dpg.add_spacer(height=5)
        dpg.add_text(msg)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_ok"][LANGUAGE.get()],
                callback=function,
                user_data=parameters,
                width=75,
            )
            dpg.add_button(
                label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                callback=lambda s, a, u: close_window(u),
                user_data=popup_id,
                width=75
            )


def popup_load(msg:str, ID:str|int, textID:str|int):
    """
    Creates a popup with no buttons.

    Params:
    msg: message to display
    ID: the window ID that the popup will get
    """

    with dpg.window(
        modal=True,
        tag=ID,
        no_close=True,
        no_title_bar=True,
        autosize=True,
    ):
        dpg.add_spacer(height=5)
        dpg.add_text(msg, tag=textID)
        dpg.add_spacer(height=5)