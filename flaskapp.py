# -*- coding: utf-8 -*-
"""
Flask app for the www.mtbo.info website.
"""

from collections import defaultdict
from functools import lru_cache

import flask
from flaskext.mysql import MySQL

from utils import tools

from models.competitors import Competitors
from models.races import Races
from models.results import Results
from models.wcup import Wcup

mysql = MySQL()
app = flask.Flask(__name__)
app.config.from_pyfile("flaskapp.cfg")

mysql.init_app(app)

RACES = Races(mysql).get_all()
COMPETITORS = Competitors(mysql).get_all_present()

# Počet ročníků každé události - get_count_by_event vrací COUNT(DISTINCT year),
# tedy kolikrát se šampionát konal, ne kolik bylo závodů.
EVENT_RACE_COUNTS = {
    code: Races(mysql).get_count_by_event(code)[0][0] for code in tools.event_codes()
}
MEDAL_NAMES = {1: "Gold", 2: "Silver", 3: "Bronze"}
YEAR = 2026

DISTANCE_NAMES = {
    "long": "Long",
    "mass-start": "Mass Start",
    "mass_start": "Mass Start",
    "middle": "Middle",
    "mix-relay": "Mix Relay",
    "relay": "Relay",
    "sprint": "Sprint",
    "sprint-relay": "Sprint Relay",
}

RELAY_FORMATS = {"M": "Men", "W": "Women", "X": "Mix"}

WCUP_COUNTED = {
    2010: 7,
    2011: 7,
    2012: 7,
    2013: 5,
    2014: 5,
    2015: 5,
    2016: 5,
    2017: 8,
    2018: 7,
    2019: 6,
    2020: 0,
    2021: 4,
    2022: 6,
    2023: 7,
    2024: 7,
    2025: 7,
    2026: 7,
}


@app.context_processor
def inject_events():
    """
    Registr událostí do všech šablon - navigace i stránka závodníka z něj
    staví seznamy, takže přidání další kategorie nevyžaduje zásah v HTML.
    """
    return {
        "EVENTS": tools.EVENTS,
        "ELITE": tools.ELITE,
        "JUNIOR_CODES": tools.non_elite_codes(),
        "CAREER_PATHS": tools.CAREER_PATHS,
    }


@lru_cache()
@app.route("/")
def home():
    """
    Main page
    """
    # Seznamy závodů mají vlastní stránky (/races/<event>/) - na rozcestí
    # jich bylo přes tři sta a stránka kvůli tomu vážila 200 kB.
    recent = Races(mysql).get_by_year(YEAR)

    res = Results(mysql)
    first_ms = res.first_medal_year(YEAR)
    first_me = res.first_medal_year(YEAR, event="EMTBOC")
    first = first_ms + first_me
    for comp in first:
        tmp = COMPETITORS[comp["competitor_id"]]
        comp["name"] = f"{tmp['first']} {tmp['last']}"
        comp["team"] = tmp["nationality"]

    return flask.render_template(
        "index.html",
        recent=recent,
        flags=tools.IOC_INDEX,
        first=first,
        year=YEAR,
    )


@app.route("/about/")
def about():
    """
    about the site
    """
    return flask.render_template("about.html")


@lru_cache()
@app.route("/all_time_participation/<event>/")
def count(event="WMTBOC"):
    """
    endpoint to show all time participation on a given event
    params:
        event: WMTBOC, EMTBOC or WCUP
    """
    wmtboc = Races(mysql).get_by_event(event.upper(), True)
    per_year = defaultdict(list)
    for mrace in wmtboc:
        per_year[mrace[1]].append(mrace[0])

    title = event.upper()

    wmtboc_table = {year: Results(mysql).get_by_events_id(id_list) for year, id_list in per_year.items()}

    wmtboc_table = {year: (len(flags), flags) for year, flags in wmtboc_table.items()}

    return flask.render_template("count.html", wmtboc=wmtboc_table, flags=tools.IOC_INDEX, title=title)


@app.route("/teams/")
def teams():
    """
    National teams results per year
    """
    title = "National teams results per year"
    nations = {com["nationality"] for com in COMPETITORS.values()}

    nations = sorted(list(nations))

    return flask.render_template(
        "teams.html",
        title=title,
        nations=nations,
        years=tools.years(),
        flags=tools.IOC_INDEX,
    )


@app.route("/nation/<code>/<year>/")
def nation(code, year):
    """
    reults for a given nation in a given year
    params:
        code: country code
        year: year
    """
    code = code.upper()
    sel_competitors = {cid: comp for cid, comp in COMPETITORS.items() if comp["nationality"] == code}
    id_comp = {val["competitor_id"] for val in sel_competitors.values()}

    races_year = Races(mysql).get_by_year(year)
    model = Results(mysql)
    all_results = [model.get_race_results(myrace[0]) for myrace in races_year]
    filtered_results = [[row for row in result if row[0] in id_comp] for result in all_results]
    filtered_results = [result for result in filtered_results if result]

    if filtered_results:
        title = f"Team {code} results for {year}"
        return flask.render_template(
            "races_team.html",
            title=title,
            results=filtered_results,
            competitors=sel_competitors,
            race_info=RACES,
            years=tools.years(),
            team=code,
        )
    else:
        title = f"No results for team {code} in {year}"
        return flask.render_template("races_team_nores.html", title=title)


@app.route("/api/prefetch/competitor/")
def api_search():
    """
    internal enpoint for autocomplete
    """
    data = [{"name": f'{val["first"]} {val["last"]}', "id": key} for key, val in COMPETITORS.items()]
    return flask.jsonify(result=data)


@app.route("/worldcup_overall/")
def wcup_overall():
    """
    World cup overall standings
    """
    model = Wcup(mysql)
    men = model.get_overall_summary(category="M")
    women = model.get_overall_summary(category="F")

    return flask.render_template(
        "wcup_overall.html",
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
        men=men,
        women=women,
    )


@lru_cache()
@app.route("/worldcup/", defaults={"year": YEAR})
@app.route("/worldcup/<int:year>/")
def wcup(year):
    """
    world cup results for a given year
    params:
        year: year
    """
    model = Results(mysql)
    races_model = Races(mysql)
    title = f"World Cup {year} individual overall standings"

    scoring = tools.wcup_scoring_events()
    season_race = races_model.get_individual_ids_by_year(year, events=scoring)
    totals_f = model.get_worldcup_points(year, gender="F", events=scoring)
    totals_m = model.get_worldcup_points(year, gender="M", events=scoring)

    try:
        counted = WCUP_COUNTED[year]
    except KeyError:
        flask.abort(404)

    nr_races = len(season_race)
    if nr_races == 0:
        counted_text = f"No results in {year} so far."
    elif counted >= nr_races:
        counted_text = f"All {nr_races} results counted in overall standings (season in progress)."
    else:
        counted_text = f"Best {counted} of {nr_races} results counted in overall standings."

    totals_f = tools.make_worldup_results(season_race, totals_f, counted)
    totals_m = tools.make_worldup_results(season_race, totals_m, counted)

    country = {COMPETITORS[row["comp_id"]]["nationality"] for row in totals_m + totals_f}

    years = sorted(WCUP_COUNTED.keys(), reverse=True)

    return flask.render_template(
        "wcup.html",
        title=title,
        counted_text=counted_text,
        table_colspan=len(season_race),
        women=totals_f,
        men=totals_m,
        year=year,
        years=years,
        stats={"men": len(totals_m), "women": len(totals_f), "country": len(country)},
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/teamworldcup/", defaults={"year": YEAR})
@app.route("/teamworldcup/<int:year>/")
def team_wcup(year):
    """
    team results for world cup
    params:
        year: year to show
    """
    model = Results(mysql)
    title = f"Team World Cup {year} overall standings"

    scoring = tools.wcup_scoring_events()
    totals_m = model.get_teamworldcup_points(year, "M", events=scoring)
    totals_f = model.get_teamworldcup_points(year, "W", events=scoring)
    totals_x = model.get_teamworldcup_points(year, "X", events=scoring)
    counted_text = "All team races are counted in overall standings each year."

    totals_m, races_m = tools.make_team_worldup_results_base(totals_m, "M")
    totals_f, races_f = tools.make_team_worldup_results_base(totals_f, "W")
    totals_x, races_x = tools.make_team_worldup_results_base(totals_x, "X")
    season_race = races_m | races_f | races_x

    totals = tools.make_team_worldup_results(season_race, totals_m, totals_f, totals_x)
    race_links = [race.split("-") for race in season_race]
    race_links = [(int(i), RELAY_FORMATS[cat]) for i, cat in race_links]
    race_links.sort(key=lambda x: x[0])

    country = set((team["team"] for team in totals))
    years = sorted(WCUP_COUNTED.keys(), reverse=True)

    return flask.render_template(
        "wcup_team.html",
        title=title,
        counted_text=counted_text,
        totals=totals,
        race_links=race_links,
        table_colspan=len(season_race),
        races=RACES,
        year=year,
        years=years,
        stats={"country": len(country)},
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/race/<int:race_id>/")
def race(race_id):
    """
    display info about given race
    params:
        race_id: race id
    """
    model = Results(mysql)
    try:
        cur_race = RACES[int(race_id)]
    except KeyError:
        flask.abort(404)

    data = model.get_race_results(race_id)
    title = f'{cur_race["event"]} {cur_race["year"]} {DISTANCE_NAMES[cur_race["distance"]]}'
    race_results_link = tools.results_link(cur_race)

    if cur_race["distance"] == "relay":
        women_list = model.get_relay_results(race_id, "W")
        men_list = model.get_relay_results(race_id, "M")

        women, women_others = tools.prepare_relay_output(women_list)
        men, men_others = tools.prepare_relay_output(men_list)
        country = set(men.keys()).union(set(women.keys()))

        return flask.render_template(
            "relay.html",
            title=title,
            women=women,
            men=men,
            women_others=women_others,
            men_others=men_others,
            stats={
                "men": len(men.keys()),
                "women": len(women.keys()),
                "country": len(country),
                "suffix": "'s teams",
            },
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=cur_race,
            results_link=race_results_link,
        )

    elif cur_race["distance"] in ("sprint-relay", "mix-relay"):
        result_list = model.get_relay_results(race_id, "X")
        results, results_others = tools.prepare_relay_output(result_list)

        return flask.render_template(
            "mix_relay.html",
            title=title,
            results=results,
            results_others=results_others,
            stats={"teams": len(results.keys())},
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=cur_race,
            results_link=race_results_link,
        )
    else:
        women = [row for row in data if COMPETITORS[row[0]]["gender"] == "F"]
        men = [row for row in data if COMPETITORS[row[0]]["gender"] == "M"]
        country = {COMPETITORS[row[0]]["nationality"] for row in data}

        return flask.render_template(
            "race.html",
            title=title,
            women=women,
            men=men,
            stats={
                "men": len(men),
                "women": len(women),
                "country": len(country),
                "suffix": "",
            },
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=cur_race,
            results_link=race_results_link,
        )


@lru_cache()
@app.route("/competitor/<competitor_id>/")
def competitor(competitor_id):
    """
    display info about given competitor
    params:
        competitor_id: competitor id
    """
    model = Results(mysql)
    try:
        current = COMPETITORS[int(competitor_id)]
    except KeyError:
        flask.abort(404)

    data = model.get_competitor_results(competitor_id)
    # place je None u štafet bez oficiálního umístění - řadí se na konec
    data.sort(key=lambda row: (row[2] is None, row[2]))

    data = [tools.format_competitor_row(row, RACES) for row in data]

    distances = list({row["dist"] for row in data})

    # Každá věková kategorie má vlastní tabulku - jsou to jiné závody
    # a sčítat je dohromady by bylo zavádějící. Youth se nesmí slít
    # s juniory: jsou jezdci, kteří jeli youth a do juniorů nedorostli
    # (nebo zatím nedorostli), ve sloučené tabulce by zmizeli.
    elite_codes = tools.event_codes(tools.ELITE)
    junior_codes = tools.event_codes(tools.JUNIOR)
    youth_codes = tools.event_codes(tools.YOUTH)

    medal_table = tools.prepare_medal_table(model, competitor_id, events=elite_codes)
    relay_medal_table = tools.prepare_medal_table(model, competitor_id, "relay", events=elite_codes)
    junior_medal_table = tools.prepare_medal_table(model, competitor_id, events=junior_codes)
    junior_relay_medal_table = tools.prepare_medal_table(
        model, competitor_id, "relay", events=junior_codes
    )
    youth_medal_table = tools.prepare_medal_table(model, competitor_id, events=youth_codes)
    youth_relay_medal_table = tools.prepare_medal_table(
        model, competitor_id, "relay", events=youth_codes
    )

    # Get raw data from database
    individual, relay = model.get_career_best_with_teams(competitor_id)

    # Process into career best structure
    career_best = tools.process_career_best_from_db(individual, relay)

    races_model = Races(mysql)

    # Statistiky, účast a první medaile pro každou událost v registru
    event_stats = {}
    participation = {}
    first_medals = {}
    for code in tools.event_codes():
        stats = tools.analyze_event_completeness(career_best, code)
        stats.update(
            tools.calculate_grand_slam_score(
                career_best, races_model.get_distances_by_year(code), code
            )
        )
        event_stats[code] = stats

        years = model.get_event_competitor_participation(competitor_id, code)
        participation[code] = {
            "total": EVENT_RACE_COUNTS[code],
            "mine": len(years),
            "years": ", ".join(years),
        }

        first_medals[code] = {
            "medal": model.get_first_medal(competitor_id, code),
            "title": model.get_first_medal(competitor_id, code, 1),
            "relay_medal": model.get_first_medal(competitor_id, code, table="relay"),
            "relay_title": model.get_first_medal(competitor_id, code, 1, table="relay"),
        }

    # Karty se ukazují, jen když tam něco je - většina závodníků
    # v juniorech ani v youth nestartovala.
    def competed_in(codes, *tables):
        return any(
            any(table[code]) for table in tables for code in codes
        ) or any(event_stats[code]["total_distances_competed"] for code in codes)

    has_junior = competed_in(junior_codes, junior_medal_table, junior_relay_medal_table)
    has_youth = competed_in(youth_codes, youth_medal_table, youth_relay_medal_table)

    title = " ".join([current["first"], current["last"]])

    try:
        birth = current["born"].split("-")[0]
    except AttributeError:
        birth = None

    # Soutěže, do kterých se závodník věkem vůbec nemohl dostat, se na
    # kartě neukazují - "nikdy se nezúčastnil" u JWMTBOC v roce 2008
    # u někoho narozeného 1975 nic neříká, soutěž vznikla dávno potom,
    # co z juniorů vyrostl.
    eligible = {code: tools.could_have_competed(meta, birth) for code, meta in tools.EVENTS.items()}

    return flask.render_template(
        "competitor.html",
        title=title,
        birth=birth,
        medal_table=medal_table,
        relay_medal_table=relay_medal_table,
        junior_medal_table=junior_medal_table,
        junior_relay_medal_table=junior_relay_medal_table,
        has_junior=has_junior,
        youth_medal_table=youth_medal_table,
        youth_relay_medal_table=youth_relay_medal_table,
        has_youth=has_youth,
        elite_codes=elite_codes,
        junior_codes=junior_codes,
        youth_codes=youth_codes,
        participation=participation,
        first_medals=first_medals,
        medal_names=MEDAL_NAMES,
        races=RACES,
        competitor=current,
        data=data,
        distances=distances,
        flags=tools.IOC_INDEX,
        event_stats=event_stats,
        eligible=eligible,
    )


@lru_cache(maxsize=256)
@app.route("/medals_table/<event>/")
@app.route("/medals_table/<event>/<country>/")
def medals_table(event="WMTBOC", country=None):
    """
    display medal table for given event type, optionally for one country only
    params:
        event: event type
        country: IOC country code, None shows the whole field
    """
    meta = tools.get_event(event)
    if meta is None:
        flask.abort(404)

    model = Results(mysql)
    medal_lines = [model.get_place_count(place, event.upper()) for place in range(1, 4)]
    relay_lines = [model.get_place_count(place, event.upper(), "relay") for place in range(1, 4)]

    converted = tools.merge_medal_lines(*medal_lines)
    converted_relay = tools.merge_medal_lines(*relay_lines)
    together = tools.merge_medal_dicts(converted, converted_relay)

    # Žebříčky se počítají nad celým polem i při filtru - jen tak sedí
    # globální pořadí včetně dělených míst.
    ranking = tools.sort_medal_table(converted)
    ranking_relay = tools.sort_medal_table(converted_relay)
    ranking_together = tools.sort_medal_table(together)

    countries = {COMPETITORS[com_id]["nationality"] for com_id in converted.keys()}
    rel_countries = {COMPETITORS[com_id]["nationality"] for com_id in converted_relay.keys()}

    # Pruh vlajek nad tabulkou - jen země, které mají aspoň jednu medaili,
    # s celkovým počtem, takže slouží i jako rychlé srovnání národů.
    all_countries = tools.medal_countries(together, COMPETITORS)
    country_totals = tools.aggregate_medals_by_country(together, COMPETITORS)

    if country is not None:
        country = country.upper()
        if country not in all_countries:
            flask.abort(404)

    converted, ranking = tools.filter_medal_table(converted, ranking, COMPETITORS, country)
    converted_relay, ranking_relay = tools.filter_medal_table(
        converted_relay, ranking_relay, COMPETITORS, country
    )
    together, ranking_together = tools.filter_medal_table(
        together, ranking_together, COMPETITORS, country
    )

    disclaimer = ""
    if event == "wcup":
        disclaimer = "WMTBOC and EMTBOC are World Cup races too. This table contains only \
            the medals from World Cup races other than the championships."

    stats = {
        "individual": len(converted),
        "indiv_countries": len(countries),
        "relay": len(converted_relay),
        "rel_countries": len(rel_countries),
    }

    table_content = {
        "all": (together, ranking_together),
        "individual": (converted, ranking),
        "relay": (converted_relay, ranking_relay),
    }

    title = f"Medals from {meta['name']}"
    if country:
        title = f"{title} - {country}"

    return flask.render_template(
        "medals.html",
        title=title,
        stats=stats,
        disclaimer=disclaimer,
        table_content=table_content,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
        event_slug=meta["slug"],
        country=country,
        all_countries=all_countries,
        country_totals=country_totals,
    )


@lru_cache()
@app.route("/team_medals_table/<event>/")
def team_medals_table(event="WMTBOC"):
    """
    display medal table for given event type grouped by country
    params:
        event: event type
    """
    meta = tools.get_event(event)
    if meta is None:
        flask.abort(404)

    model = Results(mysql)
    medal_lines = [model.get_place_count(place, event.upper()) for place in range(1, 4)]
    relay_lines = [model.get_relay_country_place_count(place, event.upper()) for place in range(1, 4)]

    converted = tools.merge_medal_lines(*medal_lines)
    converted_relay_by_country = tools.merge_medal_lines(*relay_lines)

    countries = {COMPETITORS[com_id]["nationality"] for com_id in converted.keys()}
    rel_countries = {com_id for com_id in converted_relay_by_country.keys()}

    # converted grouped by country
    converted_by_country = tools.aggregate_medals_by_country(converted, COMPETITORS)

    ranking_by_country = tools.sort_medal_table(converted_by_country)
    ranking_relay_by_country = tools.sort_medal_table(converted_relay_by_country)

    together_by_country = tools.merge_medal_dicts(converted_by_country, converted_relay_by_country)
    ranking_together_by_country = tools.sort_medal_table(together_by_country)

    disclaimer = ""
    if event == "wcup":
        disclaimer = "WMTBOC and EMTBOC are World Cup races too. This table contains only \
            the medals from World Cup races other than the championships."

    stats = {
        "individual": len(converted_by_country),
        "indiv_countries": len(countries),
        "relay": len(converted_relay_by_country),
        "rel_countries": len(rel_countries),
    }

    table_content = {
        "all": (together_by_country, ranking_together_by_country),
        "individual": (converted_by_country, ranking_by_country),
        "relay": (converted_relay_by_country, ranking_relay_by_country),
    }

    title = f"Medals from {meta['name']}"

    return flask.render_template(
        "team_medals.html",
        title=title,
        stats=stats,
        disclaimer=disclaimer,
        table_content=table_content,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/participation/<event>/")
def participation_in_event(event="WMTBOC"):
    """
    display participation table for given event type
    params:
        event: event type
    """
    meta = tools.get_event(event)
    if meta is None:
        flask.abort(404)

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id in at_last_one_participation:
        res = model.get_event_competitor_participation(competitor_id, event.upper())
        if res:
            result[competitor_id] = res

    result = sorted(result.items(), key=lambda kv: len(kv[1]), reverse=True)

    return flask.render_template(
        "participations.html",
        title=meta["name"],
        total=EVENT_RACE_COUNTS[event.upper()],
        table_data=result,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/young_stars/<event>/")
@app.route("/young_stars/<event>/<int:place>/")
def young_stars(event="WMTBOC", place=None):
    """
    display youngest medalists for given event type
    params:
        event: event type
        place: medal place
    """
    # Jen elita - u juniorů je věkové rozpětí dané kategorií, takže
    # "nejmladší mistr" nic neříká.
    meta = tools.get_event(event)
    if meta is None or meta["kind"] != tools.ELITE:
        flask.abort(404)

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)
    result = {}

    for competitor_id in at_last_one_participation:
        if place:
            place = place if place <= 3 else 3
            res = model.get_first_medal(competitor_id, event.upper(), place)
        else:
            res = model.get_first_medal(competitor_id, event.upper(), 1)

        if res:
            try:
                born = int(COMPETITORS[competitor_id]["born"].split("-")[0])
            except ValueError:
                born = 0
            except AttributeError:
                born = 0

            if born:
                age = res[0][1] - born
                result[competitor_id] = [age, res]

    result = sorted(result.items(), key=lambda kv: kv[1][0])
    result = [res for res in result if res[1][0] <= 23]

    title = f"Young stars on {meta['name']}"
    if place:
        disclaimer = f"Competitors who got a \
            {meta['name']} medal in age 24 or younger."
    else:
        disclaimer = f"Competitors who got their first \
            {meta['name']} medal before becoming 24."

    return flask.render_template(
        "youngstars.html",
        title=title,
        disclaimer=disclaimer,
        table_data=result,
        place=place,
        medal_names=MEDAL_NAMES,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/great_masters/<event>/")
@app.route("/great_masters/<event>/<int:place>/")
def great_masters(event="WMTBOC", place=None):
    """
    display oldest medalists for given event type
    params:
        event: event type
        place: medal type place
    """
    # Taky jen elita, ze stejného důvodu jako young_stars.
    meta = tools.get_event(event)
    if meta is None or meta["kind"] != tools.ELITE:
        flask.abort(404)

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id in at_last_one_participation:
        if place:
            place = place if place <= 3 else 3
            res = model.get_last_medal(competitor_id, event.upper(), place)
        else:
            res = model.get_last_medal(competitor_id, event.upper(), 1)

        if res:
            try:
                born = int(COMPETITORS[competitor_id]["born"].split("-")[0])
            except ValueError:
                born = 0
            except AttributeError:
                born = 0

            if born:
                age = res[0][1] - born
                result[competitor_id] = [age, res]

    result = sorted(result.items(), key=lambda kv: kv[1][0], reverse=True)
    result = [res for res in result if res[1][0] >= 35]

    title = f"Great masters on {meta['name']}"
    if place:
        disclaimer = f"Competitors who got a \
            {meta['name']} medal in age 35 and older."
    else:
        disclaimer = f"Competitors who got the \
            {meta['name']} title in age 35 and older."

    return flask.render_template(
        "youngstars.html",
        title=title,
        disclaimer=disclaimer,
        table_data=result,
        place=place,
        medal_names=MEDAL_NAMES,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/progression/<path>/")
@app.route("/progression/<path>/<int:place>/")
def progression(path="world", place=None):
    """
    Závodníci, kteří získali medaili jako junioři i mezi elitou.

    Bez place jsou to medailisté, s place=1 mistři - stejná konvence
    jako /young_stars/<event>/3/. Větev (world/europe/full) drží
    světové a evropské tituly oddělené, míchat se nesmí.
    """
    meta = tools.career_path(path)
    if meta is None:
        flask.abort(404)

    groups = meta["groups"]
    # bez parametru medailisté, jinak zadané místo omezené na 1-3
    place = 3 if place is None else max(1, min(place, 3))

    model = Results(mysql)
    medals = model.get_individual_medals(place=place, events=tools.path_events(groups))
    table_data = tools.build_progression(medals, COMPETITORS, groups, place=place)

    stages = [stage for stage, _ in groups]
    noun = "champions" if place == 1 else "medalists"
    title = f"{' to '.join(stages)} {noun} - {meta['name']} championships"

    return flask.render_template(
        "progression.html",
        title=title,
        table_data=table_data,
        stages=stages,
        place=place,
        path=path,
        meta=meta,
        competitors=COMPETITORS,
        distance_names=DISTANCE_NAMES,
        flags=tools.IOC_INDEX,
    )


@app.route("/events/")
@app.route("/events/<event>/")
@app.route("/events/<event>/<int:year>/")
@app.route("/events/<event>/<int:year>/<organizer>/")
def event_summary(event: str = "WMTBOC", year: int = YEAR, organizer: str = ""):
    """
    display summary of given event type for given year
    params:
        year: year
        event: event type
    """
    meta = tools.get_event(event)
    if meta is None:
        flask.abort(404)

    model = Results(mysql)

    # Check if the event has results for the requested year
    available_years = model.get_event_years(event.upper())

    # If no results for requested year, show message with available years
    if year not in available_years:
        if available_years:
            latest_year = max(available_years)
            return flask.render_template(
                "no_results.html",
                event=event.upper(),
                requested_year=year,
                available_years=sorted(available_years, reverse=True),
                latest_year=latest_year,
                event_name=tools.EVENT_NAMES.get(event.upper(), event.upper()),
            )
        else:
            flask.abort(404)

    # Světový pohár se jede na víc místech do roka, takže potřebuje i
    # pořadatele; u šampionátů je ročník jednoznačný.
    if meta["needs_organizer"] and not organizer:
        flask.abort(404)

    code = event.upper()
    host = organizer.upper() if meta["needs_organizer"] else ""

    data_men, mrace_ids = model.get_summary_medals(year, code, "M", host)
    data_women, wrace_ids = model.get_summary_medals(year, code, "F", host)
    data_relays = model.get_summary_relay_medals(year, code, host)
    countries = model.get_participating_countries(year, code, host)
    nr_men = model.count_event_competitors(year, code, "M", host)
    nr_women = model.count_event_competitors(year, code, "F", host)
    races_info = model.get_summary_venues(year, code, host)

    title = f"{meta['name']} {host + ' ' if host else ''}{year} summary"

    # Bez závodů by min()/max() nad daty spadlo.
    if not races_info:
        flask.abort(404)

    team_results = []
    for relay in data_relays:
        race_id, race_distance = relay
        print(race_id, race_distance)
        team_men = []
        team_women = []
        team_mix = []
        if race_distance == "relay":
            women_list = model.get_relay_results(race_id, "W")
            men_list = model.get_relay_results(race_id, "M")
            women_list = women_list[:9]
            men_list = men_list[:9]

            team_women, _ = tools.prepare_relay_output(women_list)
            team_men, _ = tools.prepare_relay_output(men_list)

        if race_distance == "sprint-relay":
            result_list = model.get_relay_results(race_id, "X")
            result_list = result_list[:6]
            team_mix, _ = tools.prepare_relay_output(result_list)

        if race_distance == "mix-relay":
            result_list = model.get_relay_results(race_id, "X")
            result_list = result_list[:9]
            team_mix, _ = tools.prepare_relay_output(result_list)

        team_results.append({"men": team_men, "women": team_women, "mix": team_mix})

    race_ids = mrace_ids | wrace_ids
    venues = [item[1] for item in races_info]
    dates = [item[0] for item in races_info]
    return flask.render_template(
        "summary.html",
        from_date=min(dates),
        to_date=max(dates),
        title=title,
        teams=countries,
        venues=venues,
        race_ids=race_ids,
        nr_teams=len(countries),
        nr_men=nr_men,
        nr_women=nr_women,
        data_men=data_men,
        team_results=team_results,
        data_women=data_women,
        medal_names=MEDAL_NAMES,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
        years=model.get_event_years(event.upper()),
        event=event.upper(),
        current_year=year,
    )


@lru_cache()
@app.route("/races/<event>/")
def races_history(event):
    """
    display all races of given event type with their champions
    params:
        event: event type
    """
    meta = tools.get_event(event)
    if meta is None:
        flask.abort(404)

    code = event.upper()
    races_model = Races(mysql)
    model = Results(mysql)

    history = tools.build_race_history(
        races_model.get_by_event(code),
        model.get_event_race_winners(code),
        model.get_event_relay_winners(code),
        COMPETITORS,
    )

    return flask.render_template(
        "races_history.html",
        title=f"{meta['name']} - all races",
        history=history,
        event=code,
        meta=meta,
        years=sorted({race["year"] for race in history}, reverse=True),
        distance_names=DISTANCE_NAMES,
        relay_formats=RELAY_FORMATS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/grand_slam/<event>/")
def grand_slam(event="WMTBOC"):
    """
    Grand slam results with year-aware scoring.

    A Grand Slam winner is someone who won all distances that existed
    during any year they competed (career-based), with a minimum of 3 wins.
    """
    event_upper = event.upper()
    result_model = Results(mysql)
    races_model = Races(mysql)

    # Get historical distances by year for the event
    distances_by_year = races_model.get_distances_by_year(event_upper)

    interesting_competitors = result_model.get_competitors_with_at_last_one_medal(event_upper, place=1)
    carrers_data = {}

    for comp in interesting_competitors:
        individual, relay = result_model.get_career_best_with_teams(comp)
        career_best = tools.process_career_best_from_db(individual, relay)

        # Get basic event completeness stats
        basic_stats = tools.analyze_event_completeness(career_best, event_upper)

        # Calculate year-aware Grand Slam score
        grand_slam_stats = tools.calculate_grand_slam_score(career_best, distances_by_year, event_upper)

        # Count total medals (G-S-B) from raw results
        medals_stats = tools.count_medals_by_event(individual, relay, event_upper)

        # Merge all stats
        carrers_data[comp] = {
            **basic_stats,
            **grand_slam_stats,
            **medals_stats,
        }

    # Sort by: Grand Slam winners first, then completion %, then wins, then score
    carrers_data = dict(
        sorted(
            carrers_data.items(),
            key=lambda item: (
                not item[1]["is_grand_slam_winner"],  # Grand Slam winners first
                -item[1]["completion_percentage"],  # Higher completion % first
                -item[1]["total_wins"],  # More wins first
                item[1]["distances_score"],  # Lower score first (tiebreaker)
            ),
        )
    )

    return flask.render_template(
        "grand_slam.html",
        event=event_upper,
        carrers_data=carrers_data,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
        medal_names=MEDAL_NAMES,
    )


@app.errorhandler(404)
def page_not_found(error):
    """
    404 error handler
    """
    print("404", error)
    return flask.render_template("error_404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
