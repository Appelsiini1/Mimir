"""
Mímir TeX Generator

Functions to generate instruction TeX file from available data
"""

# pylint: disable=import-error, logging-not-lazy, consider-using-f-string
import logging
from os.path import join, split

from src.constants import VERSION, ENV, DISPLAY_TEXTS, LANGUAGE
from src.data_handler import get_texdoc_settings

# pylint: disable=anomalous-backslash-in-string


def _hdr_ftr_gen(doc_settings: dict, gen_info: dict):
    """
    Generate header and footer

    Params:
    doc_settings: Document settings as JSON (dict)
    """
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

        logging.debug("TEX HEADER")
        logging.debug(hdr_cmd)
        logging.debug("TEX FOOTER")
        logging.debug(ftr_cmd)

        return (hdr_cmd, ftr_cmd)

    return ""


def _preamble_gen(doc_settings: dict, lecture: int):
    """
    Create preamble for the TeX document.
    This includes most of the general settings for the document.
    Returns a string.

    Params:
    doc_settings: Documents settings as a JSON string.
    """
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

    other = "\n".join(preamble["other"])
    toc = "\\renewcommand{\\contentsname}{" + DISPLAY_TEXTS["tex_toc"][LANGUAGE] + "}\n"
    metadata = "\\hypersetup{pdfauthor={" + f"Mímir v{VERSION}" + "}"
    metadata += ", pdftitle={L" + f"{lecture} {DISPLAY_TEXTS['assignments'][LANGUAGE]}" + "}}"

    result = [
        doc_class_cmd,
        font_cmd,
        extra_packages_cmd,
        margins_cmd,
        head_height,
        hyphenation_cmd,
        other,
        toc,
        metadata,
    ]
    logging.debug("TEX PREAMBLE")
    logging.debug(result)

    return result


def _starting_instructions_gen(gen_info: dict):
    """
    Creates the general instructions of the instruction document
    Returns a TeX string.

    Params:
    gen_info: General instructions as a dict
    """
    text = ""
    title = f"\\section*{{L{gen_info['lecture']} {DISPLAY_TEXTS['assignments'][LANGUAGE]}}}\n"

    topics = "\\begin{itemize}[noitemsep]\n"
    for topic in gen_info["topics"]:
        topics += f"\t\\item {topic}\n"

    text += title
    text += "\\vspace{0.2cm}"
    text += topics
    text += "\\end{itemize}\n"
    text += gen_info["instructions"] + "\n"
    text += "\\tableofcontents\n\\vspace{1cm}\n"

    logging.debug("TEX STARTING INSTRUCTIONS")
    logging.debug(text)

    return text


def _block_gen(display_text_key: str, data: dict, ex_file=None):
    """
    Creates assignment info block TeX string from given data.
    Returns the generated TeX string.

    Params:
    display_text_key: A key that spesifies what display text to get from DISPLAY_TEXTS
    data: A dictionary containing block data
    data_key: the spesific data to get from 'data' parameter
    ex_file: If the block is a file example, spesify the filename here. Defaults to None.
    """

    text = "{"
    text = "\\normalsize"
    if not ex_file:
        text += "\\textit{"
    text += f"\\textbf{{{DISPLAY_TEXTS[display_text_key][LANGUAGE]}"
    if ex_file:
        text += f" '{split(ex_file)[1]}'"
    text += ":}"
    if not ex_file:
        text += "}"
    text += "{\\fontfamily{{cmr}}\\selectfont\n\\begin{minted}[bgcolor=bg, fontsize=\\small]{text}\n"
    if display_text_key == "ex_input":
        for line in data:
            text += str(line) + "\n"
    elif display_text_key == "cmd_input":
        for line in data:
            text += str(line) + " "
        text += "\n"
    else:
        text += data
    if text[-1] != "\n":
        text += "\n"
    text += "\end{minted}\n}\n"
    text += "\\vspace{0.1cm}\n"

    logging.debug("TEX BLOCK GENERATOR")
    logging.debug("DISPLAY KEY: %s" % display_text_key)
    logging.debug(text)

    return text


def _assignment_text_gen(gen_info: dict, assignment_list: list, incl_solution: bool):
    """
    Creates assignment TeX string from assingment code and metadata.
    Returns a TeX string

    Params:
    assignment_list: A list of assignments as dicts containing assingment information
    incl_solution: A boolean that spesifies whether to include the example solution in the assingment
    """

    # TODO Add numbered list generator for lines starting with '-'

    text = ""
    for i, assignment in enumerate(assignment_list, start=1):
        text += "\\phantomsection\n"
        text += "\\addcontentsline{toc}{section}"
        title = f"{{L{gen_info['lecture']}{DISPLAY_TEXTS['tex_assignment_letter'][LANGUAGE]}{i}: {assignment['title']}}}\n"
        text += title
        text += "\\section*" + title
        text += assignment["instructions"] + "\n"
        text += "\\vspace{0.1cm}\n"

        if "datafiles" in assignment:
            text += "\\hfill\\break\\newline\n"
            for datafile in assignment["datafiles"]:
                text += _block_gen(
                    "tex_ex_input_datafile", datafile["data"], datafile["filename"]
                )

        for i, example_run in enumerate(assignment["example_runs"], start=1):
            text += f"\n\\large\\textbf{{{DISPLAY_TEXTS['ex_run'][LANGUAGE]} {i}}}\n"
            text += "\\hfill\\break\\newline\n"
            if example_run["CMD"]:
                text += _block_gen("cmd_input", example_run["CMD"])
            if example_run["inputs"]:
                text += _block_gen("ex_input", example_run["inputs"])
            if example_run["output"]:
                text += _block_gen("ex_output", example_run["output"])
            if example_run["outputfiles"]:
                for resultfile in example_run["outputfiles"]:
                    text += _block_gen(
                        "tex_ex_resultfile", resultfile["data"], resultfile["filename"]
                    )

        if incl_solution:
            text += (
                f"\\textbf{{{DISPLAY_TEXTS['tex_ex_solution'][LANGUAGE]}}}\\newline\n"
            )
            for code in assignment["example_codes"]:
                text += f"\\textbf{{'{split(code['filename'])[1]}':}}"
                text += "{\\fontfamily{{cmr}}\\selectfont\n\\small\\begin{minted}"
                text += f"[bgcolor=bg, fontsize=\\small]{{{assignment['code_lang']}}}\n"
                text += code["code"].replace("\t", "    ") + "\n\end{minted}\n}\n"

        text += "\\vspace{0.5cm}\n"
        text += "\\fontfamily{lmr}\\selectfont\n"

    return text


def _tex_gen(
    assignment_list: list, gen_info: dict, doc_settings: dict, incl_solution: bool
):
    """
    Generate TeX data from assignment data. Returns TeX data as a string.

    Params:
    assignment_set: a list of assignment dictionaries in the generated set.
    gen_info: dictionary containing the lecture and course information related to the assignment set
    doc_settings: dictionary containing the TeX document settings
    """

    tex_data = ""
    begin = "\\begin{document}\n"
    pagestyle = f'\\pagestyle{{{doc_settings["document"]["pagestyle"]}}}'

    pre_content = _starting_instructions_gen(gen_info)
    content = _assignment_text_gen(gen_info, assignment_list, incl_solution)
    end = "\\end{document}"

    preamble = _preamble_gen(doc_settings, gen_info['lecture'])
    header, footer = _hdr_ftr_gen(doc_settings, gen_info)

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

    logging.info("TeX data created.")

    return tex_data


def _write_tex_file(texdata: str, filename: str):
    """
    Write 'texdata' to 'filepath'. Uses UTF-8 encoding.
    Returns True if writing is succesfull, otherwise False.

    Params:
    texdata: TeX data to write as string
    """
    # XXX should this be changed to return the exception?

    filepath = join(ENV["PROGRAM_DATA"], filename)
    try:
        with open(filepath, "w", encoding="utf-8") as tex_doc:
            tex_doc.write(texdata)

    except OSError:
        logging.exception("Exception occured when writing to file.")
        return False
    else:
        logging.info("TeX file written to %s" % filepath)
        return True


def gen_one_week(
    gen_info: dict, assignment_list: list, incl_solution: bool, filename: str
):
    """
    Generates a briefing for a spesified week.

    Params:
    gen_info: General week/course information
    assingment_list: list of assignment dicts
    incl_solution: True/False whether to include example solution
    """
    document_settings = get_texdoc_settings()

    tex_data = _tex_gen(assignment_list, gen_info, document_settings, incl_solution)

    result = _write_tex_file(tex_data, filename)

    return result
