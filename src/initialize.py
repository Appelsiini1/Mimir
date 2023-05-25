"""
Mímir Initializer
Functions to initialize Mímir states and constants
"""

# pylint: disable=import-error
from os import path, mkdir
import logging

from src.constants import ENV, VERSION, LOG_LEVEL
from src.data_handler import get_recents

# pylint: disable=logging-fstring-interpolation


def _init_logging():
    """
    Initialize logging
    """
    logname = path.join(ENV["PROGRAM_DATA"], "log.txt")
    logging.basicConfig(
        filename=logname,
        level=LOG_LEVEL,
        encoding="UTF-8",
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    logging.info("-#################-")
    logging.info(f"Mímir v{VERSION}")


def _init_env_path():
    """
    Makes sure that PROGRAM_DATA path exists
    """
    if path.exists(ENV["PROGRAM_DATA"]) is False:
        mkdir(ENV["PROGRAM_DATA"])


def init_environment():
    """
    Initializes program settings, environment variables and logging
    """
    _init_env_path()
    _init_logging()
    logging.info("Mímir initializing...")
    get_recents()
    logging.info("Mímir initialized.")
