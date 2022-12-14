"""
Mímir TeX Generator
Functions to generate instruction TeX file from available data
"""

import logging
import sys

from constants import VERSION


# pylint: disable=anomalous-backslash-in-string

def hdr_ftr_gen(doc_settings: dict, gen_info: dict):
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


def preamble_gen(doc_settings):
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


def starting_instructions_gen(gen_info):
    """
    Creates the general instructions of the instruction document
    Returns a TeX string.

    Params:
    gen_info: General instructions as a JSON string
    """
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
    """
    Creates assignment TeX string from assingment code and metadata.
    Returns a TeX string

    Params:
    metadata: a list of assignment metadata JSON strings
    assignment_list: A list of assignment codes as strings
    """

    #TODO add commandline arguments, example datafiles and example result files
    #TODO Add option to not include example code for student instructions.

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
    """
    Generate TeX data from assignment data. Returns TeX data as a string.
    Params:

    """

    #TODO refactor to use data_path_handler
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
    """
    Write 'texdata' to 'filepath'
    Uses UTF-8 encoding.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as tex_doc:
            tex_doc.write(texdata)

    except OSError as e:  # pylint: disable=invalid-name
        logging.exception("Exception occured when writing to file.")
        print(e)
        sys.exit(0)
