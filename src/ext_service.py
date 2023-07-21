"""
Mímir External Service Handler

Functions to handle connections to external services like
compilers or runtime environments
"""

# pylint: disable=import-error
import logging
import subprocess
from os import path
from shutil import copy

from src.constants import ENV

def run_command(command:str, inputs:str|None, process_timeout=10):
    """
    Runs a command using subprocess and captures output.
    Returns an instance of CompletedProcess if runs is a success.
    On error returns an instance of CalledProcessError, TimeoutExpired,
    or FileNotFoundError.

    Params:
    command: the command to run as string
    inputs: the inputs that are given to the command or None
    process_timeout: Defaults to 10 (seconds).
    """

    try:

        output = subprocess.run(
            command,
            cwd=ENV["PROGRAM_DATA"],
            capture_output=True,
            text=True,
            timeout=process_timeout,
            check=True,
            input=inputs
        )
        # capture_output saves stdout ja stderr during the run
        # Text changes bytes to str
        # check raises CalledProcessError if exit code is not 0
        # timeout stops the process if it takes longer than given value

    except subprocess.CalledProcessError as process_error:
        logging.exception("Process exited with non-zero code.")
        return process_error
    except subprocess.TimeoutExpired as timeout_exception:
        logging.exception("Process timed out.")
        logging.error(timeout_exception.output)
        logging.error("##########")
        logging.error(timeout_exception.stderr)
        return timeout_exception
    except FileNotFoundError as fnfe_exception:
        logging.exception("Cannot find command")
        return fnfe_exception
    else:
        logging.info("Process completed.")
        logging.info("Command output: %s", output)
        return output


def generate_pdf():
    """
    Runs pdflatex command to generate the PDF from generated TeX file.
    """

    command = "pdflatex -shell-escape output.tex"

    output= run_command(command, None, process_timeout=30)
    output= run_command(command, None, process_timeout=30)
    return output

def copy_files(filepath_out:str, filename:str):
    """
    Copy files from input to output. Rename files if necessary, up to 100 iterations.
    
    Params:
    filepath_out: the path to move the finished PDF file to
    filename: the filename that the output will be renamed to
    """

    fpath_out = path.join(filepath_out, filename)
    filepath_out = fpath_out+".pdf"
    filepath_in = path.join(ENV["PROGRAM_DATA"], "output.pdf")
    if not path.exists(filepath_out):
        try:
            copy(filepath_in, filepath_out)
        except OSError:
            logging.exception("Error copying files!")
            return False
        return True
    for i in range(1,100):
        filepath_out = fpath_out + f" ({str(i)}).pdf"
        if not path.exists(filepath_out):
            try:
                copy(filepath_in, filepath_out)
            except OSError:
                logging.exception("Error copying files!")
                return False
            return True
    logging.error("Too many iterations to output filename!\
                    Please delete old files or choose a new folder.")
    return False
