"""
Mímir External Service Handler
Functions to handle connections to external services like
compilers or runtime environments
"""

import logging
import subprocess
from os import path

from constants import ENV
from custom_errors import CannotMoveFileError

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
        logging.error("Following errors were encountered during command run: ")
        return output


def generate_pdf(filepath_out:str, filename:str):
    """
    Runs pdflatex command to generate the PDF from generated TeX file.

    Params:
    filepath_out: the path to move the finished PDF file to
    """

    #TODO add error handling if pdflatex command returns an exception

    command = "pdflatex output.tex"

    output= run_command(command, None)

    if output is type(subprocess.CompletedProcess):
        if ENV["OS"] == "nt":
            filepath_out = path.join(filepath_out, filename)
            command = f"cd \"{ENV['PROGRAM_DATA']}\" \
                && move /Y output.pdf \"{filepath_out}\""
        else:
            filepath_dest = path.join(filepath_out, "output.pdf")
            command = f"cd \"{ENV['PROGRAM_DATA']}\" \
                && mv output.pdf \"{filepath_dest}\" \
                && cd \"{filepath_out}\" \
                && mv output.pdf {filename}"

        output = run_command(command, None)
        if output is not type(subprocess.CompletedProcess):
            raise CannotMoveFileError(output)
