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
    assert tools.event_codes(tools.JUNIOR) == ["JWMTBOC", "EJMTBOC"]
    assert tools.event_codes(tools.YOUTH) == ["EYMTBOC"]


def test_non_elite_codes_covers_youth():
    """
    youth i junioři dohromady - dělí se jen elita/neelita (navigace)
    """
    assert tools.non_elite_codes() == tools.event_codes({tools.JUNIOR, tools.YOUTH})
    assert "WMTBOC" not in tools.non_elite_codes()
    assert "EYMTBOC" in tools.non_elite_codes()


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


def test_youth_medals_do_not_land_in_junior_table():
    """
    Youth medaile se nesmí přičíst juniorským.

    Karta na detailu závodníka se stavěla z non_elite_codes(), což je
    "všechno kromě elity" - jakmile přibyl EYMTBOC do registru, youth
    medaile tiše spadly do juniorské tabulky. Proto se karty ptají
    event_codes(JUNIOR) a event_codes(YOUTH) zvlášť.
    """
    class OnlyYouthMedals:
        def get_competitor_place_count(self, competitor_id, place, event, table="race"):
            return [(1, 2)] if event == "EYMTBOC" else []

    junior = tools.prepare_medal_table(
        OnlyYouthMedals(), 1, events=tools.event_codes(tools.JUNIOR)
    )
    youth = tools.prepare_medal_table(
        OnlyYouthMedals(), 1, events=tools.event_codes(tools.YOUTH)
    )

    # jezdec, který jel jen youth, nesmí mít nic v juniorské tabulce
    assert "EYMTBOC" not in junior
    assert all(medals == [0, 0, 0] for medals in junior.values())
    assert youth["EYMTBOC"] == [2, 2, 2]


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


# --- build_progression ---

# řádek medaile má tvar z Results.get_individual_medals:
# (competitor_id, event, year, race_id, distance, place)
WORLD = tools.CAREER_PATHS["world"]["groups"]
FULL = tools.CAREER_PATHS["full"]["groups"]

RIDERS = {
    1: {"first": "Krystof", "last": "Bogar", "nationality": "CZE", "gender": "M"},
    2: {"first": "Susanna", "last": "Laurila", "nationality": "FIN", "gender": "F"},
    3: {"first": "Jen", "last": "Junior", "nationality": "SWE", "gender": "F"},
    4: {"first": "Jen", "last": "Elita", "nationality": "NOR", "gender": "M"},
    5: {"first": "Kaarina", "last": "Nurminen", "nationality": "FIN", "gender": "F"},
}


def test_build_progression_needs_every_stage():
    """
    kdo má medaili jen v jedné etapě, do tabulky nepatří - jde
    o přechod mezi kategoriemi, ne o seznam medailistů
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),
        (3, "JWMTBOC", 2011, 10, "long", 2),   # jen junior
        (4, "WMTBOC", 2013, 20, "sprint", 3),  # jen elita
    ]

    rows = tools.build_progression(medals, RIDERS, WORLD)

    assert [row["competitor_id"] for row in rows] == [1]


def test_build_progression_counts_medals_and_gap():
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "JWMTBOC", 2012, 11, "sprint", 2),
        (1, "WMTBOC", 2013, 20, "sprint", 1),
        (1, "WMTBOC", 2014, 21, "middle", 1),
    ]

    row = tools.build_progression(medals, RIDERS, WORLD)[0]

    assert row["stages"]["Junior"]["medals"] == [1, 1, 0]
    assert row["stages"]["Elite"]["medals"] == [2, 0, 0]
    assert row["gap"] == 2


def test_build_progression_first_medal_is_oldest():
    """
    při shodě roku rozhoduje lepší umístění - první medaile je ta,
    kterou by závodník jmenoval jako svůj průlom
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 3),
        (1, "JWMTBOC", 2011, 11, "sprint", 1),
        (1, "JWMTBOC", 2012, 12, "middle", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 2),
    ]

    first = tools.build_progression(medals, RIDERS, WORLD)[0]["stages"]["Junior"]["first"]

    assert first == (2011, 11, "sprint", 1)


def test_build_progression_place_filter_makes_champions():
    """
    place=1 dělá variantu champions - stříbro už nestačí ani k zařazení
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),
        (2, "JWMTBOC", 2009, 12, "sprint", 1),
        (2, "WMTBOC", 2012, 22, "middle", 2),  # jen stříbro v elitě
    ]

    medalists = tools.build_progression(medals, RIDERS, WORLD)
    champions = tools.build_progression(medals, RIDERS, WORLD, place=1)

    assert {row["competitor_id"] for row in medalists} == {1, 2}
    assert [row["competitor_id"] for row in champions] == [1]


def test_build_progression_sorted_by_gap_not_by_year():
    """
    Nejrychlejší přechod první.

    Řazení podle roku první elitní medaile by zvýhodňovalo starší jezdce -
    nahoru by se dostal ten, kdo závodil dřív, ne ten, kdo to zvládl
    nejrychleji. Tady má jezdec 2 starší medaile, ale delší rozestup,
    takže musí být až druhý.
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),   # gap 2, elita 2013
        (2, "JWMTBOC", 2005, 12, "sprint", 1),
        (2, "WMTBOC", 2012, 22, "middle", 1),   # gap 7, elita 2012
    ]

    rows = tools.build_progression(medals, RIDERS, WORLD)

    assert [row["competitor_id"] for row in rows] == [1, 2]
    assert [row["gap"] for row in rows] == [2, 7]


def test_build_progression_same_gap_orders_by_year():
    """
    při shodném rozestupu jde první ten starší - pořadí musí být úplné
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),
        (2, "JWMTBOC", 2009, 12, "sprint", 1),
        (2, "WMTBOC", 2011, 22, "middle", 1),
    ]

    rows = tools.build_progression(medals, RIDERS, WORLD)

    assert [row["competitor_id"] for row in rows] == [2, 1]
    assert [row["gap"] for row in rows] == [2, 2]


def test_build_progression_three_stages():
    """
    celý oblouk youth -> junior -> elita je jen delší seznam skupin,
    žádná zvláštní větev v kódu
    """
    medals = [
        (5, "EYMTBOC", 2017, 30, "sprint", 2),
        (5, "EJMTBOC", 2018, 31, "middle", 1),
        (5, "EMTBOC", 2023, 32, "long", 3),
        (1, "EJMTBOC", 2018, 31, "middle", 2),  # chybí youth
        (1, "EMTBOC", 2023, 32, "long", 1),
    ]

    rows = tools.build_progression(medals, RIDERS, FULL)

    assert [row["competitor_id"] for row in rows] == [5]
    assert rows[0]["gap"] == 6
    assert set(rows[0]["stages"]) == {"Youth", "Junior", "Elite"}


def test_build_progression_ignores_other_events():
    """
    světová větev nesmí započítat evropské tituly - jsou to dvě
    samostatné soutěže a míchat je by tabulku nafouklo
    """
    medals = [
        (1, "EJMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),
    ]

    assert tools.build_progression(medals, RIDERS, WORLD) == []


def test_build_progression_skips_unknown_competitor():
    medals = [
        (999, "JWMTBOC", 2011, 10, "long", 1),
        (999, "WMTBOC", 2013, 20, "sprint", 1),
    ]

    assert tools.build_progression(medals, RIDERS, WORLD) == []


def test_build_progression_empty_input():
    assert tools.build_progression([], RIDERS, WORLD) == []


MEDALISTS = {
    1: {"nationality": "CZE"},
    2: {"nationality": "FIN"},
    3: {"nationality": "CZE"},
    4: {"nationality": "SVK"},
    5: {"nationality": "FIN"},
}


def test_medal_countries_sorted_and_unique():
    converted = {1: [1, 0, 0], 2: [2, 0, 0], 3: [0, 1, 0]}

    assert tools.medal_countries(converted, MEDALISTS) == ["CZE", "FIN"]


def test_medal_countries_skips_unknown_competitor():
    """
    závodník mimo registr nesmí shodit stavbu seznamu vlajek
    """
    converted = {1: [1, 0, 0], 999: [1, 0, 0]}

    assert tools.medal_countries(converted, MEDALISTS) == ["CZE"]


def test_filter_medal_table_without_country_keeps_everything():
    """
    bez filtru je lokální pořadí rovno globálnímu - řádek má pořád stejný tvar
    """
    converted = {1: [2, 0, 0], 2: [1, 0, 0]}
    ranking = [(0, 1), (1, 2)]

    filtered, filtered_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS)

    assert filtered == converted
    assert filtered_ranking == [(0, 0, 1), (1, 1, 2)]


def test_filter_medal_table_keeps_only_country():
    converted = {1: [3, 0, 0], 2: [2, 0, 0], 3: [1, 0, 0], 5: [1, 0, 0]}
    ranking = [(0, 1), (1, 2), (2, 3), (3, 5)]

    filtered, filtered_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS, "CZE")

    assert filtered == {1: [3, 0, 0], 3: [1, 0, 0]}
    assert filtered_ranking == [(0, 0, 1), (1, 2, 3)]


def test_filter_medal_table_renumbers_locally_but_keeps_global():
    """
    lokální pořadí jde od nuly bez děr, globální zůstává z celého pole
    """
    converted = {2: [5, 0, 0], 5: [4, 0, 0], 1: [3, 0, 0], 3: [2, 0, 0]}
    ranking = [(0, 2), (1, 5), (2, 1), (3, 3)]

    _, filtered_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS, "FIN")

    assert [local for local, _, _ in filtered_ranking] == [0, 1]
    assert [glob for _, glob, _ in filtered_ranking] == [0, 1]

    _, cze_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS, "CZE")

    assert [local for local, _, _ in cze_ranking] == [0, 1]
    assert [glob for _, glob, _ in cze_ranking] == [2, 3]


def test_filter_medal_table_shares_local_place_on_tie():
    """
    stejný počet medailí = dělené místo i v národní tabulce
    """
    converted = {1: [1, 0, 0], 3: [1, 0, 0], 2: [1, 0, 0]}
    ranking = [(0, 1), (0, 3), (0, 2)]

    _, filtered_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS, "CZE")

    assert [local for local, _, _ in filtered_ranking] == [0, 0]


def test_filter_medal_table_country_without_medals():
    converted = {1: [1, 0, 0], 2: [1, 0, 0]}
    ranking = [(0, 1), (1, 2)]

    filtered, filtered_ranking = tools.filter_medal_table(converted, ranking, MEDALISTS, "NOR")

    assert filtered == {}
    assert filtered_ranking == []


def test_could_have_competed_elite_has_no_age_limit():
    """
    elita se jezdí bez horní hranice - i ročník 1975 tam patří
    """
    assert tools.could_have_competed(tools.EVENTS["WMTBOC"], 1975)
    assert tools.could_have_competed(tools.EVENTS["WCUP"], 1975)


def test_could_have_competed_too_old_when_event_started():
    """
    Stengard (1975) vyrostla z juniorů dávno před prvním JWMTBOC 2008
    """
    assert not tools.could_have_competed(tools.EVENTS["JWMTBOC"], 1975)
    assert not tools.could_have_competed(tools.EVENTS["EJMTBOC"], 1975)
    assert not tools.could_have_competed(tools.EVENTS["EYMTBOC"], 1975)


def test_could_have_competed_bogar():
    """
    Bogar (1994) na JWMTBOC jet mohl a jel, na EJMTBOC (2018) byl už dospělý
    """
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], 1994)
    assert not tools.could_have_competed(tools.EVENTS["EJMTBOC"], 1994)
    assert not tools.could_have_competed(tools.EVENTS["EYMTBOC"], 1994)


def test_could_have_competed_last_eligible_year_counts():
    """
    hranice: kdo je v kategorii přesně v prvním ročníku, ještě se počítá
    """
    # EJMTBOC od 2018, junior do 20 let -> ročník 1998 je akorát
    assert tools.could_have_competed(tools.EVENTS["EJMTBOC"], 1998)
    assert not tools.could_have_competed(tools.EVENTS["EJMTBOC"], 1997)

    # EYMTBOC od 2016, youth do 17 let -> ročník 1999 je akorát
    assert tools.could_have_competed(tools.EVENTS["EYMTBOC"], 1999)
    assert not tools.could_have_competed(tools.EVENTS["EYMTBOC"], 1998)


def test_could_have_competed_unknown_birth_year_shows_event():
    """
    pětina jezdců nemá v databázi rok narození - radši řádek navíc
    než zamlčená možnost
    """
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], None)
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], "")
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], "nesmysl")
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], 0)


def test_could_have_competed_accepts_year_as_string():
    """
    ze šablony chodí rok jako string
    """
    assert tools.could_have_competed(tools.EVENTS["JWMTBOC"], "1994")
    assert not tools.could_have_competed(tools.EVENTS["EJMTBOC"], "1994")
