__author__ = "albert"
# -*- coding: utf-8 -*-

from datetime import date

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


# --- build_race_history ---

# řádek závodu má tvar z Races.get_by_event:
# (id, year, date, distance, event, venue, country, url, map_m, map_w, iofurl, team)
def _race_row(race_id, year, day, distance, country="SWE"):
    return (race_id, year, date(year, 8, day), distance, "WMTBOC", "Mora", country,
            None, None, None, None, 0)


PEOPLE = {
    1: {"first": "Gabriella", "last": "Gustafsson", "nationality": "SWE", "gender": "F"},
    2: {"first": "Samuel", "last": "Pokala", "nationality": "FIN", "gender": "M"},
    3: {"first": "Hans Jorgen", "last": "Kvale", "nationality": "NOR", "gender": "M"},
    4: {"first": "Anton", "last": "Foliforov", "nationality": "RUS", "gender": "M"},
    5: {"first": "Jana", "last": "Ceska", "nationality": "CZE", "gender": "F"},
    6: {"first": "Eva", "last": "Ceska", "nationality": "CZE", "gender": "F"},
    7: {"first": "Petra", "last": "Ceska", "nationality": "CZE", "gender": "F"},
}


def test_build_race_history_two_genders_women_first():
    """
    individuální závod má dva vítěze - ženu a muže; ženy se ukazují první
    """
    history = tools.build_race_history(
        [_race_row(8775, 2026, 26, "middle")], [(8775, 1), (8775, 2)], [], PEOPLE
    )

    assert len(history) == 1
    champions = history[0]["champions"]
    assert [c["group"] for c in champions] == ["W", "M"]
    assert champions[0]["members"] == [(1, "Gabriella Gustafsson", "SWE")]
    assert champions[1]["members"] == [(2, "Samuel Pokala", "FIN")]


def test_build_race_history_tie_keeps_both_nationalities():
    """
    dělené první místo bývá napříč státy, takže vlajka patří ke jménu
    """
    history = tools.build_race_history(
        [_race_row(4702, 2014, 26, "sprint")], [(4702, 3), (4702, 4)], [], PEOPLE
    )

    champions = history[0]["champions"]
    assert len(champions) == 1
    assert champions[0]["group"] == "M"
    assert [member[2] for member in champions[0]["members"]] == ["NOR", "RUS"]


def test_build_race_history_relay_is_a_team():
    """
    štafeta má jednoho vítěze na třídu a v něm tři jezdce v pořadí legů
    """
    relay = [
        (8778, "M", "LTU", 2),
        (8778, "W", "FIN", 5),
        (8778, "W", "FIN", 6),
        (8778, "W", "FIN", 7),
    ]
    history = tools.build_race_history(
        [_race_row(8778, 2026, 30, "relay")], [], relay, PEOPLE
    )

    champions = history[0]["champions"]
    assert [c["group"] for c in champions] == ["W", "M"]
    assert all(c["team"] for c in champions)
    assert [member[0] for member in champions[0]["members"]] == [5, 6, 7]


def test_build_race_history_mix_relay_single_group():
    history = tools.build_race_history(
        [_race_row(8934, 2026, 28, "mix-relay")],
        [],
        [(8934, "X", "CZE", 5), (8934, "X", "CZE", 2)],
        PEOPLE,
    )

    champions = history[0]["champions"]
    assert len(champions) == 1
    assert champions[0]["group"] == "X"


def test_build_race_history_keeps_race_without_winner():
    """
    závod bez vítěze se nesmí zahodit - odkaz na něj je smysl té stránky
    """
    history = tools.build_race_history([_race_row(1, 2009, 10, "relay")], [], [], PEOPLE)

    assert len(history) == 1
    assert history[0]["champions"] == []


def test_build_race_history_newest_first():
    """
    v jeden den se jede víc závodů, takže řadí i datum a id
    """
    races = [
        _race_row(10, 2025, 12, "sprint"),
        _race_row(11, 2026, 26, "middle"),
        _race_row(12, 2026, 30, "long"),
    ]
    history = tools.build_race_history(races, [], [], PEOPLE)

    assert [race["race_id"] for race in history] == [12, 11, 10]


def test_build_race_history_skips_unknown_competitor():
    """
    závodník bez záznamu (např. smazaný) nesmí stránku shodit
    """
    history = tools.build_race_history(
        [_race_row(8775, 2026, 26, "middle")], [(8775, 999)], [], PEOPLE
    )

    assert history[0]["champions"] == []
