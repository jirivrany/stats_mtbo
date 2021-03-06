# -*- coding: utf-8 -*-


class Results(object):
    """
    Results Model - for table competitor_race
    """

    def __init__(self, mysql):
        self.cursor = mysql.connect().cursor()

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
        self.cursor.execute(query, (competitor_id, ))
        races = list(self.cursor.fetchall())
        query = "SELECT competitor_id, race_id, place, time from competitor_relay WHERE competitor_id = %s"
        self.cursor.execute(query, (competitor_id, ))
        relays = list(self.cursor.fetchall())
        return races+relays

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
        return [str(x[0]) for x in res]

    def get_participation_years(self, event):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT competitor_id, COUNT(race_id) FROM competitor_race WHERE race_id IN (SELECT id FROM races WHERE event='WMTBOC') GROUP BY competitor_id"            
        self.cursor.execute(query)
        return self.cursor.fetchall()

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
                    GROUP BY t1.competitor_id".format(table)
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
                    AND t1.competitor_id = %s".format(table)
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
                    ORDER BY t2.year\
                    LIMIT {}".format(table, limit)
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
                    ORDER BY t2.year DESC\
                    LIMIT {}".format(table, limit)
        self.cursor.execute(query, (place, event, int(competitor_id)))
        return self.cursor.fetchall()
    