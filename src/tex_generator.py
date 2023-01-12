"""
Mímir TeX Generator
Functions to generate instruction TeX file from available data
"""

import logging
from os.path import join

from constants import VERSION, ENV, DISPLAY_TEXTS, LANGUAGE


# pylint: disable=anomalous-backslash-in-string


def _hdr_ftr_gen(doc_settings: dict, gen_info: dict):
    """Generate header and footer
    Params:
    doc_settings: Document settings as JSON (dict)"""
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


def _preamble_gen(doc_settings):
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

    return [
        doc_class_cmd,
        font_cmd,
        extra_packages_cmd,
        margins_cmd,
        head_height,
        hyphenation_cmd,
    ]


def _starting_instructions_gen(gen_info, lecture_no):
    """
    Creates the general instructions of the instruction document
    Returns a TeX string.

    Params:
    gen_info: General instructions as a dict
    """
    week_info = gen_info["lectures"][lecture_no - 1]
    text = ""
    title = f"\\section*{{L{week_info['lecture_no']} {DISPLAY_TEXTS['tex_assignment'][LANGUAGE]}}}\n"

    topics = "\\begin{itemize}[noitemsep]\n"
    for topic in week_info["topics"]:
        topics += f"\t\\item {topic}\n"

    text += title
    text += "\\vspace{0.2cm}"
    text += topics
    text += "\\end{itemize}\n"
    text += week_info["instructions"] + "\n"
    text += "\\tableofcontents\n\\vspace{1cm}\n"

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
    if ex_file:
        text += "\\large "
    text += f"\\textbf{{{DISPLAY_TEXTS[display_text_key]}"
    if ex_file:
        text += f"'{ex_file}'"
    text += ":}}"
    text += "{\\fontfamily{{qcr}}\\selectfont\n\\begin{verbatim}\n"
    text += data + "\n\end{verbatim}\n}\n"
    text += "\\vspace{0.1cm}\n"

    return text


def _assignment_text_gen(assignment_list: list, incl_solution=False):
    """
    Creates assignment TeX string from assingment code and metadata.
    Returns a TeX string

    Params:
    assignment_list: A list of assignments as dicts containing assingment information
    """

    # Assignment dict:
    # lecture, title, instructions, example_runs(dict) datafile(s)(list of dicts), examplecode(s)
    # Example run dict:
    # input, output, outputfile, CMD
    # Datafile dict:
    # filename, data

    # TODO Add numbered list generator for lines starting with '-'

    text = ""
    for i, assignment in enumerate(assignment_list):
        text += f"\\addsec{{L{assignment['lecture']}T{i:02d}: {assignment['title']}}}\n"
        text += assignment["instructions"] + "\n"
        text += "\\vspace{0.1cm}\n"

        for datafile in assignment["datafiles"]:
            text += _block_gen("tex_ex_input_datafile", datafile["data"], datafile["filename"])

        for i, example_run in enumerate(assignment["example_runs"]):
            text += (
                f"\n\\large\\textbf{{{DISPLAY_TEXTS['tex_ex_run'][LANGUAGE]}{i+1}}}\n"
            )
            text += "\\vspace{0.1cm,}\n"
            if example_run["CMD"]:
                text += _block_gen("tex_cmd_input", example_run["CMD"])
            if example_run["input"]:
                text += _block_gen("tex_ex_input", example_run["input"])
            if example_run["output"]:
                text += _block_gen("tex_ex_output", example_run["output"])
            if example_run["outputfiles"]:
                for resultfile in example_run["outputfiles"]:
                    text += _block_gen("tex_ex_resultfile", resultfile["data"], resultfile["filename"])

        if incl_solution:
            text += f"\\textbf{{{DISPLAY_TEXTS['tex_ex_solution'][LANGUAGE]}}}\n"
            text += "{\\fontfamily{{qcr}}\\selectfont\n\\begin{verbatim}\n"
            text += assignment.replace("\t", "    ") + "\end{verbatim}\n}\n"

        text += "\\vspace{0.5cm}\n"

    return text


def tex_gen(assignment_set: dict, lecture_info: dict, doc_settings: dict):
    """
    Generate TeX data from assignment data. Returns TeX data as a string.

    Params:
    assignment_set: a dictionary containing the generated assignment set.
    lecture_info: a dictionary containing the lecture information related to the assignment set
    doc_settings: a dictionary containing the TeX document settings
    """

    # TODO Refactor to use new parameters
    tex_data = ""
    begin = "\\begin{document}\n"
    pagestyle = f'\\pagestyle{{{doc_settings["document"]["pagestyle"]}}}'

    pre_content = _starting_instructions_gen(gen_info)
    content = _assignment_text_gen(assignment_metadata, assignment)
    end = "\\end{document}"

    preamble = _preamble_gen(doc_settings)
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

    return tex_data


def write_tex_file(texdata: str):
    """
    Write 'texdata' to 'filepath'. Uses UTF-8 encoding.
    Returns True if writing is succesfull, otherwise False.

    Params:
    texdata: TeX data to write as string
    """
    # XXX should this be changed to return the exception?

    filepath = join(ENV["PROGRAM_DATA"], "output.tex")
    try:
        with open(filepath, "w", encoding="utf-8") as tex_doc:
            tex_doc.write(texdata)

    except OSError:
        logging.exception("Exception occured when writing to file.")
        return False
    else:
        return True
