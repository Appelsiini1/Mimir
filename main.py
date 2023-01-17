"""
Mímir Main
Functions to start Mímir
"""

import dearpygui.dearpygui as dpg

from src.constants import VERSION
from src.initialize import init_environment
from src.tex_generator import gen_one_week
from src.ui_handler import main_window, set_style

def main():
    """
    Main entry point to Mímir
    """
    init_environment()
    dpg.create_context()
    dpg.create_viewport(title=f'Mimir v{VERSION}', width=1500, height=800)
    set_style()
    main_window()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()



if __name__ == "__main__":
    main()
