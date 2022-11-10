# -*- coding: utf-8 -*-
import flask
import sys
from flaskext.mysql import MySQL
import operator
from collections import defaultdict
from functools import lru_cache
from datetime import datetime

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
WMTBOC_NR = Races(mysql).get_count_by_event("WMTBOC")[0][0]
EMTBOC_NR = Races(mysql).get_count_by_event("EMTBOC")[0][0]
MEDAL_NAMES = {1: "Gold", 2: "Silver", 3: "Bronze"}
YEAR = 2022

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
}


@lru_cache()
@app.route("/")
def home():
    wmtboc = Races(mysql).get_by_event("WMTBOC")
    emtboc = Races(mysql).get_by_event("EMTBOC")

    wmtboc = sorted(wmtboc, key=lambda x: x[1], reverse=True)
    emtboc = sorted(emtboc, key=lambda x: x[1], reverse=True)

    wcup = Races(mysql).get_by_event("WCUP")
    recent = Races(mysql).get_by_year(YEAR)

    res = Results(mysql)
    first_ms = res.first_medal_year(YEAR)
    first_me = res.first_medal_year(YEAR, event="EMTBOC")
    first = first_ms + first_me
    for comp in first:
        tmp = COMPETITORS[comp["competitor_id"]]
        comp["name"] = "{} {}".format(tmp["first"], tmp["last"])
        comp["team"] = tmp["nationality"]

    return flask.render_template(
        "index.j2",
        wmtboc=wmtboc,
        emtboc=emtboc,
        wcup=wcup,
        recent=recent,
        flags=tools.IOC_INDEX,
        first=first,
        year=YEAR,
    )


@app.route("/about/")
def about():
    return flask.render_template("about.j2")


@lru_cache()
@app.route("/all_time_participation/<event>/")
def count(event="WMTBOC"):
    wmtboc = Races(mysql).get_by_event(event.upper(), True)
    per_year = defaultdict(list)
    for mrace in wmtboc:
        per_year[mrace[1]].append(mrace[0])

    title = event.upper()

    wmtboc_table = {
        year: Results(mysql).get_by_events_id(id_list)
        for year, id_list in per_year.items()
    }

    wmtboc_table = {year: (len(flags), flags) for year, flags in wmtboc_table.items()}

    return flask.render_template(
        "count.j2", wmtboc=wmtboc_table, flags=tools.IOC_INDEX, title=title
    )


@app.route("/teams/")
def teams():
    title = "National teams results per year"
    nations = {com["nationality"] for com in COMPETITORS.values()}

    nations = sorted(list(nations))

    return flask.render_template(
        "teams.j2",
        title=title,
        nations=nations,
        years=tools.years(),
        flags=tools.IOC_INDEX,
    )


@app.route("/nation/<code>/<year>/")
def nation(code, year):
    code = code.upper()
    sel_competitors = {
        cid: comp for cid, comp in COMPETITORS.items() if comp["nationality"] == code
    }
    id_comp = {val["competitor_id"] for val in sel_competitors.values()}

    races_year = Races(mysql).get_by_year(year)
    model = Results(mysql)
    all_results = [model.get_race_results(myrace[0]) for myrace in races_year]
    filtered_results = [
        [row for row in result if row[0] in id_comp] for result in all_results
    ]
    filtered_results = [result for result in filtered_results if result]

    if filtered_results:
        title = "Team {} results for {}".format(code, year)
        return flask.render_template(
            "races_team.j2",
            title=title,
            results=filtered_results,
            competitors=sel_competitors,
            race_info=RACES,
            years=tools.years(),
            team=code,
        )
    else:
        title = "No results for team {} in {}".format(code, year)
        return flask.render_template("races_team_nores.j2", title=title)


@app.route("/api/prefetch/competitor/")
def api_search():
    data = [
        {"name": "{} {}".format(val["first"], val["last"]), "id": key}
        for key, val in COMPETITORS.items()
    ]
    return flask.jsonify(result=data)

@app.route("/worldcup_overall/")
def wcup_overall():
    model = Wcup(mysql)
    men = model.get_overall_summary(category='M')
    women = model.get_overall_summary(category='F')

    return flask.render_template("wcup_overall.j2", 
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
        men=men,
        women=women)

@lru_cache()
@app.route("/worldcup/", defaults={"year": YEAR})
@app.route("/worldcup/<int:year>/")
def wcup(year):
    model = Results(mysql)
    races_model = Races(mysql)
    title = "World Cup {} individual overall standings".format(year)

    current_year = datetime.now().year + 1
    season_race = races_model.get_individual_ids_by_year(year)
    totals_f = model.get_worldcup_points(year, gender="F")
    totals_m = model.get_worldcup_points(year, gender="M")
    counted = WCUP_COUNTED[year]
    counted_text = (
        f"Best {counted} of {len(season_race)} results counted in overall standings."
    )

    totals_f = tools.make_worldup_results(season_race, totals_f, counted)
    totals_m = tools.make_worldup_results(season_race, totals_m, counted)
    
    country = {
        COMPETITORS[row["comp_id"]]["nationality"] for row in totals_m + totals_f
    }

    return flask.render_template(
        "wcup.j2",
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
    model = Results(mysql)
    races_model = Races(mysql)
    title = "Team World Cup {} overall standings".format(year)

    current_year = datetime.now().year + 1
    totals_m = model.get_teamworldcup_points(year, "M")
    totals_f = model.get_teamworldcup_points(year, "W")
    totals_x = model.get_teamworldcup_points(year, "X")
    counted_text = f"All team races are counted in overall standings each year."

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
        "wcup_team.j2",
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
    model = Results(mysql)
    try:
        race = RACES[int(race_id)]
    except KeyError:
        flask.abort(404)

    data = model.get_race_results(race_id)
    title = "{} {} {}".format(
        race["event"], race["year"], DISTANCE_NAMES[race["distance"]]
    )

    if race["distance"] == "relay":
        women_list = model.get_relay_results(race_id, "W")
        men_list = model.get_relay_results(race_id, "M")

        women = tools.prepare_relay_output(women_list)
        men = tools.prepare_relay_output(men_list)
        country = set(men.keys()).union(set(women.keys()))

        return flask.render_template(
            "relay.j2",
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
            race=race,
        )

    elif race["distance"] in ("sprint-relay", "mix-relay"):
        result_list = model.get_relay_results(race_id, "X")
        results = tools.prepare_relay_output(result_list)

        return flask.render_template(
            "mix_relay.j2",
            title=title,
            results=results,
            stats={"teams": len(results.keys())},
            competitors=COMPETITORS,
            flags=tools.IOC_INDEX,
            race=race,
        )
    else:
        women = [row for row in data if COMPETITORS[row[0]]["gender"] == "F"]
        men = [row for row in data if COMPETITORS[row[0]]["gender"] == "M"]
        country = {COMPETITORS[row[0]]["nationality"] for row in data}

        return flask.render_template(
            "race.j2",
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
            race=race,
        )


@lru_cache()
@app.route("/competitor/<competitor_id>/")
def competitor(competitor_id):
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

    first_medals = {
        "medal_wmtboc": model.get_first_medal(competitor_id, "WMTBOC"),
        "medal_emtboc": model.get_first_medal(competitor_id, "EMTBOC"),
        "title_wmtboc": model.get_first_medal(competitor_id, "WMTBOC", 1),
        "title_emtboc": model.get_first_medal(competitor_id, "EMTBOC", 1),
        "relay_medal_wmtboc": model.get_first_medal(
            competitor_id, "WMTBOC", table="relay"
        ),
        "relay_medal_emtboc": model.get_first_medal(
            competitor_id, "EMTBOC", table="relay"
        ),
        "relay_title_wmtboc": model.get_first_medal(
            competitor_id, "WMTBOC", 1, table="relay"
        ),
        "relay_title_emtboc": model.get_first_medal(
            competitor_id, "EMTBOC", 1, table="relay"
        ),
    }

    title = "{} {}".format(current["first"], current["last"])

    try:
        birth = current["born"].split("-")[0]
    except AttributeError:
        birth = None

    return flask.render_template(
        "competitor.j2",
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
    )


@lru_cache()
@app.route("/medals_table/<event>/")
def medals_table(event="WMTBOC"):
    model = Results(mysql)
    medal_lines = [model.get_place_count(place, event.upper()) for place in range(1, 4)]
    relay_lines = [
        model.get_place_count(place, event.upper(), "relay") for place in range(1, 4)
    ]

    converted = tools.merge_medal_lines(*medal_lines)
    converted_relay = tools.merge_medal_lines(*relay_lines)
    together = tools.merge_medal_dicts(converted, converted_relay)

    ranking = tools.sort_medal_table(converted)
    ranking_relay = tools.sort_medal_table(converted_relay)
    ranking_together = tools.sort_medal_table(together)

    countries = {COMPETITORS[com_id]["nationality"] for com_id in converted.keys()}
    rel_countries = {
        COMPETITORS[com_id]["nationality"] for com_id in converted_relay.keys()
    }

    disclaimer = ''
    if event=='wcup':
        disclaimer = "WMTBOC and EMTBOC are World Cup races too. This table contains only the medals from World Cup races other than the championships."


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

    title = "Medals from {}".format(tools.EVENT_NAMES[event.upper()])

    return flask.render_template(
        "medals.j2",
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

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id in at_last_one_participation:
        res = model.get_event_competitor_participation(competitor_id, event.upper())
        if res:
            result[competitor_id] = res

    result = sorted(result.items(), key=lambda kv: len(kv[1]), reverse=True)

    title = tools.EVENT_NAMES[event.upper()]
    tname = "{}_NR".format(event.upper())

    return flask.render_template(
        "participations.j2",
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

    title = "Young stars on {}".format(tools.EVENT_NAMES[event.upper()])
    if place:
        disclaimer = "Competitors who got a {} medal in age 24 or younger.".format(
            tools.EVENT_NAMES[event.upper()]
        )
    else:
        disclaimer = (
            "Competitors who got their first {} medal before becoming 24.".format(
                tools.EVENT_NAMES[event.upper()]
            )
        )

    return flask.render_template(
        "youngstars.j2",
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

    title = "Great masters on {}".format(tools.EVENT_NAMES[event.upper()])
    if place:
        disclaimer = "Competitors who got a {} medal in age 35 and older.".format(
            tools.EVENT_NAMES[event.upper()]
        )
    else:
        disclaimer = "Competitors who got the {} title in age 35 and older.".format(
            tools.EVENT_NAMES[event.upper()]
        )

    return flask.render_template(
        "youngstars.j2",
        title=title,
        disclaimer=disclaimer,
        table_data=result,
        place=place,
        medal_names=MEDAL_NAMES,
        competitors=COMPETITORS,
        flags=tools.IOC_INDEX,
    )


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("error_404.j2"), 404


def insert_wcup(year, totals):
    """
    for local use only
    """
    model = Wcup(mysql)
    model.insert_results(year, totals)



if __name__ == "__main__":
    app.run(debug=True)
