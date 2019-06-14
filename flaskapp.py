# -*- coding: utf-8 -*-
import flask
import sys
from flaskext.mysql import MySQL
from models.competitors import Competitors
from models.races import Races
from models.results import Results
import operator
from utils import tools
from collections import defaultdict

mysql = MySQL()
app = flask.Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

mysql.init_app(app)

RACES = Races(mysql).get_all()
COMPETITORS = Competitors(mysql).get_all_present()
WMTBOC_NR = Races(mysql).get_count_by_event('WMTBOC')[0][0]
EMTBOC_NR = Races(mysql).get_count_by_event('EMTBOC')[0][0]
MEDAL_NAMES = {
    1: 'Gold',
    2: 'Silver',
    3: 'Bronze'
}

@app.route('/')
def home():
    wmtboc = Races(mysql).get_by_event('WMTBOC')
    emtboc = Races(mysql).get_by_event('EMTBOC')
    wcup = Races(mysql).get_by_event('WCUP')
    recent = Races(mysql).get_by_year(2019)
    return flask.render_template('index.html', wmtboc=wmtboc, emtboc=emtboc, wcup=wcup, recent=recent)


@app.route('/about/')
def about():
    return flask.render_template('about.html')


@app.route('/all_time_participation/<event>/')
def count(event='WMTBOC'):
    wmtboc = Races(mysql).get_by_event(event.upper())
    per_year = defaultdict(list)
    for mrace in wmtboc:
        per_year[mrace[1]].append(mrace[0])

    title = event.upper()

    wmtboc_table = {year: Results(mysql).get_by_events_id(id_list) for year, id_list in per_year.items()}

    wmtboc_table = {year: (len(flags), flags) for year, flags in wmtboc_table.items()}

    return flask.render_template('count.html', wmtboc=wmtboc_table, flags=tools.IOC_INDEX, title=title)


@app.route('/teams/')
def teams():
    title = "National teams results per year"
    nations = {com['nationality'] for com in COMPETITORS.values()}

    nations = sorted(list(nations))

    return flask.render_template('teams.html', title=title, nations=nations, years=tools.years(), flags=tools.IOC_INDEX)


@app.route('/nation/<code>/<year>/')
def nation(code, year):
    code = code.upper()
    sel_competitors = {
        cid: comp for cid, comp in COMPETITORS.items() if comp['nationality'] == code}
    id_comp = {val['competitor_id'] for val in sel_competitors.values()}

    races_year = Races(mysql).get_by_year(year)
    model = Results(mysql)
    all_results = [model.get_race_results(myrace[0]) for myrace in races_year]
    filtered_results = [[row for row in result if row[0] in id_comp]
                        for result in all_results]
    filtered_results = [result for result in filtered_results if result]

    if filtered_results:
        title = "Team {} results for {}".format(code, year)
        return flask.render_template('races_team.html',
                                     title=title,
                                     results=filtered_results,
                                     competitors=sel_competitors,
                                     race_info=RACES,
                                     years=tools.years(),
                                     team=code)
    else:
        title = "No results for team {} in {}".format(code, year)
        return flask.render_template('races_team_nores.html', title=title)


@app.route('/api/prefetch/competitor/')
def api_search():
    data = [{"name": u"{} {}".format(
        val['first'], val['last']), "id": key} for key, val in COMPETITORS.items()]

    return flask.jsonify(result=data)


@app.route('/api/competitor/<competitor_id>/')
def api_competitor(competitor_id):
    model = Results(mysql)
    data = model.get_competitor_results(competitor_id)
    data.sort(key=operator.itemgetter(2))

    data = [tools.format_competitor_row(row, RACES) for row in data]

    return flask.jsonify(result=data)


@app.route('/race/<race_id>/')
def race(race_id):
    model = Results(mysql)
    race = RACES[int(race_id)]
    data = model.get_race_results(race_id)

    women = [row for row in data if COMPETITORS[row[0]]["gender"] == 'F']
    men = [row for row in data if COMPETITORS[row[0]]["gender"] == 'M']
    country = {COMPETITORS[row[0]]["nationality"] for row in data}

    title = "{} {} {}".format(race['event'], race['year'], race['distance'])

    return flask.render_template('race.html',
                                 title=title,
                                 women=women,
                                 men=men,
                                 stats={'men': len(men), 'women': len(women), 'country': len(country)},
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX,
                                 race=race)


@app.route('/competitor/<competitor_id>/')
def competitor(competitor_id):
    model = Results(mysql)
    current = COMPETITORS[int(competitor_id)]
    medal_table = dict.fromkeys(tools.EVENT_NAMES.keys(), [])
    for event in tools.EVENT_NAMES.keys():
        medal_lines = [
            model.get_competitor_place_count(competitor_id, place, event.upper()) for place in range(1, 4)]

        converted = tools.merge_medal_lines(*medal_lines) 
        try:   
            medal_table[event] = converted[int(competitor_id)]
        except KeyError:
            medal_table[event] = [0,0,0]


    my_wmtboc = model.get_event_competitor_participation(competitor_id, 'WMTBOC')
    my_emtboc = model.get_event_competitor_participation(competitor_id, 'EMTBOC')
    
    first_medal_wmtboc = model.get_first_medal(competitor_id, 'WMTBOC')
    first_medal_emtboc = model.get_first_medal(competitor_id, 'EMTBOC')

    first_title_wmtboc = model.get_first_medal(competitor_id, 'WMTBOC', 1)
    first_title_emtboc = model.get_first_medal(competitor_id, 'EMTBOC', 1)

    title = "{} {}".format(
        current['first'], current['last'])

    birth = current['born'].split('-')[0]

    return flask.render_template('competitor.html',
                                 title=title,
                                 birth=birth,
                                 medal_table=medal_table,
                                 wmtboc_total=WMTBOC_NR,
                                 wmtboc_competitor=len(my_wmtboc),
                                 wmtbo_years=", ".join(my_wmtboc),
                                 emtboc_total=EMTBOC_NR,
                                 emtboc_competitor=len(my_emtboc),
                                 emtbo_years=", ".join(my_emtboc),
                                 first_title_emtboc=first_title_emtboc,
                                 first_title_wmtboc=first_title_wmtboc,
                                 first_medal_emtboc=first_medal_emtboc,
                                 first_medal_wmtboc=first_medal_wmtboc,
                                 medal_names=MEDAL_NAMES,
                                 races=RACES,
                                 competitor=current,
                                 flags=tools.IOC_INDEX)


@app.route('/medals_table/<event>/')
def medals_table(event='WMTBOC'):
    model = Results(mysql)
    medal_lines = [
        model.get_place_count(place, event.upper()) for place in range(1, 4)]

    converted = tools.merge_medal_lines(*medal_lines)
    gold_rank = reversed(
        [y[1] for y in sorted([(converted[x], x) for x in converted.keys()])])

    rank = -1
    skip = 1
    ranking = []
    prew = (0, 0, 0)
    for comp_id in gold_rank:
        curr = converted[comp_id]
        if curr == prew:
            skip += 1
        else:
            rank += skip
            skip = 1

        ranking.append((rank, comp_id))
        prew = curr

    title = "Individual medals from {}".format(tools.EVENT_NAMES[event.upper()])

    return flask.render_template('medals.html',
                                 title=title,
                                 table_data=converted,
                                 sorting=ranking,
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX)


@app.route('/participation/<event>/')    
def participation_in_event(event='WMTBOC'):

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id, participation_nr in at_last_one_participation:
        res = model.get_event_competitor_participation(competitor_id, event.upper())
        if res:
            result[competitor_id] = res
    
    result = sorted(result.items(), key=lambda kv: len(kv[1]), reverse=True)    

    print(result)

    title = tools.EVENT_NAMES[event.upper()]
    tname = "{}_NR".format(event.upper())

    return flask.render_template('participations.html',
                                 title=title,
                                 total=getattr(sys.modules[__name__], tname),
                                 table_data=result,
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX)


@app.route('/young_stars/<event>/')
@app.route('/young_stars/<event>/<int:place>/')      
def young_stars(event='WMTBOC', place=None):

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id, participation_nr in at_last_one_participation:
        if place:
            place = place if place <= 3 else 3
            res = model.get_first_medal(competitor_id, event.upper(), place)
        else:
            res = model.get_first_medal(competitor_id, event.upper(), 1)

        if res:
            try:
                born = int(COMPETITORS[competitor_id]['born'].split('-')[0])
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
        disclaimer = "Competitors who got a {} medal in age 35 and older.".format(tools.EVENT_NAMES[event.upper()])
    else:    
        disclaimer = "Competitors who got their first {} medal before becoming 24.".format(tools.EVENT_NAMES[event.upper()])

    
    return flask.render_template('youngstars.html',
                                 title=title,
                                 disclaimer=disclaimer,
                                 table_data=result,
                                 place=place,
                                 medal_names=MEDAL_NAMES,
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX)


@app.route('/great_masters/<event>/')
@app.route('/great_masters/<event>/<int:place>/')      
def great_masters(event='WMTBOC', place=None):

    model = Results(mysql)

    at_last_one_participation = model.get_participation_years(event)

    result = {}

    for competitor_id, participation_nr in at_last_one_participation:
        if place:
            place = place if place <= 3 else 3
            res = model.get_last_medal(competitor_id, event.upper(), place)
        else:    
            res = model.get_last_medal(competitor_id, event.upper(), 1)
        
        if res:
            try:
                born = int(COMPETITORS[competitor_id]['born'].split('-')[0])
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
        disclaimer = "Competitors who got a {} medal in age 35 and older.".format(tools.EVENT_NAMES[event.upper()])
    else:
        disclaimer = "Competitors who got the {} title in age 35 and older.".format(tools.EVENT_NAMES[event.upper()])

    
    return flask.render_template('youngstars.html',
                                 title=title,
                                 disclaimer=disclaimer,
                                 table_data=result,
                                 place=place,
                                 medal_names=MEDAL_NAMES,
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX)




@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error_404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
