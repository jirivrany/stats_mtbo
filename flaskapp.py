# -*- coding: utf-8 -*-
"""
Flask app for the www.mtbo.info website.
"""
import sys
import operator
from collections import defaultdict
from functools import lru_cache
from datetime import datetime

import flask
from flaskext.mysql import MySQL

from utils import tools

from models.competitors import Competitors
from models.races import Races
from models.results import Results
from models.wcup import Wcup
from loguru import logger


mysql = MySQL()
app = flask.Flask(__name__)
app.config.from_pyfile("flaskapp.cfg")

mysql.init_app(app)

RACES = Races(mysql).get_all()
COMPETITORS = Competitors(mysql).get_all_present()
WMTBOC_NR = Races(mysql).get_count_by_event("WMTBOC")[0][0]
EMTBOC_NR = Races(mysql).get_count_by_event("EMTBOC")[0][0]
MEDAL_NAMES = {1: "Gold", 2: "Silver", 3: "Bronze"}
YEAR = 2025

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
}


@lru_cache()
@app.route("/")
def home():
    """
    Main page
    """
    wmtboc = Races(mysql).get_by_event("WMTBOC")
    emtboc = Races(mysql).get_by_event("EMTBOC")
    wmtboc_years = Races(mysql).get_event_years("WMTBOC")
    emtboc_years = Races(mysql).get_event_years("EMTBOC")
    wcup_years = Races(mysql).get_event_years("WCUP")

    wmtboc = sorted(wmtboc, key=lambda x: x[1], reverse=True)
    emtboc = sorted(emtboc, key=lambda x: x[1], reverse=True)

    wcup_races = Races(mysql).get_by_event("WCUP")
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
        wmtboc=wmtboc,
        emtboc=emtboc,
        wmtboc_years=wmtboc_years,
        emtboc_years=emtboc_years,
        wcup_years=wcup_years,
        wcup=wcup_races,
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

    current_year = datetime.now().year + 1
    season_race = races_model.get_individual_ids_by_year(year)
    totals_f = model.get_worldcup_points(year, gender="F")
    totals_m = model.get_worldcup_points(year, gender="M")
    try:
        counted = WCUP_COUNTED[year]
    except KeyError:
        flask.abort(404)

    if len(season_race) > 0:
        counted_text = f"Best {counted} of {len(season_race)} results counted in overall standings."
    else:
        counted_text = f"No results in {year} so far."

    totals_f = tools.make_worldup_results(season_race, totals_f, counted)
    totals_m = tools.make_worldup_results(season_race, totals_m, counted)

    country = {COMPETITORS[row["comp_id"]]["nationality"] for row in totals_m + totals_f}

    return flask.render_template(
        "wcup.html",
        title=title,
        counted_text=counted_text,
        table_colspan=len(season_race),
        women=totals_f,
        men=totals_m,
        year=year,
        stats={"men": len(totals_m), "women": len(totals_f), "country": len(country)},
        competitors=COMPETITORS,
        current_year=current_year,
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

    current_year = datetime.now().year + 1
    totals_m = model.get_teamworldcup_points(year, "M")
    totals_f = model.get_teamworldcup_points(year, "W")
    totals_x = model.get_teamworldcup_points(year, "X")
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

    return flask.render_template(
        "wcup_team.html",
        title=title,
        counted_text=counted_text,
        totals=totals,
        race_links=race_links,
        table_colspan=len(season_race),
        races=RACES,
        year=year,
        stats={"country": len(country)},
        competitors=COMPETITORS,
        current_year=current_year,
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

    if cur_race["distance"] == "relay":
        women_list = model.get_relay_results(race_id, "W")
        men_list = model.get_relay_results(race_id, "M")

        women = tools.prepare_relay_output(women_list)
        men = tools.prepare_relay_output(men_list)
        country = set(men.keys()).union(set(women.keys()))

        return flask.render_template(
            "relay.html",
            title=title,
            women=women,
            men=men,
            stats={
                "men": len(men.keys()),
                "women": len(women.keys()),
                "country": len(country),
                "suffix": "'s teams",
            },
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=cur_race,
        )

    elif cur_race["distance"] in ("sprint-relay", "mix-relay"):
        result_list = model.get_relay_results(race_id, "X")
        results = tools.prepare_relay_output(result_list)

        return flask.render_template(
            "mix_relay.html",
            title=title,
            results=results,
            stats={"teams": len(results.keys())},
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=cur_race,
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
    data.sort(key=operator.itemgetter(2))

    data = [tools.format_competitor_row(row, RACES) for row in data]

    distances = list({row["dist"] for row in data})

    medal_table = tools.prepare_medal_table(model, competitor_id)
    relay_medal_table = tools.prepare_medal_table(model, competitor_id, "relay")

    my_wmtboc = model.get_event_competitor_participation(competitor_id, "WMTBOC")
    my_emtboc = model.get_event_competitor_participation(competitor_id, "EMTBOC")

    # Get raw data from database
    individual, relay = model.get_career_best_with_teams(competitor_id)

    # Process into career best structure
    career_best = tools.process_career_best_from_db(individual, relay)

    # Analyze completeness for each event
    wmtboc_stats = tools.analyze_event_completeness(career_best, "WMTBOC")
    emtboc_stats = tools.analyze_event_completeness(career_best, "EMTBOC")
    wcup_stats = tools.analyze_event_completeness(career_best, "WCUP")

    # Calculate Grand Slam scores for each event
    races_model = Races(mysql)
    wmtboc_distances_by_year = races_model.get_distances_by_year("WMTBOC")
    emtboc_distances_by_year = races_model.get_distances_by_year("EMTBOC")
    wcup_distances_by_year = races_model.get_distances_by_year("WCUP")

    wmtboc_grand_slam = tools.calculate_grand_slam_score(career_best, wmtboc_distances_by_year, "WMTBOC")
    emtboc_grand_slam = tools.calculate_grand_slam_score(career_best, emtboc_distances_by_year, "EMTBOC")
    wcup_grand_slam = tools.calculate_grand_slam_score(career_best, wcup_distances_by_year, "WCUP")

    # Merge Grand Slam data into stats
    wmtboc_stats.update(wmtboc_grand_slam)
    emtboc_stats.update(emtboc_grand_slam)
    wcup_stats.update(wcup_grand_slam)

    logger.info(f"Competitor {competitor_id} - WMTBOC stats: {wmtboc_stats}")
    logger.info(f"Competitor {competitor_id} - EMTBOC stats: {emtboc_stats}")
    logger.info(f"Competitor {competitor_id} - WCUP stats: {wcup_stats}")

    first_medals = {
        "medal_wmtboc": model.get_first_medal(competitor_id, "WMTBOC"),
        "medal_emtboc": model.get_first_medal(competitor_id, "EMTBOC"),
        "title_wmtboc": model.get_first_medal(competitor_id, "WMTBOC", 1),
        "title_emtboc": model.get_first_medal(competitor_id, "EMTBOC", 1),
        "relay_medal_wmtboc": model.get_first_medal(competitor_id, "WMTBOC", table="relay"),
        "relay_medal_emtboc": model.get_first_medal(competitor_id, "EMTBOC", table="relay"),
        "relay_title_wmtboc": model.get_first_medal(competitor_id, "WMTBOC", 1, table="relay"),
        "relay_title_emtboc": model.get_first_medal(competitor_id, "EMTBOC", 1, table="relay"),
    }

    title = " ".join([current["first"], current["last"]])

    try:
        birth = current["born"].split("-")[0]
    except AttributeError:
        birth = None

    return flask.render_template(
        "competitor.html",
        title=title,
        birth=birth,
        medal_table=medal_table,
        relay_medal_table=relay_medal_table,
        wmtboc_total=WMTBOC_NR,
        wmtboc_competitor=len(my_wmtboc),
        wmtbo_years=", ".join(my_wmtboc),
        emtboc_total=EMTBOC_NR,
        emtboc_competitor=len(my_emtboc),
        emtbo_years=", ".join(my_emtboc),
        first_medals=first_medals,
        medal_names=MEDAL_NAMES,
        races=RACES,
        competitor=current,
        data=data,
        distances=distances,
        flags=tools.IOC_INDEX,
        wmtboc_stats=wmtboc_stats,
        emtboc_stats=emtboc_stats,
        wcup_stats=wcup_stats,
    )


@lru_cache()
@app.route("/medals_table/<event>/")
def medals_table(event="WMTBOC"):
    """
    display medal table for given event type
    params:
        event: event type
    """
    model = Results(mysql)
    medal_lines = [model.get_place_count(place, event.upper()) for place in range(1, 4)]
    relay_lines = [model.get_place_count(place, event.upper(), "relay") for place in range(1, 4)]

    converted = tools.merge_medal_lines(*medal_lines)
    converted_relay = tools.merge_medal_lines(*relay_lines)
    together = tools.merge_medal_dicts(converted, converted_relay)

    ranking = tools.sort_medal_table(converted)
    ranking_relay = tools.sort_medal_table(converted_relay)
    ranking_together = tools.sort_medal_table(together)

    countries = {COMPETITORS[com_id]["nationality"] for com_id in converted.keys()}
    rel_countries = {COMPETITORS[com_id]["nationality"] for com_id in converted_relay.keys()}

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

    title = f"Medals from {tools.EVENT_NAMES[event.upper()]}"

    return flask.render_template(
        "medals.html",
        title=title,
        stats=stats,
        disclaimer=disclaimer,
        table_content=table_content,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@lru_cache()
@app.route("/team_medals_table/<event>/")
def team_medals_table(event="WMTBOC"):
    """
    display medal table for given event type grouped by country
    params:
        event: event type
    """
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

    title = f"Medals from {tools.EVENT_NAMES[event.upper()]}"

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
    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id in at_last_one_participation:
        res = model.get_event_competitor_participation(competitor_id, event.upper())
        if res:
            result[competitor_id] = res

    result = sorted(result.items(), key=lambda kv: len(kv[1]), reverse=True)

    title = tools.EVENT_NAMES[event.upper()]
    tname = f"{event.upper()}_NR"

    return flask.render_template(
        "participations.html",
        title=title,
        total=getattr(sys.modules[__name__], tname),
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

    title = f"Young stars on {tools.EVENT_NAMES[event.upper()]}"
    if place:
        disclaimer = f"Competitors who got a \
            {tools.EVENT_NAMES[event.upper()]} medal in age 24 or younger."
    else:
        disclaimer = f"Competitors who got their first \
            {tools.EVENT_NAMES[event.upper()]} medal before becoming 24."

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

    title = f"Great masters on {tools.EVENT_NAMES[event.upper()]}"
    if place:
        disclaimer = f"Competitors who got a \
            {tools.EVENT_NAMES[event.upper()]} medal in age 35 and older."
    else:
        disclaimer = f"Competitors who got the \
            {tools.EVENT_NAMES[event.upper()]} title in age 35 and older."

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

    if event.upper() in ("WMTBOC", "EMTBOC"):
        data_men, mrace_ids = model.get_summary_medals(year, event.upper())
        data_women, wrace_ids = model.get_summary_medals(year, event.upper(), "F")
        title = f"{tools.EVENT_NAMES[event.upper()]} {year} summary"
        data_relays = model.get_summary_relay_medals(year, event.upper())
        countries = model.get_participating_countries(year, event.upper())
        nr_men = model.count_event_competitors(year, event.upper(), "M")
        nr_women = model.count_event_competitors(year, event.upper(), "F")
        races_info = model.get_summary_venues(year, event.upper())
    elif event.upper() == "WCUP" and organizer:
        data_men, mrace_ids = model.get_summary_medals(year, event.upper(), "M", organizer.upper())
        data_women, wrace_ids = model.get_summary_medals(year, event.upper(), "F", organizer.upper())
        title = f"{tools.EVENT_NAMES[event.upper()]} {organizer.upper()} {year} summary"
        data_relays = model.get_summary_relay_medals(year, event.upper(), organizer.upper())
        countries = model.get_participating_countries(year, event.upper(), organizer.upper())
        nr_men = model.count_event_competitors(year, event.upper(), "M", organizer.upper())
        nr_women = model.count_event_competitors(year, event.upper(), "F", organizer.upper())
        races_info = model.get_summary_venues(year, event.upper(), organizer.upper())
    else:
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

            team_women = tools.prepare_relay_output(women_list)
            team_men = tools.prepare_relay_output(men_list)

        if race_distance == "sprint-relay":
            result_list = model.get_relay_results(race_id, "X")
            result_list = result_list[:6]
            team_mix = tools.prepare_relay_output(result_list)

        if race_distance == "mix-relay":
            result_list = model.get_relay_results(race_id, "X")
            result_list = result_list[:9]
            team_mix = tools.prepare_relay_output(result_list)

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


def insert_wcup(year, totals):
    """
    for local use only, should be called from wordlcup endpoint
    where the totals are calculated for each year
    """
    model = Wcup(mysql)
    model.insert_results(year, totals)


if __name__ == "__main__":
    app.run(debug=True)
