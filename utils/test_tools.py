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


def test_category_badge():
    """
    Odznak se odvozuje z kind, ne z výčtu kódů - jinak by nová událost
    na rozcestí zůstala bez odznaku a nikdo by si toho nevšiml.
    """
    assert tools.category_badge("EYMTBOC")["label"] == "Youth"
    assert tools.category_badge("ejmtboc")["label"] == "Junior"
    assert tools.category_badge("U23WCUP")["label"] == "U23"
    assert tools.category_badge("nonsense") is None


def test_elite_has_no_badge():
    """
    Elita je výchozí stav, ne výjimka - odznak by nesla většina řádků
    a přestal by být vidět. Chybějící odznak tedy znamená elitu.
    """
    for code in tools.event_codes(tools.ELITE):
        assert tools.category_badge(code) is None, code


def test_every_non_elite_event_has_a_badge():
    """
    Každá neelitní událost musí mít odznak. Až přibude další kategorie,
    tenhle test spadne dřív, než se na rozcestí objeví řádek bez odznaku.
    """
    for code in tools.event_codes():
        if tools.get_event(code)["kind"] == tools.ELITE:
            continue
        assert tools.category_badge(code), code


def test_world_cup_has_no_grand_slam():
    """
    Pohár Grand Slam nemá. Věcně to není cíl - program seriálu se mění
    ročník od ročníku. Datově to navíc vycházelo špatně: do Poháru se
    počítají i závody WMTBOC a EMTBOC, takže se vítězství z mistrovství
    míchala do seriálu.
    """
    assert not tools.has_grand_slam("WCUP")
    assert not tools.has_grand_slam("wcup")
    assert not tools.has_grand_slam("U23WCUP")
    assert "WCUP" not in tools.grand_slam_codes()
    assert "U23WCUP" not in tools.grand_slam_codes()


def test_championships_keep_grand_slam():
    """mistrovství mají stálý program, takže tam Grand Slam zůstává"""
    assert tools.has_grand_slam("WMTBOC")
    assert tools.has_grand_slam("emtboc")
    assert tools.has_grand_slam("JWMTBOC")
    assert not tools.has_grand_slam("nonsense")


def test_grand_slam_menu_is_world_championships_only():
    """
    V menu jsou jen světová mistrovství a EMTBOC. Evropské juniorské
    a mládežnické se počítají a stránku mají, ale do menu nejdou -
    šest položek Grand Slamu by v něm to podstatné utopilo.
    """
    assert tools.grand_slam_menu_codes() == ["WMTBOC", "EMTBOC", "JWMTBOC"]
    assert "EJMTBOC" not in tools.grand_slam_menu_codes()
    assert "EYMTBOC" not in tools.grand_slam_menu_codes()


def test_grand_slam_menu_only_links_to_pages_that_exist():
    """
    Do menu nesmí přijít soutěž bez Grand Slamu - odkaz by vedl na 404.
    Menu je podmnožina toho, co se počítá.
    """
    for code in tools.grand_slam_menu_codes():
        assert tools.has_grand_slam(code), code

    assert set(tools.grand_slam_menu_codes()) <= set(tools.grand_slam_codes())


def test_grand_slam_never_covers_a_wcup_scoring_series():
    """
    Grand Slam nesmí být u soutěže, do které bodují jiné soutěže -
    přesně tím byl Pohár rozbitý. Kdyby takový seriál přibyl, spadne
    to tady, ne až v tabulce.
    """
    scoring = set(tools.wcup_scoring_events()) | set(tools.u23_scoring_events())

    for code in tools.grand_slam_codes():
        meta = tools.EVENTS[code]
        # Vadí jen seriál, do kterého přispívají cizí závody, ne to,
        # že mistrovství samo někam boduje.
        assert not meta["needs_organizer"] or code not in scoring, code


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

# Datum narození je tu proto, že se podle věku řadí. Ročníky jsou
# nastavené tak, aby medaile v testech vycházely na rozumný věk
# (junior 16-20, elita 19+).
RIDERS = {
    1: {"first": "Krystof", "last": "Bogar", "nationality": "CZE", "gender": "M",
        "born": "1994-01-01"},
    2: {"first": "Susanna", "last": "Laurila", "nationality": "FIN", "gender": "F",
        "born": "1991-01-01"},
    3: {"first": "Jen", "last": "Junior", "nationality": "SWE", "gender": "F",
        "born": "1993-01-01"},
    4: {"first": "Jen", "last": "Elita", "nationality": "NOR", "gender": "M",
        "born": "1993-01-01"},
    5: {"first": "Kaarina", "last": "Nurminen", "nationality": "FIN", "gender": "F",
        "born": "2002-01-01"},
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

    assert first == (2011, 11, "sprint", 1, "JWMTBOC")


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


def test_build_progression_sorted_by_age_not_by_year():
    """
    Nejmladší elitní medailista první.

    Řazení podle roku první elitní medaile by zvýhodňovalo starší jezdce -
    nahoru by se dostal ten, kdo závodil dřív, ne ten, kdo to zvládl
    nejmladší.
    """
    medals = [
        (1, "JWMTBOC", 2011, 10, "long", 1),
        (1, "WMTBOC", 2013, 20, "sprint", 1),   # Bogar *1994 -> elita v 19
        (2, "JWMTBOC", 2009, 12, "sprint", 1),
        (2, "WMTBOC", 2012, 22, "middle", 1),   # Laurila *1991 -> elita v 21
    ]

    rows = tools.build_progression(medals, RIDERS, WORLD)

    assert [row["competitor_id"] for row in rows] == [1, 2]
    assert [row["elite_age"] for row in rows] == [19, 21]


def test_build_progression_age_beats_short_gap():
    """
    Klíčový případ, kvůli kterému se od rozestupu odešlo.

    Kdo vezme juniorskou medaili až ve 20, tedy v nejsilnějším ročníku
    kategorie, a elitní ve 22, má rozestup jen 2 roky. Kdo prorazí v 17
    a pak čeká, než ho federace pustí do elity, má rozestup 5 let - ale
    elitní medaili má ve stejném věku. Kratší rozestup tady nesmí vyhrát.
    """
    medals = [
        (2, "JWMTBOC", 2011, 10, "long", 1),    # Laurila *1991 -> junior ve 20
        (2, "WMTBOC", 2013, 20, "sprint", 1),   # elita ve 22, rozestup 2
        (1, "JWMTBOC", 2011, 12, "sprint", 1),  # Bogar *1994 -> junior v 17
        (1, "WMTBOC", 2016, 22, "middle", 1),   # elita ve 22, rozestup 5
    ]

    rows = tools.build_progression(medals, RIDERS, WORLD)

    assert [row["competitor_id"] for row in rows] == [1, 2]
    assert [row["gap"] for row in rows] == [5, 2]
    assert [row["first_age"] for row in rows] == [17, 20]


def test_build_progression_missing_birth_goes_last():
    """
    bez data narození se věk spočítat nedá - řádek ale z tabulky
    vypadnout nesmí, jen se propadne na konec
    """
    riders = dict(RIDERS)
    riders[3] = {"first": "Jen", "last": "Junior", "nationality": "SWE", "gender": "F"}

    medals = [
        (3, "JWMTBOC", 2009, 10, "long", 1),
        (3, "WMTBOC", 2011, 20, "sprint", 1),
        (1, "JWMTBOC", 2011, 12, "sprint", 1),
        (1, "WMTBOC", 2013, 22, "middle", 1),
    ]

    rows = tools.build_progression(medals, riders, WORLD)

    assert [row["competitor_id"] for row in rows] == [1, 3]
    assert rows[1]["elite_age"] is None


def test_birth_year_handles_missing_and_junk():
    assert tools.birth_year({"born": "1994-05-06"}) == 1994
    assert tools.birth_year({"born": ""}) is None
    assert tools.birth_year({"born": None}) is None
    assert tools.birth_year({}) is None
    assert tools.birth_year(None) is None
    assert tools.birth_year({"born": "necoSpatne"}) is None


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


def test_build_progression_merged_stage_takes_either_event():
    """
    v celém oblouku stačí na juniorech i elitě medaile ze světa NEBO
    z Evropy - jinak by vypadl každý, kdo vyjel z Evropy ven
    """
    medals = [
        (5, "EYMTBOC", 2016, 30, "sprint", 1),
        (5, "JWMTBOC", 2018, 31, "long", 1),  # světová, ne evropská
        (5, "WMTBOC", 2024, 32, "mass-start", 1),
    ]

    rows = tools.build_progression(medals, RIDERS, FULL)

    assert [row["competitor_id"] for row in rows] == [5]
    assert rows[0]["gap"] == 8


def test_build_progression_merged_stage_sums_both_events():
    """
    sloučená etapa sčítá medaile z obou soutěží a průlom je ta nejstarší
    z nich - u sloučené etapy si `first` veze i kód, odkud medaile je
    """
    medals = [
        (5, "EYMTBOC", 2016, 30, "sprint", 2),
        (5, "JWMTBOC", 2018, 31, "long", 1),
        (5, "EJMTBOC", 2019, 32, "middle", 1),
        (5, "EMTBOC", 2023, 33, "long", 3),
    ]

    junior = tools.build_progression(medals, RIDERS, FULL)[0]["stages"]["Junior"]

    assert junior["medals"] == [2, 0, 0]
    assert junior["first"] == (2018, 31, "long", 1, "JWMTBOC")


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


GARDE = {"nationality": "FRA", "nat_history": [("SVK", 2005, 2012), ("FRA", 2014, None)]}
BALLOT = {"nationality": "SUI", "nat_history": [("FRA", 2004, 2007)]}


def test_nationality_in_without_history_returns_current():
    """
    drtivá většina závodníků historii nemá - rychlá cesta bez dohledávání
    """
    assert tools.nationality_in({"nationality": "CZE"}, 2009) == "CZE"


def test_nationality_in_picks_the_right_stint():
    """
    Garde jela do 2012 za Slovensko, od 2014 za Francii
    """
    assert tools.nationality_in(GARDE, 2005) == "SVK"
    assert tools.nationality_in(GARDE, 2012) == "SVK"
    assert tools.nationality_in(GARDE, 2014) == "FRA"
    assert tools.nationality_in(GARDE, 2017) == "FRA"


def test_nationality_in_gap_year_falls_to_later_stint():
    """
    2013 Garde nezávodila, rok mezi úseky nesmí spadnout na chybu
    """
    assert tools.nationality_in(GARDE, 2013) == "FRA"


def test_nationality_in_before_first_stint():
    """
    rok před prvním úsekem bere nejbližší, ne dnešní registraci
    """
    assert tools.nationality_in(GARDE, 2004) == "SVK"
    assert tools.nationality_in(BALLOT, 2003) == "FRA"


def test_nationality_in_after_closed_stint_keeps_history():
    """
    Ballot jela za Francii, dnes je v Eventoru jako Švýcarsko - staré
    výsledky musí zůstat francouzské
    """
    assert tools.nationality_in(BALLOT, 2005) == "FRA"
    assert tools.nationality_in(BALLOT, 2020) == "FRA"


def test_nationality_in_open_ended_stint():
    """
    valid_to NULL = trvá dosud
    """
    stengard = {"nationality": "FIN", "nat_history": [("FIN", 2002, 2025), ("SWE", 2026, None)]}

    assert tools.nationality_in(stengard, 2025) == "FIN"
    assert tools.nationality_in(stengard, 2026) == "SWE"
    assert tools.nationality_in(stengard, 2030) == "SWE"


def test_nationality_in_handles_year_as_string_and_junk():
    assert tools.nationality_in(GARDE, "2009") == "SVK"
    assert tools.nationality_in(GARDE, None) == "FRA"
    assert tools.nationality_in(GARDE, "nesmysl") == "FRA"


# Ruská federace 2021 - kvůli dopingu start pod vlajkou IOF jako neutrálové.
# Foliforov má kariéru přes celý ten zlom, Shvedov začal až v neutrálním roce.
FOLIFOROV = {"nationality": "RUS", "nat_history": [("RUS", 2005, 2020), ("NEU", 2021, 2021)]}
SHVEDOV = {"nationality": "RUS", "nat_history": [("NEU", 2021, 2021)]}


def test_nationality_in_neutral_year_is_only_2021():
    """
    Neutrální je opravdu jen ten jeden rok - medaile z dřívějška
    zůstávají Rusku, jinak by se přepsala celá kariéra.
    """
    assert tools.nationality_in(FOLIFOROV, 2005) == "RUS"
    assert tools.nationality_in(FOLIFOROV, 2020) == "RUS"
    assert tools.nationality_in(FOLIFOROV, 2021) == "NEU"


def test_nationality_in_neutral_only_career():
    """
    Kdo poprvé startoval až 2021, za Rusko nezávodil nikdy - dnešní
    registrace v Eventoru (RUS) se na výsledky propsat nesmí.
    """
    assert tools.nationality_in(SHVEDOV, 2021) == "NEU"


def test_neutral_code_has_a_flag():
    """
    Šablony sahají na IOC_INDEX[kód] bez ošetření, takže chybějící NEU
    by shodilo každou stránku s výsledkem z roku 2021.
    """
    assert "NEU" in tools.IOC_INDEX


SWITCHER = {
    270: {"nationality": "FRA", "nat_history": [("SVK", 2005, 2012), ("FRA", 2014, None)]},
    99: {"nationality": "CZE"},
}


def test_medals_for_country_splits_by_era():
    """
    Garde má individuální medaile za obě země - každá tabulka jen svoje
    """
    by_year = {(270, 2008): [1, 0, 0], (270, 2009): [1, 0, 1], (270, 2015): [0, 0, 1]}

    svk = tools.medals_for_country(by_year, SWITCHER, "SVK")
    fra = tools.medals_for_country(by_year, SWITCHER, "FRA")

    assert svk == {270: [2, 0, 1]}
    assert fra == {270: [0, 0, 1]}


def test_medals_for_country_skips_competitor_without_medals_there():
    by_year = {(270, 2008): [1, 0, 0], (99, 2008): [0, 1, 0]}

    assert tools.medals_for_country(by_year, SWITCHER, "SVK") == {270: [1, 0, 0]}
    assert tools.medals_for_country(by_year, SWITCHER, "CZE") == {99: [0, 1, 0]}


def test_relay_medals_for_country_uses_team_not_nationality():
    """
    u štafet drží zemi competitor_relay.team, rok se dohledávat nemusí
    """
    lines = [
        [(270, "SVK", 1)],
        [(270, "FRA", 1)],
        [(270, "SVK", 2), (99, "CZE", 1)],
    ]

    assert tools.relay_medals_for_country(lines, "SVK") == {270: [1, 0, 2]}
    assert tools.relay_medals_for_country(lines, "FRA") == {270: [0, 1, 0]}
    assert tools.relay_medals_for_country(lines, "CZE") == {99: [0, 0, 1]}


def test_aggregate_relay_medals_by_team_counts_competitors():
    """
    pruh vlajek počítá jednotlivce, ne týmy - jeden bronz štafety = tři medaile
    """
    lines = [[], [], [(1, "CZE", 1), (2, "CZE", 1), (3, "CZE", 1)]]

    assert tools.aggregate_relay_medals_by_team(lines) == {"CZE": [0, 0, 3]}


def test_filter_medal_table_by_country_overrides_nationality():
    """
    hotové počty za zemi mají přednost před dnešní národností
    """
    converted = {270: [2, 0, 1], 99: [1, 0, 0]}
    ranking = [(0, 270), (1, 99)]
    by_country = {270: [1, 0, 1]}

    filtered, filtered_ranking = tools.filter_medal_table(
        converted, ranking, SWITCHER, "SVK", by_country
    )

    assert filtered == {270: [1, 0, 1]}
    assert filtered_ranking == [(0, 0, 270)]


def test_format_place_keeps_real_places():
    assert tools.format_place(1) == "1"
    assert tools.format_place(120) == "120"
    assert tools.format_place("7") == "7"


def test_format_place_uses_status_from_time_column():
    """
    důvod je v databázi ve sloupci s časem - DSQ nesmí vypadat jako nedokončeno
    """
    assert tools.format_place(9999, "DSQ") == "DSQ"
    assert tools.format_place(99999, "NC") == "NC"
    assert tools.format_place(9999, "dsq") == "DSQ"


def test_format_place_without_status_falls_back():
    """
    od 2015 je u nedokončených závodů čas prázdný
    """
    assert tools.format_place(99999) == "nc"
    assert tools.format_place(99999, "") == "nc"
    assert tools.format_place(9999, "1:23:45") == "nc"


def test_format_place_handles_missing_value():
    assert tools.format_place(None) == ""
    assert tools.format_place("") == ""


def test_team_worldcup_keeps_best_team_of_federation():
    """
    Pravidla IOF: "only the best placed team of each federation shall be
    considered". Federace může postavit druhý tým, ten jede jako `reduced`
    bez místa a bez bodů. Dřív o výsledku rozhodovalo pořadí řádků
    z databáze, takže nulový druhý tým přepsal ten bodující.

    Data jsou skutečná - LTU na EMTBOC 2026 mix-relay (závod 8934).
    """
    rows = [
        (6568, 8934, "LTU", 17),
        (24215, 8934, "LTU", 0),
        (10248, 8934, "LTU", 0),
        (13160, 8934, "LTU", 17),
        (19787, 8934, "LTU", 0),
        (23324, 8934, "LTU", 17),
    ]

    base, races = tools.make_team_worldup_results_base(rows, "X")

    assert races == {"8934-X"}
    assert base["LTU"]["8934-X"]["points"] == 17
    assert sorted(base["LTU"]["8934-X"]["members"]) == [6568, 13160, 23324]


def test_team_worldcup_keeps_members_of_scoreless_team():
    """
    Tým bez bodů (diskvalifikace, 16. místo a dál) se musí v sestavě
    objevit taky - jinak by zmizel ze seznamu závodníků.
    """
    rows = [(1, 8934, "TUR", 0), (2, 8934, "TUR", 0), (3, 8934, "TUR", 0)]

    base, _ = tools.make_team_worldup_results_base(rows, "X")

    assert base["TUR"]["8934-X"]["points"] == 0
    assert sorted(base["TUR"]["8934-X"]["members"]) == [1, 2, 3]


def test_is_u23_uses_season_year_not_race_date():
    """
    "up to the end of the calendar year in which they have their 23rd
    birthday" - jezdec je U23 celou sezónu. Ověřeno na 2026: ročník 2003
    ještě patří, 2002 už ne.
    """
    assert tools.is_u23(2003, 2026) is True
    assert tools.is_u23(2002, 2026) is False
    assert tools.is_u23(2004, 2026) is True


def test_is_u23_excludes_unknown_birth_year():
    """
    Opak could_have_competed() - do oficiálního pořadí se nesmí dostat
    jezdec, u kterého nevíme, jestli tam patří.
    """
    for unknown in (None, "", "nesmysl", 0, 1800):
        assert tools.is_u23(unknown, 2026) is False


def test_u23_places_renumber_from_elite_results():
    """Z elitních míst se stane pořadí 1..n."""
    rows = [(7, "a"), (14, "b"), (16, "c"), (18, "d")]

    assert tools.u23_places(rows) == [
        (1, (7, "a")),
        (2, (14, "b")),
        (3, (16, "c")),
        (4, (18, "d")),
    ]


def test_u23_places_keep_shared_places_shared():
    """
    Skutečný případ - WMTBOC 2026 middle (závod 8775): Nowak a Klemettinen
    dojeli oba na 36. místě ve stejném čase. Oba jsou U23 osmí a další
    v pořadí je desátý, ne devátý. Prosté číslování 1..n posune všechny
    pod nimi a body přestanou sedět s oficiální tabulkou IOF.
    """
    rows = [(20, "Hnilica"), (36, "Nowak"), (36, "Klemettinen"), (40, "Janowski")]

    numbered = tools.u23_places(rows)

    assert [pair[0] for pair in numbered] == [1, 2, 2, 4]


def test_u23_scoring_events_are_separate_from_elite():
    """
    U23 nesmí být v elitním seznamu - wcup_scoring_events() řídí elitní
    stránky Poháru a U23 řádky by do nich přitekly jako cizí body.
    Málem se to stalo: stačilo dát U23 událostem scores_wcup=True.
    """
    elite = tools.wcup_scoring_events()
    u23 = tools.u23_scoring_events()

    assert sorted(elite) == ["EMTBOC", "WCUP", "WMTBOC"]
    assert sorted(u23) == ["U23WCUP", "U23WMTBOC"]
    assert not set(elite) & set(u23)


def test_standings_link_can_be_derived_from_registry():
    """
    Rozcestí na hlavní straně vybírá odkaz na průběžné pořadí podle
    needs_organizer a scores_u23_wcup. Dřív tam byl natvrdo /worldcup/,
    takže karta U23WCUP odkazovala na elitní Pohár.

    Každá událost s needs_organizer musí patřit právě do jednoho Poháru,
    jinak by se z registru nedalo poznat, kam odkázat.
    """
    for code in tools.event_codes():
        meta = tools.EVENTS[code]
        if not meta["needs_organizer"]:
            continue

        elite = bool(meta.get("scores_wcup"))
        u23 = bool(meta.get("scores_u23_wcup"))

        assert elite != u23, code


def test_u23_counted_is_one_below_elite():
    """
    Do U23 Poháru se počítá o jeden výsledek míň, protože dlouhá trať
    na MS do U23 neboduje. Ročníky musí sedět s WCUP_COUNTED v aplikaci.
    """
    assert tools.U23_WCUP_COUNTED == {2022: 5, 2023: 6, 2024: 6, 2025: 6, 2026: 6}


def test_scores_for_u23_excludes_only_wmtboc_long():
    assert tools.scores_for_u23("WMTBOC", "long") is False
    assert tools.scores_for_u23("WMTBOC", "sprint") is True
    assert tools.scores_for_u23("WCUP", "long") is True
    assert tools.scores_for_u23("EMTBOC", "long") is True


# --- Perfect Championship: nejlepší jednotlivý šampionát ---

PERFECT_COMPETITORS = {
    1: {"first": "Anna", "last": "Alpha", "nationality": "CZE"},
    2: {"first": "Bela", "last": "Beta", "nationality": "FIN"},
    3: {"first": "Cyril", "last": "Gamma", "nationality": "SWE"},
}


def test_perfect_championship_olympic_order():
    """
    Rozhoduje zlato, při shodě stříbro, pak bronz. Tři zlata a stříbro
    jsou víc než tři zlata a dva bronzy - kvůli tomuhle pravidlu to
    nejde řadit podle součtu medailí.
    """
    by_year = {
        (1, 2019): [3, 0, 2],
        (2, 2021): [3, 1, 0],
        (3, 2024): [4, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [key for _, key, _, _ in table] == [(3, 2024), (2, 2021), (1, 2019)]


def test_perfect_championship_shares_rank_and_skips():
    """
    Stejná bilance = stejné pořadí, další v řadě přeskočí. Po dvou
    druhých je čtvrtý, ne třetí.
    """
    by_year = {
        (1, 2019): [4, 0, 0],
        (2, 2021): [3, 1, 0],
        (3, 2024): [3, 1, 0],
        (1, 2022): [2, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [rank for rank, _, _, _ in table] == [0, 1, 1, 3]


def test_perfect_championship_years_are_not_summed():
    """
    Jednotkou je jeden šampionát, ne kariéra. Čtyři zlata ze dvou ročníků
    zůstávají dvěma řádky po dvou - jinak by to byl Grand Slam a vyšlo
    by z toho jedno čtyřzlaté mistrovství, které se nikdy nekonalo.
    """
    by_year = {
        (1, 2019): [2, 0, 0],
        (1, 2021): [2, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert len(table) == 2
    assert all(medals == [2, 0, 0] for _, _, medals, _ in table)


def test_perfect_championship_hides_rows_without_gold():
    """bez zlata se řádek nezobrazuje - tabulka je o vítězstvích"""
    by_year = {
        (1, 2019): [0, 3, 1],
        (2, 2021): [2, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [key for _, key, _, _ in table] == [(2, 2021)]


def test_perfect_championship_hides_single_gold_years():
    """
    Jedno zlato je skvělý výsledek, ale k dokonalému šampionátu daleko -
    a je jich tolik, že tabulku utopí. Na WMTBOC končilo přes sto jmen
    na jednom děleném místě úplně dole.
    """
    by_year = {
        (1, 2019): [1, 2, 0],
        (2, 2021): [1, 0, 0],
        (3, 2024): [2, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [key for _, key, _, _ in table] == [(3, 2024)]
    # ani hromada stříbra jedno zlato nevytáhne - rozhoduje zlato
    assert (1, 2019) not in [key for _, key, _, _ in table]


def test_perfect_championship_default_threshold_is_two():
    """
    Práh je vlastnost dashboardu, ne volba volajícího - drží se v konstantě,
    aby ho šablona mohla napsat do textu a nerozešel se s realitou.
    """
    assert tools.PERFECT_CHAMPIONSHIP_MIN_GOLD == 2

    by_year = {(1, 2019): [1, 0, 0]}

    assert tools.perfect_championship_table(by_year, PERFECT_COMPETITORS) == []
    # práh jde přebít, když by ho někdy chtěl někdo jiný
    assert len(tools.perfect_championship_table(by_year, PERFECT_COMPETITORS, min_gold=1)) == 1


def test_perfect_championship_min_gold_is_configurable():
    by_year = {
        (1, 2019): [1, 0, 0],
        (2, 2021): [3, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS, min_gold=3)

    assert [key for _, key, _, _ in table] == [(2, 2021)]


def test_perfect_championship_ties_are_stable():
    """
    Naprostá shoda se řadí podle roku a pak abecedně, ne podle pořadí
    v dictu - jinak by se tabulka mezi requesty přeskupovala.
    """
    by_year = {
        (3, 2024): [2, 0, 0],
        (1, 2019): [2, 0, 0],
        (2, 2019): [2, 0, 0],
    }

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [key for _, key, _, _ in table] == [(1, 2019), (2, 2019), (3, 2024)]
    # všichni mají stejnou bilanci, takže i stejné pořadí
    assert [rank for rank, _, _, _ in table] == [0, 0, 0]


def test_perfect_championship_works_without_competitors():
    """registr je jen pro abecední řazení, bez něj to musí projít taky"""
    by_year = {(1, 2019): [2, 0, 0], (2, 2021): [3, 0, 0]}

    table = tools.perfect_championship_table(by_year)

    assert [key for _, key, _, _ in table] == [(2, 2021), (1, 2019)]


def test_perfect_championship_empty_input():
    assert tools.perfect_championship_table({}) == []


def test_assign_shared_ranks_matches_medal_table_rule():
    """
    Dělená místa se počítají stejně jako v medailové tabulce - tenhle
    test hlídá, že se obě pravidla nerozejdou.
    """
    medals = {"a": [3, 0, 0], "b": [2, 0, 0], "c": [2, 0, 0], "d": [1, 0, 0]}

    ranking = tools.assign_shared_ranks(["a", "b", "c", "d"], medals.get)

    assert ranking == [(0, "a"), (1, "b"), (1, "c"), (3, "d")]


def test_perfect_championship_skips_the_world_cup():
    """
    Jeden ročník Poháru není jedna akce, ale seriál přes sezónu - a boduje
    do něj i WMTBOC a EMTBOC. Stejný důvod jako u Grand Slamu.
    """
    assert not tools.has_perfect_championship("WCUP")
    assert not tools.has_perfect_championship("u23wcup")
    assert not tools.has_perfect_championship("nonsense")
    assert "WCUP" not in tools.perfect_championship_codes()
    assert "U23WCUP" not in tools.perfect_championship_codes()


def test_perfect_championship_covers_championships():
    assert tools.has_perfect_championship("WMTBOC")
    assert tools.has_perfect_championship("emtboc")
    assert tools.has_perfect_championship("JWMTBOC")
    assert tools.has_perfect_championship("EYMTBOC")


def test_perfect_championship_menu_matches_grand_slam():
    """
    Stejná trojice jako u Grand Slamu - ostatní stránku mají, ale menu
    by se jimi zaplnilo.
    """
    assert tools.perfect_championship_menu_codes() == ["WMTBOC", "EMTBOC", "JWMTBOC"]


def test_perfect_championship_menu_only_links_to_pages_that_exist():
    """do menu nesmí přijít soutěž bez stránky - odkaz by vedl na 404"""
    for code in tools.perfect_championship_menu_codes():
        assert tools.has_perfect_championship(code), code

    assert set(tools.perfect_championship_menu_codes()) <= set(
        tools.perfect_championship_codes()
    )


def test_perfect_championship_never_covers_a_series():
    """
    Perfect Championship nesmí být u seriálu, do kterého bodují jiné
    soutěže - jeden "ročník" by pak nebyl jeden šampionát.
    """
    scoring = set(tools.wcup_scoring_events()) | set(tools.u23_scoring_events())

    for code in tools.perfect_championship_codes():
        meta = tools.EVENTS[code]
        assert not meta["needs_organizer"] or code not in scoring, code


def test_merge_medal_dicts_works_on_competitor_year_keys():
    """
    Sloupec "combined" sčítá individuální a štafetové medaile přes klíč
    (závodník, rok). merge_medal_dicts vzniklo nad samotným ID, takže
    tohle hlídá, že mu složený klíč nevadí - a že řádek, který je jen
    ve štafetách, nezmizí.
    """
    individual = {(1, 2019): [2, 0, 0], (2, 2021): [1, 1, 0]}
    relay = {(1, 2019): [1, 0, 0], (3, 2024): [0, 1, 0]}

    together = tools.merge_medal_dicts(individual, relay)

    assert together == {
        (1, 2019): [3, 0, 0],
        (2, 2021): [1, 1, 0],
        (3, 2024): [0, 1, 0],
    }


def test_max_relays_in_one_year():
    """
    Rozhoduje nejvyšší počet štafet v jednom ročníku, ne součet přes roky.
    Když se mix štafeta jela jindy než klasická, samostatný sloupec nemá
    co řadit.
    """
    # WMTBOC - jediná štafeta každý rok
    assert tools.max_relays_in_one_year({2019: ["sprint", "middle", "relay"]}) == 1

    # dvě štafety v jednom roce
    assert tools.max_relays_in_one_year({2019: ["sprint", "relay", "mix_relay"]}) == 2

    # dvě štafety, ale každá v jiném roce - pořád jen jedna naráz
    assert tools.max_relays_in_one_year({2018: ["relay"], 2019: ["mix_relay"]}) == 1


def test_max_relays_without_any_relay():
    assert tools.max_relays_in_one_year({2019: ["sprint", "middle"]}) == 0
    assert tools.max_relays_in_one_year({}) == 0


def test_max_relays_counts_sprint_relay():
    """sprint_relay je taky štafeta - jméno disciplíny ji nesmí vyřadit"""
    assert tools.max_relays_in_one_year({2019: ["relay", "sprint_relay"]}) == 2


def test_races_by_year_and_kind_splits_relay_out():
    """
    Emily Benham Kvale vyhrála 2019 všechny čtyři individuální závody.
    Pátý závod toho roku byla štafeta, takže v individuálním sloupci
    musí být "4 ze 4" - "4 z 5" by vypadalo jako ztráta.
    """
    counts = tools.races_by_year_and_kind(
        {2019: ["sprint", "middle", "long", "mass_start", "relay"]}
    )

    assert counts["individual"][2019] == 4
    assert counts["relay"][2019] == 1
    # v součtu pětka zůstává - je z ní vidět, že štafetová medaile chybí
    assert counts["combined"][2019] == 5


def test_races_by_year_and_kind_is_not_minus_one():
    """
    Nejde odečíst natvrdo jedničku. Ročník bez štafety žádnou nemá
    a EMTBOC jich může mít v programu víc.
    """
    counts = tools.races_by_year_and_kind(
        {
            2020: ["sprint", "middle"],
            2021: ["sprint", "relay", "mix_relay"],
        }
    )

    assert counts["individual"][2020] == 2
    assert counts["relay"][2020] == 0
    assert counts["individual"][2021] == 1
    assert counts["relay"][2021] == 2


def test_races_by_year_and_kind_counts_every_year():
    """každý ročník musí být ve všech třech sloupcích, ať se nekouká do prázdna"""
    counts = tools.races_by_year_and_kind({2019: ["sprint"], 2021: ["relay"]})

    for kind in ("individual", "relay", "combined"):
        assert set(counts[kind]) == {2019, 2021}, kind


def test_races_by_year_and_kind_empty():
    assert tools.races_by_year_and_kind({}) == {
        "individual": {},
        "relay": {},
        "combined": {},
    }


def test_perfect_championship_rows_carry_the_year_for_flags():
    """
    Šablona bere z řádku rok a podle něj hledá vlajku (nationality_in) i
    odkaz na ročník. Rok tedy musí zůstat použitelný jako rok - Emily
    Benham Kvale jela 2019 za GBR, dnes je vedená jako NOR.
    """
    emily = {
        "nationality": "NOR",
        "nat_history": [("GBR", 2000, 2021), ("NOR", 2022, None)],
    }
    by_year = {(1, 2019): [4, 0, 0], (1, 2024): [2, 0, 0]}

    table = tools.perfect_championship_table(by_year, {1: emily})
    flags = {year: tools.nationality_in(emily, year) for _, (_, year), _, _ in table}

    assert flags == {2019: "GBR", 2024: "NOR"}


def test_perfect_championship_survives_incomplete_competitor_record():
    """
    Jméno se používá jen jako tiebreak při naprosté shodě medailí.
    Záznam bez first/last kvůli tomu nesmí shodit celou stránku.
    """
    partial = {1: {"nationality": "NOR"}, 2: {"first": "B", "last": "B", "nationality": "CZE"}}
    by_year = {(1, 2019): [2, 0, 0], (2, 2019): [2, 0, 0]}

    table = tools.perfect_championship_table(by_year, partial)

    assert len(table) == 2


def test_perfect_championship_complete_year_wins_a_tie():
    """
    Hnilica má z EMTBOC 2026 čtyři zlata ze čtyř závodů, Laurila z 2013
    čtyři z pěti. Stejná bilance, ale Hnilica víc získat nemohl - jde
    tedy napřed a dostane vlastní místo, ne dělené.
    """
    by_year = {(1, 2026): [4, 0, 0], (2, 2013): [4, 0, 0]}
    races = {2026: 4, 2013: 5}

    table = tools.perfect_championship_table(
        by_year, PERFECT_COMPETITORS, races_by_year=races
    )

    assert [key for _, key, _, _ in table] == [(1, 2026), (2, 2013)]
    assert [rank for rank, _, _, _ in table] == [0, 1]
    assert [swept for _, _, _, swept in table] == [True, False]


def test_perfect_championship_completeness_never_beats_medals():
    """
    Kompletnost se řeší až po medailích. Dvě zlata ze dvou závodů jsou
    hezká, ale čtyři z pěti jsou pořád víc - jinak by tabulku vyhrávaly
    ročníky, kde se skoro nic nejelo.
    """
    by_year = {(1, 2019): [4, 0, 0], (2, 2021): [2, 0, 0]}
    races = {2019: 5, 2021: 2}

    table = tools.perfect_championship_table(
        by_year, PERFECT_COMPETITORS, races_by_year=races
    )

    assert [key for _, key, _, _ in table] == [(1, 2019), (2, 2021)]
    # ten menší ročník je kompletní, ale to ho nahoru nevytáhne
    assert [swept for _, _, _, swept in table] == [False, True]


def test_perfect_championship_sweep_flag_needs_race_counts():
    """bez počtu závodů se kompletnost neřeší a nic se nerozbije"""
    by_year = {(1, 2019): [4, 0, 0]}

    table = tools.perfect_championship_table(by_year, PERFECT_COMPETITORS)

    assert [swept for _, _, _, swept in table] == [False]


def test_perfect_championship_sweep_with_unknown_year():
    """rok, který v počtech závodů chybí, se nepovažuje za kompletní"""
    by_year = {(1, 1999): [4, 0, 0]}

    table = tools.perfect_championship_table(
        by_year, PERFECT_COMPETITORS, races_by_year={2019: 5}
    )

    assert [swept for _, _, _, swept in table] == [False]


def test_perfect_championship_equal_sweeps_still_share_rank():
    """
    Dva kompletní ročníky se stejnou bilancí jsou si pořád rovné -
    kompletnost dělené místo neruší, jen ho neuděluje přes ni.
    """
    by_year = {(1, 2019): [3, 0, 0], (2, 2021): [3, 0, 0]}
    races = {2019: 3, 2021: 3}

    table = tools.perfect_championship_table(
        by_year, PERFECT_COMPETITORS, races_by_year=races
    )

    assert [rank for rank, _, _, _ in table] == [0, 0]
    assert all(swept for _, _, _, swept in table)
