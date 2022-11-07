# Mímir Proof-of-concept program
# Rami Saarivuori
# 2022
# LUT University

import logging
from os import getenv, path, mkdir
import sys
import json

ENVPATH = path.abspath(path.dirname(__file__))
ENVPATH2 = getenv("APPDATA") + "\\MimirPoC"
VERSION = 0.1


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
    filepath = input("Assignment data file path: ").strip('"')
    metafilepath = input("Assingment metadata file path: ").strip('"')
    return filepath, metafilepath


def get_files(metadatapath: str, datapath: str, document_settingspath: str):

    # TeX base for document
    try:
        with open(document_settingspath, encoding="utf-8") as doc_json:
            raw_json = doc_json.read()
            doc_settings = json.loads(raw_json)
    except FileNotFoundError:
        logging.exception("Document settings file not found.")
        print("Document settings file not found.")
        sys.exit(0)

    # Assignment metadata
    try:
        with open(metadatapath, encoding="utf-8") as assignment_metafile:
            raw_json = assignment_metafile.read()
            assignment_metadata = json.loads(raw_json)
    except FileNotFoundError:
        logging.exception("Assingment data file %s not found.", metadatapath)
        print("Assignment metadatafile not found.")
        sys.exit(0)

    # Assignment example solution
    try:
        with open(datapath, encoding="utf-8") as assignment_examplefile:
            assignment = assignment_examplefile.read()
    except FileNotFoundError:
        logging.exception("Assignment example %s file not found", datapath)
        print("Assignment example file not found.")
        sys.exit(0)

    return (doc_settings, assignment_metadata, assignment)


def tex_gen(metadatapath, datapath, document_settingspath: str):

    doc_settings, assignment_metadata, assignment = get_files(
        metadatapath, datapath, document_settingspath
    )

    tex_data = ""

    try:
        with open("testdocument.tex", encoding='utf-8') as tex_doc:
            pass

    except Exception as e:
        logging.exception("Exception occured when writing to file.")
        print(e)
        sys.exit(0)
        



def main():  # pylint: disable=missing-function-docstring
    # print("Hello World!")
    init()
    filepath, metafilepath = ask_path()


if __name__ == "__main__":
    main()
