# -*- coding: utf-8 -*-


class Results(object):
    """
    Results Model - for table competitor_race
    """

    def __init__(self, mysql):
        self.cursor = mysql.connect().cursor()

    def get_race_results(self, race_id):
        """
        get single competitor by competitor_id
        :return {values}
        """
        query = "SELECT * from competitor_race WHERE race_id = %s ORDER BY place"
        self.cursor.execute(query, (race_id,))
        return self.cursor.fetchall()

    def get_competitor_results(self, competitor_id):
        """
        get all women with at last one result present
        :return {id : {values}}
        """
        query = "SELECT * from competitor_race WHERE competitor_id = %s"
        self.cursor.execute(query, (competitor_id, ))
        return list(self.cursor.fetchall())

    def get_by_events_id(self, event_list):
        """
        get all results for several races
        :param event list
        :return list
        """
        query = """SELECT DISTINCT competitors.nationality
                FROM competitor_race, competitors
                WHERE competitor_race.competitor_id = competitors.id"""


        if len(event_list) == 2:
            query += " AND (competitor_race.race_id = %s OR competitor_race.race_id = %s)"
        else:
            query += """ AND (competitor_race.race_id = %s OR
                        competitor_race.race_id = %s OR competitor_race.race_id = %s)"""

        query += " ORDER BY competitors.nationality"
        self.cursor.execute(query, event_list)
        db_result = self.cursor.fetchall()

        return db_result

    def get_place_count(self, place, event):
        """
        Counts times has some competitor finished on given place
        :param place string
        :param event string
        :return
        """
        query = "SELECT t1.competitor_id, COUNT(t1.place)\
                    FROM competitor_race AS t1\
                    LEFT JOIN races AS t2\
                    ON t1.race_id = t2.id\
                    WHERE t1.place = %s\
                    AND t2.event = %s\
                    GROUP BY t1.competitor_id"
        self.cursor.execute(query, (place, event))
        return self.cursor.fetchall()
