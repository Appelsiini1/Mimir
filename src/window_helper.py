"""
Mímir window helper functions
"""

import dearpygui.dearpygui as dpg

def close_window(window_id: int | str):
    """
    Closes a UI window.

    Params:
    sender: Not used.
    app_data: Not used.
    window_id: The UUID of the window to close.
    """
    dpg.delete_item(window_id)