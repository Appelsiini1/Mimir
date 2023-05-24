"""Mímir UI popups"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE, UI_ITEM_TAGS
from src.ui_helper import close_window

def popup_no_course_open(sender:int|str):
    """
    Creates warning popup for no course open
    """

    popup_id = dpg.generate_uuid()
    with dpg.popup(parent=sender, mousebutton=dpg.mvMouseButton_Left, modal=True, tag=popup_id):
        dpg.add_spacer(height=5)
        dpg.add_text(DISPLAY_TEXTS["popup_nocourse"][LANGUAGE])
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        dpg.add_button(
            label=DISPLAY_TEXTS["ui_ok"][LANGUAGE],
            callback=close_window,
            user_data=popup_id,
            width=75,
        )
