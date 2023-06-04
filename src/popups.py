"""Mímir UI popups"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import dearpygui.dearpygui as dpg

from src.constants import DISPLAY_TEXTS, LANGUAGE
from src.ui_helper import close_window, move_info


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


def popup_create_course(**args):
    """
    Creates a popup with course info inputs
    """

    field_ids = {
        "popup": dpg.generate_uuid(),
        "id": dpg.generate_uuid(),
        "title": dpg.generate_uuid(),
        "weeks": dpg.generate_uuid(),
    }
    with dpg.window(
        modal=True,
        tag=field_ids["popup"],
        no_close=True,
        no_title_bar=True,
        autosize=True,
    ):
        with dpg.group():
            with dpg.table(header_row=False):
                dpg.add_table_column(
                    label="Course info one",
                    width_fixed=True,
                    init_width_or_weight=230,
                )
                dpg.add_table_column(
                    label="Course info two",
                    width_fixed=True,
                    init_width_or_weight=410,
                )
                with dpg.table_row():
                    dpg.add_text(DISPLAY_TEXTS["ui_course_id"][LANGUAGE.get()] + ":")
                    dpg.add_input_text(
                        callback=None,
                        width=400,
                        tag=field_ids["id"],
                    )
                with dpg.table_row():
                    dpg.add_text(DISPLAY_TEXTS["ui_course_name"][LANGUAGE.get()] + ":")
                    dpg.add_input_text(callback=None, width=400, tag=field_ids["title"])
                with dpg.table_row():
                    dpg.add_text(DISPLAY_TEXTS["ui_no_weeks"][LANGUAGE.get()] + ":")
                    dpg.add_input_int(
                        callback=None,
                        width=150,
                        min_value=1,
                        min_clamped=True,
                        tag=field_ids["weeks"],
                    )

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_save"][LANGUAGE.get()],
                    callback=move_info,
                    user_data=field_ids,
                    width=75,
                )
                dpg.add_spacer(width=5)
                dpg.add_button(
                    label=DISPLAY_TEXTS["ui_cancel"][LANGUAGE.get()],
                    callback=lambda s, a, u: close_window(u),
                    user_data=field_ids["popup"],
                )
