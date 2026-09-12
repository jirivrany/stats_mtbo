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


def test_event_codes_order_and_filter():
    """
    registr drží pořadí zobrazení a umí filtrovat po kategoriích
    """
    assert tools.event_codes()[:3] == ["WMTBOC", "EMTBOC", "WCUP"]
    assert tools.event_codes(tools.ELITE) == ["WMTBOC", "EMTBOC", "WCUP"]
    assert tools.event_codes({tools.JUNIOR, tools.YOUTH}) == ["JWMTBOC", "EJMTBOC"]


def test_non_elite_codes_covers_youth():
    """
    youth se má chytit sám, až přibude - proto se ptáme "není elita"
    """
    assert tools.non_elite_codes() == tools.event_codes({tools.JUNIOR, tools.YOUTH})
    assert "WMTBOC" not in tools.non_elite_codes()


def test_get_event_is_case_insensitive():
    """
    v URL chodí kódy malými písmeny
    """
    assert tools.get_event("jwmtboc")["kind"] == tools.JUNIOR
    assert tools.get_event("JWMTBOC")["name"].startswith("Junior")
    assert tools.get_event("nonsense") is None
    assert tools.get_event("") is None


def test_is_junior():
    assert tools.is_junior("JWMTBOC")
    assert tools.is_junior("ejmtboc")
    assert not tools.is_junior("WMTBOC")
    assert not tools.is_junior("nonsense")


def test_wcup_scoring_excludes_juniors():
    """
    juniorské závody se jedou ve stejné roky jako elitní, ale do
    Světového poháru nepatří - bez toho lezly do tabulek jako prázdné sloupce
    """
    scoring = tools.wcup_scoring_events()

    assert scoring == ["WMTBOC", "EMTBOC", "WCUP"]
    assert not any(tools.is_junior(code) for code in scoring)


def test_prepare_medal_table_keeps_groups_apart():
    """
    juniorské a elitní medaile se nesmí sčítat, tak se tabulka staví zvlášť
    """
    class FakeModel:
        def get_competitor_place_count(self, competitor_id, place, event, table="race"):
            return [(1, 1)] if event == "JWMTBOC" else []

    elite = tools.prepare_medal_table(FakeModel(), 1, events=tools.event_codes(tools.ELITE))
    junior = tools.prepare_medal_table(FakeModel(), 1, events=tools.non_elite_codes())

    assert list(elite) == ["WMTBOC", "EMTBOC", "WCUP"]
    assert all(medals == [0, 0, 0] for medals in elite.values())
    assert junior["JWMTBOC"] == [1, 1, 1]
    assert junior["EJMTBOC"] == [0, 0, 0]
