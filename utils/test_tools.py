__author__ = "albert"
# -*- coding: utf-8 -*-

from utils import tools


def test_base_dict():
    """
    test pro vyslednou funkci merge tuples
    """
    line_a = ((1, 3), (3, 4), (10, 2))
    line_b = ((1, 2), (2, 4), (5, 2))
    line_c = ((1, 5), (3, 2), (7, 3))

    expected_result = {
        1: [0, 0, 0],
        2: [0, 0, 0],
        3: [0, 0, 0],
        5: [0, 0, 0],
        7: [0, 0, 0],
        10: [0, 0, 0],
    }

    assert expected_result == tools.create_base_dict(line_a, line_b, line_c)


def test_merge_tuples():
    """
    test pro vyslednou funkci merge tuples
    """
    line_a = ((1, 3), (3, 4), (10, 2))
    line_b = ((1, 2), (2, 4), (5, 2))
    line_c = ((1, 5), (3, 2), (7, 3))

    expected_result = {
        1: [3, 2, 5],
        2: [0, 4, 0],
        3: [4, 0, 2],
        5: [0, 2, 0],
        7: [0, 0, 3],
        10: [2, 0, 0],
    }

    assert expected_result == tools.merge_medal_lines(line_a, line_b, line_c)


def test_merge_medal_dicts():
    rank_a = {270: [2, 2, 2], 313: [2, 1, 1]}
    rank_b = {270: [1, 1, 0], 230: [1, 1, 1]}

    expected_result = {270: [3, 3, 2], 313: [2, 1, 1], 230: [1, 1, 1]}

    assert expected_result == tools.merge_medal_dicts(rank_a, rank_b)
