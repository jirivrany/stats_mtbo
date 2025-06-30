# -*- coding: utf-8 -*-


class Results(object):
    """
    Results Model - for table competitor_race
    """

    def __init__(self, mysql):
        self.cursor = mysql.connect().cursor()

    def get_summary_medals(self, year, event, gender="M", organizer=""):
        """
        get summary of results for given year and event
        """
        query = "SELECT cr.competitor_id, cr.race_id, cr.place, r.distance \
                FROM competitor_race cr \
                JOIN races r ON cr.race_id = r.id \
                JOIN competitors c ON cr.competitor_id = c.id "

        if not organizer:
            query += "WHERE r.year = %s AND r.event = %s "
        else:
            query += "WHERE r.year = %s AND r.event = %s AND r.country = %s "

        query += "AND cr.place IN (1, 2, 3) \
                AND c.gender = %s \
                ORDER BY r.date ASC, cr.place ASC;"
        if not organizer:
            self.cursor.execute(query, (year, event, gender))
        else:
            self.cursor.execute(query, (year, event, organizer, gender))
        query_result = self.cursor.fetchall()

        # Initialize an empty dictionary to store the result
        result_dict = {}
        ids_dict = {}
        # Process the query result and organize it into the dictionary
        for item in query_result:
            competitor_id, race_id, place, event_type = item
            # Create a tuple (competitor_id, place)
            result_tuple = (competitor_id, place)
            ids_dict[event_type] = race_id
            # Append the tuple to the corresponding event type in the dictionary
            result_dict.setdefault(event_type, []).append(result_tuple)

        return result_dict, ids_dict

    def get_participating_countries(self, year, event, organizer=""):
        """
        get list of countries participating in given year and event
        """
        query = "SELECT DISTINCT c.nationality \
                FROM competitor_race cr \
                JOIN races r ON cr.race_id = r.id \
                JOIN competitors c ON cr.competitor_id = c.id "
        if not organizer:
            query += "WHERE r.year = %s AND r.event = %s "
        else:
            query += "WHERE r.year = %s AND r.event = %s AND r.country = %s "

        query += "ORDER BY c.nationality;"
        if not organizer:
            self.cursor.execute(query, (year, event))
        else:
            self.cursor.execute(query, (year, event, organizer))
        return [item[0] for item in self.cursor.fetchall()]

    def count_event_competitors(self, year, event, gender="M", organizer=""):
        """
        count competitors participating in given year and event
        """
        query = "SELECT COUNT(DISTINCT c.id) \
                FROM competitor_race cr \
                JOIN races r ON cr.race_id = r.id \
                JOIN competitors c ON cr.competitor_id = c.id "
        if not organizer:
            query += "WHERE r.year = %s AND r.event = %s "
        else:
            query += "WHERE r.year = %s AND r.event = %s AND r.country = %s "
        query += "AND c.gender = %s;"

        if not organizer:
            self.cursor.execute(query, (year, event, gender))
        else:
            self.cursor.execute(query, (year, event, organizer, gender))

        return self.cursor.fetchone()[0]

    def get_summary_venues(self, year, event, organizer=""):
        """
        get summary of results for given year and event
        """
        query = "SELECT r.date, r.venue \
                FROM races r "
        if not organizer:
            query += "WHERE r.year = %s AND r.event = %s "
        else:
            query += "WHERE r.year = %s AND r.event = %s AND r.country = %s "

        query += "ORDER BY r.date ASC;"

        if not organizer:
            self.cursor.execute(query, (year, event))
        else:
            self.cursor.execute(query, (year, event, organizer))
        return self.cursor.fetchall()

    def get_summary_relay_medals(self, year, event, organizer=""):
        """
        get summary of results for given year and event
        """
        if not organizer:
            query = "SELECT id, distance from races WHERE year = %s AND event = %s AND team = 1"
            self.cursor.execute(query, (year, event))
        else:
            query = "SELECT id, distance from races WHERE year = %s AND event = %s AND country = %s AND team = 1"
            self.cursor.execute(query, (year, event, organizer))

        return self.cursor.fetchall()

    def get_worldcup_points(self, year, gender="M"):
        """
        get results for inidividual wcup and year and category
        """

        query = "SELECT competitor_id, race_id, wcup\
                FROM competitor_race\
                WHERE race_id IN (SELECT id FROM races WHERE year=%s AND team=0 ORDER BY date)\
                AND competitor_id IN (SELECT id FROM competitors WHERE gender = %s)\
                ORDER BY competitor_id;"

        self.cursor.execute(query, (year, gender))
        return self.cursor.fetchall()

    def get_teamworldcup_points(self, year, category="M"):
        """
        get results for team wcup and year
        """

        query = "SELECT competitor_id, race_id, team, wcup\
                FROM competitor_relay\
                WHERE race_id IN (SELECT id FROM races WHERE year=%s AND team=1 ORDER BY date)\
                AND class=%s\
                ORDER BY competitor_id;"

        self.cursor.execute(query, (year, category))
        return self.cursor.fetchall()

    def get_race_results(self, race_id):
        """
        get results of race
        :param int race id
        :return {values}
        """
        query = "SELECT * from competitor_race WHERE race_id = %s ORDER BY place"
        self.cursor.execute(query, (race_id,))
        return self.cursor.fetchall()

    def get_relay_results(self, race_id, klasa):
        """
        get results of relay race
        :param int relay race id
        :return {values}
        """
        query = "SELECT * from competitor_relay WHERE race_id = %s AND class = %s ORDER BY place"
        self.cursor.execute(query, (race_id, klasa))
        res = self.cursor.fetchall()
        return res

    def get_competitor_results(self, competitor_id):
        """
        get all results of competitor
        :return list
        """
        query = "SELECT competitor_id, race_id, place, time from competitor_race WHERE competitor_id = %s"
        self.cursor.execute(query, (competitor_id,))
        races = list(self.cursor.fetchall())
        query = "SELECT competitor_id, race_id, place, time from competitor_relay WHERE competitor_id = %s"
        self.cursor.execute(query, (competitor_id,))
        relays = list(self.cursor.fetchall())
        return races + relays

    def get_by_events_id(self, event_list):
        """
        get all results for several races
        :param event_list
        :return list
        """

        query = """SELECT DISTINCT competitors.nationality
                FROM competitor_race, competitors
                WHERE competitor_race.competitor_id = competitors.id"""

        if len(event_list) == 2:
            query += " AND (competitor_race.race_id = %s OR competitor_race.race_id = %s)"
        elif len(event_list) == 3:
            query += """ AND (competitor_race.race_id = %s
                OR competitor_race.race_id = %s
                OR competitor_race.race_id = %s)"""
        else:
            query += """ AND (competitor_race.race_id = %s
                OR competitor_race.race_id = %s
                OR competitor_race.race_id = %s
                OR competitor_race.race_id = %s)"""

        query += " ORDER BY competitors.nationality"
        self.cursor.execute(query, event_list)
        db_result = self.cursor.fetchall()

        return db_result

    def get_event_competitor_participation(self, competitor_id, event):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT DISTINCT(t2.year) \
                    FROM competitor_race AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t2.event = %s\
                    AND t1.competitor_id = %s\
                    ORDER BY t2.year"
        self.cursor.execute(query, (event, int(competitor_id)))
        res = self.cursor.fetchall()
        res = {str(x[0]) for x in res}

        query2 = "SELECT DISTINCT(t2.year) \
                    FROM competitor_relay AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t2.event = %s\
                    AND t1.competitor_id = %s\
                    ORDER BY t2.year"
        self.cursor.execute(query2, (event, int(competitor_id)))
        res2 = self.cursor.fetchall()
        res2 = {str(x[0]) for x in res2}
        res = list(res.union(res2))

        return sorted(res)

    def get_participation_years(self, event):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """

        query = (
            "SELECT competitor_id, COUNT(race_id) FROM competitor_race "
            "WHERE race_id IN (SELECT id FROM races WHERE event='{}') "
            "GROUP BY competitor_id"
        ).format(event.upper())

        query2 = (
            "SELECT competitor_id, COUNT(race_id) FROM competitor_relay "
            "WHERE race_id IN (SELECT id FROM races WHERE event='{}') "
            "GROUP BY competitor_id"
        ).format(event.upper())

        self.cursor.execute(query)
        res = self.cursor.fetchall()
        res = {key for key, count in res}
        self.cursor.execute(query2)
        res2 = self.cursor.fetchall()
        res2 = {key for key, count in res2}

        return res.union(res2)

    def get_place_count(self, place, event, table="race"):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT t1.competitor_id, COUNT(t1.place)\
                    FROM competitor_{} AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place = %s\
                    AND t2.event = %s\
                    GROUP BY t1.competitor_id".format(
            table
        )
        self.cursor.execute(query, (place, event))
        return self.cursor.fetchall()

    def get_relay_country_place_count(self, place, event):
        """
        Counts how many times each country finished at a given place in relay events.
        Since relay teams are always from a single country, we can get the nationality
        from any team member.

        :param place: int - the place to count (1 for gold, 2 for silver, 3 for bronze)
        :param event: string - the event name
        :return: list of tuples (country, count)
        """

        query = """
            SELECT 
                c.nationality,
                COUNT(DISTINCT cr.race_id, cr.team) as medal_count
            FROM competitor_relay cr
            JOIN races r ON cr.race_id = r.id
            JOIN competitors c ON cr.competitor_id = c.id
            WHERE cr.place = %s 
                AND r.event = %s
            GROUP BY c.nationality
            ORDER BY medal_count DESC
        """

        self.cursor.execute(query, (place, event))
        return self.cursor.fetchall()

    def get_competitor_place_count(self, competitor_id, place, event, table="race"):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT t1.competitor_id, COUNT(t1.place)\
                    FROM competitor_{} AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place = %s\
                    AND t2.event = %s\
                    AND t1.competitor_id = %s".format(
            table
        )
        self.cursor.execute(query, (place, event, int(competitor_id)))
        return self.cursor.fetchall()

    def get_first_medal(self, competitor_id, event, place=3, limit=1, table="race"):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT t2.id, t2.year, t2.distance, t2.date, t1.place\
                    FROM competitor_{} AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place <= %s\
                    AND t2.event = %s\
                    AND t1.competitor_id = %s\
                    ORDER BY t2.date\
                    LIMIT {}".format(
            table, limit
        )
        self.cursor.execute(query, (place, event, int(competitor_id)))
        return self.cursor.fetchall()

    def get_last_medal(self, competitor_id, event, place=3, limit=1, table="race"):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT t2.id, t2.year, t2.distance, t2.date, t1.place\
                    FROM competitor_{} AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place <= %s\
                    AND t2.event = %s\
                    AND t1.competitor_id = %s\
                    ORDER BY t2.date DESC\
                    LIMIT {}".format(
            table, limit
        )
        self.cursor.execute(query, (place, event, int(competitor_id)))
        return self.cursor.fetchall()

    def first_medal_year(self, year, event="WMTBOC", table="race"):
        query = "SELECT t1.competitor_id, t1.place, t2.date\
                    FROM competitor_{} AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place <= 3\
                    AND t2.event = %s\
                    AND t2.year = %s".format(
            table
        )
        self.cursor.execute(query, (event, year))

        result = []
        for comp_id, place, race_date in self.cursor.fetchall():
            med = self.get_first_medal(comp_id, event)
            if med[0][3] == race_date:
                row = {
                    "competitor_id": comp_id,
                    "race_id": med[0][0],
                    "event": event,
                    "race_format": med[0][2],
                    "place": place,
                }
                result.append(row)
        return result

    def get_event_years(self, event):
        """
        Get list of years when a specific event was held
        :param event: string - the event name
        :return: list of years
        """
        query = "SELECT DISTINCT year FROM races WHERE event = %s ORDER BY year DESC"
        self.cursor.execute(query, (event,))
        return [row[0] for row in self.cursor.fetchall()]
