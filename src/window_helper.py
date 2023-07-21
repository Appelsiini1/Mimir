"""
Mímir window helper functions
"""

import dearpygui.dearpygui as dpg

def close_window(window_id: int | str):
    """
    Closes a UI window.

    Params:
    window_id: The UUID of the window to close.
    """
    dpg.delete_item(window_id)