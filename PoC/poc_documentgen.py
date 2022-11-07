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
VERSION = 0.2


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


# def ask_path():  # pylint: disable=missing-function-docstring
#     filepath = input("Assignment data file path: ").strip('"')
#     metafilepath = input("Assingment metadata file path: ").strip('"')
#     return filepath, metafilepath


def get_files(metadatapath: str, datapath: list, document_settingspath: str):

    # TeX base for document
    try:
        with open(document_settingspath, "r", encoding="utf-8") as doc_json:
            raw_json = doc_json.read()
            doc_settings = json.loads(raw_json)
    except FileNotFoundError:
        logging.exception("Document settings file not found.")
        print("Document settings file not found.")
        sys.exit(0)

    # Assignment metadata
    try:
        with open(metadatapath, "r", encoding="utf-8") as assignment_metafile:
            raw_json = assignment_metafile.read()
            assignment_metadata = json.loads(raw_json)
    except FileNotFoundError:
        logging.exception("Assingment data file %s not found.", metadatapath)
        print("Assignment metadatafile not found.")
        sys.exit(0)

    # Assignment example solution
    assignments = []
    for dpath in datapath:
        try:
            with open(dpath, "r", encoding="utf-8") as assignment_examplefile:
                assignment = assignment_examplefile.read()
        except FileNotFoundError:
            logging.exception("Assignment example %s file not found", datapath)
            print("Assignment example file not found.")
            sys.exit(0)
        assignments.append(assignment)

    return (doc_settings, assignment_metadata, assignments)


def tex_gen(metadatapath: str, datapath: list, document_settingspath: str):

    doc_settings, assignment_metadata, assignment = get_files(
        metadatapath, datapath, document_settingspath
    )

    tex_data = ""

    doc_class = doc_settings["document"]["preamble"]["documentclass"]
    doc_class_options = doc_settings["document"]["preamble"]["documentclass_options"]
    document_class_cmd = f"\\documentclass[{doc_class_options[0]}, {doc_class_options[1]}]{{{doc_class}}}"

    font = doc_settings["document"]["preamble"]["font"]
    font_cmd = f'\\usepackage[{font["family"]}]{{{font["package"]}}}\n\\usepackage[{font["type"]}]{{fontenc}}'

    extra_packages = doc_settings["document"]["preamble"]["packages"]
    extra_packages_cmd = f"\\usepackage{{{extra_packages[0][0]}}}\n\\usepackage{{{extra_packages[1][0]}}}\n\\usepackage{{lipsum}}"

    margins = doc_settings["document"]["preamble"]["margins"]
    margins_cmd = f"\\usepackage[{doc_class_options[1]}, left={margins[0]}mm, right={margins[1]}mm, top={margins[2]}mm, bottom={margins[3]}mm]{{geometry}}"

    hyphenation = doc_settings["document"]["preamble"]["no_hyphenation"]
    hyphenation_cmd = ""
    for t in hyphenation:
        hyphenation_cmd += t + "\n"

    begin = "\\begin{document}\n"

    text = "\\lipsum[1-1]"

    end = "\\end{document}"

    tex_cmd = [
        document_class_cmd,
        font_cmd,
        extra_packages_cmd,
        margins_cmd,
        hyphenation_cmd,
        begin,
        text,
        end,
    ]
    tex_data = "\n".join(tex_cmd)

    return tex_data


def write_tex_file(texdata, filepath):
    try:
        with open(filepath, "w", encoding="utf-8") as tex_doc:
            tex_doc.write(texdata)

    except Exception as e:  # pylint: disable=invalid-name
        logging.exception("Exception occured when writing to file.")
        print(e)
        sys.exit(0)


def main():  # pylint: disable=missing-function-docstring
    # print("Hello World!")

    datafilepath = ["Data\\poc_L01T1.c"]
    metafilepath = "Data\\poc_cprg_L01T1.json"
    document_settingspath = "Data\\poc_document_settings.json"
    resultpath = "result.tex"

    init()
    tex_data = tex_gen(metafilepath, datafilepath, document_settingspath)
    write_tex_file(tex_data, resultpath)


if __name__ == "__main__":
    main()
