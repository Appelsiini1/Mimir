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
