"""
Mímir Assignment Set Generator
Functions to handle the creation of pseudorandom assignment sets
"""

# pylint: disable=import-error

from datetime import date
from random import choice, choices, randint
from os.path import join

from src.constants import LANGUAGE, COURSE_INFO, OPEN_COURSE_PATH
from src.data_handler import (
    get_pos_convert,
)
from src.data_getters import (
    get_all_indexed_assignments,
    get_assignment_json,
    get_week_data,
)


def generate_one_set(
    week: int, positions: int, exclude_expanding=True
) -> list[tuple[dict, str]]:
    """
    Generate one set of assignments.
    Returns a list of tuples that contain the selected assignment data

    Params:
    week: the number of the week to generate
    positions: the number of assignment positions in the week
    exclude_expanding: Whether to exclude expanding assignments from the set.
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
        return None

    selected_list = []
    for i in range(0, positions):
        pos = []
        for item in filtered:
            if i+1 in item["exp_assignment_no"]:
                pos.append(item)

        if not pos:
            continue
        selected = select_for_position(pos)
        if selected[0]:
            ind = filtered.index(selected[0])
            filtered.pop(ind)
            selected_list.append(selected)

    return selected_list


def select_for_position(pos: list) -> tuple[dict, str]:
    """
    Select assignment for given position.

    Params:
    pos: the list of suitable assignments
    """
    weights = []
    var_int = 0  # how many variations in total
    selected = (None, None)
    for item in pos:
        for var in item["variations"]:
            weights.append(count_weight(var["used_in"]))
            var_int += 1
    all_vars = list(range(0, var_int))
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
    pos_table_keys = list(pos_table.keys())
    pos_table_keys.sort()
    pos_weights = {}
    i = 1
    for key in pos_table_keys:
        pos_weights[key] = i
        i += 1

    cur_year = date.today().year
    item_weights = []
    for item in data:
        year = int(item[-4:])
        pos = item[:-4]
        weight = pos_weights[pos] + (cur_year - year) * i + randint(0, 5)
        weight -= len(data)
        if weight <= 0:
            weight = 1
        item_weights.append(weight)

    return min(item_weights)


def generate_full_set(exclude_expanding=False) -> list[list[tuple[dict, str]]] | None:
    """
    Generate full set of assignments based on lecture week count
    Returns a list of lists that contain the selected assignment variations.

    Params:
    exclude_expanding: Whether to exclude expanding assignments from the sets
    """

    week_data = get_week_data()
    week_data["lectures"].sort(key=lambda a: a["lecture_no"])

    sets = []
    if exclude_expanding:
        for i in range(0, COURSE_INFO["course_weeks"]):
            _set = generate_one_set(
                week_data["lecture"][i]["lecture_no"],
                week_data["lecture"][i]["assignment_count"],
                exclude_expanding=True,
            )
            if _set:
                sets.append()

    else:
        _all = get_all_indexed_assignments()
        filtered = []
        for item in _all:
            if item["is_expanding"]:
                filtered.append(item)
        if not filtered:
            return None

        exp_positions = {}
        for week_n in range(0, COURSE_INFO["course_weeks"]):
            week_filtered = []
            for item in filtered:
                if int(item["position"].split(";")[0]) == i + 1:
                    week_filtered.append(get_assignment_json(item["json_path"]))

            selected = select_for_position(week_filtered)
            if selected[0]:
                ind = filtered.index(selected[0])
                filtered.pop(ind)
                positions = selected[0]["exp_assignment_no"]

                weights = []
                for i in range(0, len(selected[0]["exp_assignment_no"])):
                    weights.append(2)
                weights.append(1)
                positions.append(-1)
                pos_n = choices(positions, weights=weights)
                if pos_n != -1:
                    if str(week_n) not in exp_positions:
                        exp_positions[str(week_n)] = {}
                    if str(week_n) not in exp_positions[str(week_n)]:
                        exp_positions[str(week_n)][str(pos_n)] = selected

                    next_a = choice(selected[0]["next"])
                    choose_next(filtered, next_a, exp_positions)

            _set = generate_one_set(
                week_data["lecture"][i]["lecture_no"],
                week_data["lecture"][i]["assignment_count"],
                exclude_expanding=True,
            )
            try:
                set_pos = exp_positions[str(week_n)]
            except KeyError:
                pass
            else:
                for key in set_pos.keys():
                    if len(_set) < int(key) - 1:
                        _set.append(set_pos[key])
                    else:
                        _set[int(key) - 1] = set_pos[key]

            sets.append(_set)

    return sets


def choose_next(filtered: list, next_a: str, exp_positions: dict) -> None:
    """
    Choose the next in line for expanding assignment and place it into the
    correct spot on the exp_positions dict
    """

    item = get_assignment_json(
        join(OPEN_COURSE_PATH.get_subdir(metadata=True), next_a + ".json")
    )

    lecture = item["exp_lecture"]
    positions = item["exp_assignment_no"]
    weights = []
    for i in range(0, len(positions)):
        weights.append(2)
    positions.append(-1)
    weights.append(1)

    c_position = choices(positions, weights=weights)
    if c_position != -1:
        if str(lecture) not in exp_positions:
            exp_positions[str(lecture)] = {}
        if str(lecture) not in exp_positions[str(lecture)]:
            exp_positions[str(lecture)][str(c_position)] = item
        for i, a in enumerate(filtered):
            if a["a_id"] == next_a:
                filtered.pop(i)
        next_a = choice(item["next"])
        choose_next(filtered, next_a, exp_positions)
    else:
        return
    return


def format_set(_set:list) -> list[dict]:
    """
    Format the set to include only the correct variations

    Params:
    _set: the list of tuples that makes a set
    """

    formatted = []
    for assig in _set:
        var_letter = assig[1]
        data = assig[0]

        for i, item in enumerate(data["variations"]):
            if item["variation_id"] == var_letter:
                data["variations"] = [item]
                break
        formatted.append(data)

    return formatted
