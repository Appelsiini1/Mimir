"""
Mímir Initializer
Functions to initialize Mímir states and constants
"""

# pylint: disable=import-error
from os import path, mkdir
import logging

from src.constants import ENV, VERSION, LOG_LEVEL
from src.data_getters import get_recents
from src.common import resource_path

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

def init_defaults():
    """
    Makes sure that default files exist at ENV
    """
    doc_path = path.join(ENV["PROGRAM_DATA"], "document_settings.json")
    # untt_path = path.join(ENV["PROGRAM_DATA"], "unnumberedtotoc.sty")
    if not path.exists(doc_path):
        try:
            with open(resource_path("resource/document_settings.json"), "r", encoding="utf-8") as f:
                data = f.read()
                with open(doc_path, "w", encoding="utf-8") as f2:
                    f2.write(data)
        except OSError:
            logging.exception("Unable to write document settings defaults to ENV!!")
    # if not path.exists(untt_path):
    #     try:
    #         with open(resource_path("resource/unnumberedtotoc.sty"), "r", encoding="utf-8") as f:
    #             data = f.read()
    #             with open(untt_path, "w", encoding="utf-8") as f2:
    #                 f2.write(data)
    #     except OSError:
    #         logging.exception("Unable to write needed TeX libraries to ENV!!")


def init_environment():
    """
    Initializes program settings, environment variables and logging
    """
    _init_env_path()
    _init_logging()
    logging.info("Mímir initializing...")
    init_defaults()
    get_recents()
