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
VERSION = 0.4


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


def get_files(
    metadatapaths: list, datapath: list, document_settingspath: str, general_path: str
):

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
    assignment_metadata = []
    for metadatapath in metadatapaths:
        try:
            with open(metadatapath, "r", encoding="utf-8") as assignment_metafile:
                raw_json = assignment_metafile.read()
                loaded_json = json.loads(raw_json)
                assignment_metadata.append(loaded_json)
        except FileNotFoundError:
            logging.exception("Assingment data file %s not found.", metadatapath)
            print("Assignment metadatafile not found.")
            sys.exit(0)

    # Week general data
    try:
        with open(general_path, "r", encoding="utf-8") as gen_file:
            raw_json = gen_file.read()
            gen_info = json.loads(raw_json)
    except FileNotFoundError:
        logging.exception("Week metadata file %s not found", general_path)
        print("Week metadata not found")
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

    return (doc_settings, assignment_metadata, assignments, gen_info)


def hdr_ftr_gen(doc_settings, gen_info):
    # generate header and footer
    header_opt = doc_settings["document"]["preamble"]["header"]
    footer_opt = doc_settings["document"]["preamble"]["footer"]

    if doc_settings["document"]["pagestyle"] == "fancy":
        hdr_cmd = "\\fancyhead{}\n"
        ftr_cmd = "\\fancyfoot{}\n"

        if header_opt["include_course"]:
            course = gen_info["course_id"] + " " + gen_info["course_name"]
            hdr_cmd += f"\\fancyhead[L]{{{course}}}\n"

        if footer_opt["include_week"]:
            ftr_cmd += f"\\fancyfoot[C]{{Viikko {gen_info['lecture']}}}\n"

        if footer_opt["include_program"]:
            ftr_cmd += f"\\fancyfoot[L]{{Mímir v{VERSION}}}"

        page_numbering = f"\\fancyhead[{header_opt['page_numbering'][0]}]\
{{Sivu {header_opt['page_numbering'][1]}}}\n"
        hdr_cmd += page_numbering

        return (hdr_cmd, ftr_cmd)

    else:
        return ""


def preamble_gen(doc_settings):
    preamble = doc_settings["document"]["preamble"]

    doc_class = preamble["documentclass_options"]
    doc_class_cmd = f"\\documentclass[{doc_class[0]}, \
{doc_class[1]}]{{{preamble['documentclass']}}}"

    font = preamble["font"]
    font_cmd = f'\\usepackage[{font["family"]}]{{{font["package"]}}}\n\
\\usepackage[{font["type"]}]{{fontenc}}'

    extra_packages = preamble["packages"]
    extra_packages_cmd = ""
    for package in extra_packages:
        extra_packages_cmd += f"\\usepackage[{package[1]}]{{{package[0]}}}\n"

    margins = preamble["margins"]
    margins_cmd = f"\\usepackage[{doc_class[1]}, \
left={margins[0]}mm, \
right={margins[1]}mm, \
top={margins[2]}mm, \
bottom={margins[3]}mm]\
{{geometry}}"

    head_height = f"\\setlength{{\\headheight}}{{{preamble['head_height']}}}\n"

    hyphenation = preamble["no_hyphenation"]
    hyphenation_cmd = ""
    for t in hyphenation:
        hyphenation_cmd += t + "\n"

    return [
        doc_class_cmd,
        font_cmd,
        extra_packages_cmd,
        margins_cmd,
        head_height,
        hyphenation_cmd,
    ]


def starting_instructions_gen(gen_info):
    text = ""
    title = f"\\section*{{L{gen_info['lecture']} Tehtävät}}\n"

    topics = "\\begin{itemize}[noitemsep]\n"
    for topic in gen_info["topics"]:
        topics += f"\t\\item {topic}\n"

    text += title
    text += "\\vspace{0.2cm}"
    text += topics
    text += "\\end{itemize}\n"
    text += gen_info["instructions"] + "\n"
    text += "\\tableofcontents\n\\vspace{1cm}\n"

    return text


def assignment_text_gen(metadata: list, assignment_list: list):

    text = ""
    for i, assignment in enumerate(assignment_list):
        meta = metadata[i]
        text += f"\\addsec{{L{meta['lecture']}T{meta['exp_assignment_no']}: {meta['title']}}}\n"
        text += meta["instructions"] + "\n"
        text += "\\vspace{0.1cm}\n"

        text += "\n\\textbf{Esimerkkiajo}\n"
        text += "{\\fontfamily{{qcr}}\\selectfont\n\\begin{verbatim}\n"
        text += meta["example_output"] + "\n\end{verbatim}\n}\n"
        text += "\\vspace{0.1cm}\n"

        text += "\\textbf{Malliratkaisu}\n"
        text += "{\\fontfamily{{qcr}}\\selectfont\n\\begin{verbatim}\n"
        text += assignment.replace("\t", "    ") + "\end{verbatim}\n}\n"

        text += "\\vspace{0.5cm}\n"

    return text


def tex_gen(
    metadatapath: list, datapath: list, document_settingspath: str, general_path: str
):

    doc_settings, assignment_metadata, assignment, gen_info = get_files(
        metadatapath, datapath, document_settingspath, general_path
    )

    tex_data = ""
    begin = "\\begin{document}\n"
    pagestyle = f'\\pagestyle{{{doc_settings["document"]["pagestyle"]}}}'

    pre_content = starting_instructions_gen(gen_info)
    content = assignment_text_gen(assignment_metadata, assignment)
    end = "\\end{document}"

    preamble = preamble_gen(doc_settings)
    header, footer = hdr_ftr_gen(doc_settings, gen_info)

    tex_cmd = preamble + [
        begin,
        pagestyle,
        header,
        footer,
        pre_content,
        content,
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

    datafilepath = ["Data\\poc_L01T1.c", "Data\\poc_L01T2.c"]
    metafilepath = ["Data\\poc_cprg_L01T1.json", "Data\\poc_cprg_L01T2.json"]
    document_settingspath = "Data\\poc_document_settings.json"
    resultpath = "result.tex"
    general_path = "Data\\poc_cprg_L01_general.json"

    init()
    tex_data = tex_gen(metafilepath, datafilepath, document_settingspath, general_path)
    write_tex_file(tex_data, resultpath)


if __name__ == "__main__":
    main()
