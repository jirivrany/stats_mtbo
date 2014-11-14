# -*- coding: utf-8 -*-
import flask
from flaskext.mysql import MySQL
from models.competitors import Competitors
from models.races import Races
from models.results import Results
import operator
from utils import tools
from collections import defaultdict

mysql = MySQL()
app = flask.Flask(__name__)

mysql.init_app(app)
app.config.from_pyfile('flaskapp.cfg')
RACES = Races(mysql).get_all()

COMPETITORS = Competitors(mysql).get_all_present()

@app.route('/')
def home():
    wmtboc = Races(mysql).get_by_event('WMTBOC')
    emtboc = Races(mysql).get_by_event('EMTBOC')
    wcup = Races(mysql).get_by_event('WCUP')
    return flask.render_template('index.html', wmtboc=wmtboc, emtboc=emtboc, wcup=wcup)

@app.route('/nation/<code>/<year>/')
def nation(code, year):

    code = code.upper()
    sel_competitors = {cid: comp for cid, comp in COMPETITORS.iteritems() if comp['nationality'] == code}
    id_comp = {val['competitor_id'] for val in sel_competitors.itervalues()}

    races_year = Races(mysql).get_by_year(year)
    title = "Team {} results for {}".format(code, year)
    model = Results(mysql)
    all_results = [model.get_race_results(race[0]) for race in races_year]
    filered_results = [[row for row in result if row[0] in id_comp] for result in all_results]

    return flask.render_template('races_team.html', title=title, results=filered_results, competitors=sel_competitors, race_info=RACES)


@app.route('/race/<race_id>/')
def race(race_id):
    model = Results(mysql)
    race = RACES[int(race_id)]
    data = model.get_race_results(race_id)

    women = [row for row in data if COMPETITORS[row[0]]["gender"]=='F']
    men = [row for row in data if COMPETITORS[row[0]]["gender"]=='M']
    title = "{} {} {}".format(race['event'], race['year'], race['distance'])

    return flask.render_template('race.html', title=title, women=women, men=men, competitors=COMPETITORS, flags=tools.IOC_INDEX)


@app.route('/competitor/<competitor_id>/')
def competitor(competitor_id):
    model = Results(mysql)
    current = COMPETITORS[int(competitor_id)]
    data = model.get_competitor_results(competitor_id)
    data.sort(key = operator.itemgetter(2))
    title = "{} {} {}".format(current['first'], current['last'], current['nationality'])

    return flask.render_template('competitor.html', title=title, results=data, races=RACES)


@app.route('/medals_table/<event>/')
def medals_table(event):
    model = Results(mysql)
    medal_lines = [model.get_place_count(place, event.upper()) for place in range(1, 4)]

    converted = tools.merge_medal_lines(*medal_lines)
    gold_rank = reversed([y[1] for y in sorted([(converted[x], x) for x in converted.keys()])])

    title = "Medals from world championship"

    return flask.render_template('medals.html',
                                 title=title,
                                 table_data=converted,
                                 sort=gold_rank,
                                 competitors=COMPETITORS,
                                 flags=tools.IOC_INDEX)

@app.route('/sqltest')
def testsql():
    model = Results(mysql)
    data = list(model.get_place_count('1'))
    data.sort(key=operator.itemgetter(1))
    data.reverse()
    # return "{} {}".format(data['first'], data['last'])
    return str(data)


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error_404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
