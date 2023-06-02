"""
Mímir Main

Functions to start Mímir
"""

import logging
import dearpygui.dearpygui as dpg

dpg.create_context()

# pylint: disable=wrong-import-position
from src.constants import VERSION, UI_ITEM_TAGS
from src.initialize import init_environment
from src.UI_handler import main_window
from src.ui_helper import setup_ui


def main():
    """
    Main entry point to Mímir
    """
    init_environment()
    logging.info("Environment initialized.")

    dpg.create_viewport(title=f"Mimir v{VERSION}", width=1500, height=800)

    setup_ui()
    main_window()
    dpg.set_primary_window(UI_ITEM_TAGS["MAIN_WINDOW"], True)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()


if __name__ == "__main__":
    main()
