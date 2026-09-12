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


def test_results_link_iof_archive():
    """
    staré závody: iofurl pod 1000 je ID v IOF archivu
    """
    race = {"race_id": 3887, "iofurl": 48}

    assert tools.results_link(race) == (
        "IOF results page",
        "https://old.orienteering.sport/events/48/",
    )


def test_results_link_eventor_from_iofurl():
    """
    iofurl nad 1000 je eventorové ID závodu, který má vlastní primární klíč
    (junioři 2018/2019 vytažení z elitního XML)
    """
    race = {"race_id": 100006, "iofurl": 5964}

    assert tools.results_link(race) == (
        "Eventor results page",
        "https://eventor.orienteering.sport/Events/Show/5964",
    )


def test_results_link_eventor_from_race_id():
    """
    bez iofurl je eventorové ID rovnou primární klíč
    """
    race = {"race_id": 8503, "iofurl": None}

    assert tools.results_link(race) == (
        "Eventor results page",
        "https://eventor.orienteering.sport/Events/Show/8503",
    )


def test_results_link_legacy_relay():
    """
    staré štafety (id 1-23) v Eventoru nejsou, jejich id není eventorové
    """
    assert tools.results_link({"race_id": 1, "iofurl": None}) is None
    assert tools.results_link({"race_id": 23, "iofurl": None}) is None


def test_results_link_without_any_id():
    """
    bez obou identifikátorů odkaz sestavit nejde
    """
    assert tools.results_link({"race_id": None, "iofurl": None}) is None
