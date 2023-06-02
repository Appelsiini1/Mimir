"""
Mímir Assignment Set Generator
Functions to handle the creation of pseudorandom assignment sets
"""

# pylint: disable=import-error

from datetime import date
from random import choices

from src.tex_generator import gen_one_week
from src.constants import LANGUAGE
from src.data_handler import (
    get_pos_convert,
)
from src.data_getters import get_all_indexed_assignments, get_assignment_json


def generate_one_set(week: int, positions: int, exclude_expanding=False):
    """
    Generate one set of assignments.

    Params:
    week: the number of the week to generate
    positions: the number of assignment positions in the week
    """

    _all = get_all_indexed_assignments()
    filtered = []

    for item in _all:
        if exclude_expanding:
            if int(item["position"].split(";")[0]) == week and not item["is_expanding"]:
                filtered.append(get_assignment_json(item["json_path"]))
        else:
            if int(item["position"].split(";")[0]) == week:
                filtered.append(get_assignment_json(item["json_path"]))

    if not filtered:
        return

    selected_list = []
    for i in range(0, positions):
        pos = []
        for item in filtered:
            if i in item["exp_assignment_no"]:
                pos.append(item)
        selected = select_for_position(pos)
        if selected[0]:
            ind = filtered.index(selected[0])
            filtered.pop(ind)
            selected_list.append(selected)


def select_for_position(pos: list) -> tuple[dict, str]:
    """
    Select assignment for given position.

    Params:
    filtered: the list of suitable assignments
    """
    weights = []
    var_int = 0  # how many variations in total
    selected = (None, None)
    for item in pos:
        for var in item["variations"]:
            weights.append(count_weight(var["used_in"]))
            var_int += 1
    all_vars = range(0, var_int)
    selection = choices(all_vars, weights=weights)
    if selection[0] == 0:
        selected = (pos[0], pos[0]["variations"][0]["variation_id"])
    else:
        x = 0
        for item in pos:
            for var in item["variations"]:
                x += 1
                if x == selection[0]:
                    selected = (item, var["variation_id"])

    return selected


def count_weight(data: list) -> int:
    """
    Counts the weight the variation gets based on the 'used in' list

    Params:
    data: a list of previous times the assignment has been used in.
    """

    if not data:
        return 1

    pos_table: dict = get_pos_convert()[LANGUAGE.get()]
    pos_table_keys = list(pos_table.keys()).sort()
    pos_weights = {}
    i = 1
    for key in pos_table_keys:
        pos_weights[key] = i
        i += 1

    cur_year = date.today().year
    item_weights = []
    for item in data:
        year = int(item[-4:])
        pos = int(item[:-4])
        weight = pos_weights[pos] + (cur_year - year) * i
        weight -= len(data)
        if weight < 0:
            weight = 1
        item_weights.append(weight)

    return min(item_weights)
