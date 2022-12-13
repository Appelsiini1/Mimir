"""
Mímir Initializer
Functions to initialize Mímir states and constants
"""

from os import path, mkdir
import logging

from constants import ENV, VERSION, LOG_LEVEL


def init_logging():  # pylint: disable=missing-function-docstring
    logname = path.join(ENV["PROGRAM_DATA"], "log.txt")
    logging.basicConfig(
        filename=logname,
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    logging.info(  # pylint: disable=logging-fstring-interpolation
        f"MimirPoC v{VERSION}"
    )

def init_env_path():
    """Makes sure that PROGRAM_DATA path exists"""
    if path.exists(ENV["PROGRAM_DATA"]) is False:
        mkdir(ENV["PROGRAM_DATA"])
