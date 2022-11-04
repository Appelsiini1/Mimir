# Mímir Proof-of-concept program
# Rami Saarivuori
# 2022
# LUT University

import subprocess
import logging
from os import getenv, path, mkdir
import sys

ENVPATH = path.abspath(path.dirname(__file__))
ENVPATH2 = getenv("APPDATA") + "\\MimirPoC"
VERSION = 0.3


def init():  # pylint: disable=missing-function-docstring
    logname = path.join(ENVPATH, "log.txt")
    if path.exists(ENVPATH) is False:
        mkdir(ENVPATH)
    logging.basicConfig(
        filename=logname,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    logging.info(  # pylint: disable=logging-fstring-interpolation
        f"MimirPoC v{VERSION}"
    )


def ask_path():  # pylint: disable=missing-function-docstring
    filepath = input("TeX file path: ").strip('"')
    return filepath

def generate_pdf(filepath:str):
    try:

        output = subprocess.run(
            f"pdflatex {filepath}",
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        # komennon voisi myös antaa listana
        # capture_output tallentaa stdout ja stderr ajon aikana
        # Text on string muunnos byte stringistä normaaliin
        # check nostaa CalledProcessError jos paluuarvo ei ole 0
        # timeout lopettaa prosessin jos se vie kauemmin kuin annettu arvo

        # pdflatex pyytää käyttäjältä inputtia mikäli lähtötiedostoa ei ole olemassa, sen takia timeout

    except subprocess.CalledProcessError:
        logging.exception("Process exited with non-zero code:")
    except subprocess.TimeoutExpired as TE:  # pylint: disable=invalid-name
        logging.exception("Process timed out.")
        logging.error(TE.output)
        logging.error("##########")
        logging.error(TE.stderr)
        logging.error("##########")
        logging.error(TE.timeout)
        print("Process timed out, likely due to missing or wrong path.")
        # oikeassa moduulissa voisi tarkistaa esim. os kirjaston avulla että tiedosto on olemassa
        # eikä välttämättä ole ongelma jos tex tiedosto tehdään ohjelman avulla, mutta
        # virheenkäsittely on silti hyvä tehdä jos tiedosto vaikka jostain kumman syystä katoaa välissä
        sys.exit(0)
    except FileNotFoundError:
        logging.exception("Cannot find pdflatex")
        print("Cannot execute pdflatex command, make sure it is installed.")
        sys.exit(0)


    logging.info(output.args)
    logging.info("############")
    logging.info(output.returncode)
    logging.info("############")
    logging.info(str(output.stdout))
    logging.info("############")
    logging.error(str(output.stderr))
    logging.info("############")


def main():  # pylint: disable=missing-function-docstring
    # print("Hello World!")
    init()
    filepath = ask_path()
    generate_pdf(filepath)

    print("Run finished, details in log.")


if __name__ == "__main__":
    main()
