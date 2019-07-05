# -*- coding: utf-8 -*-


class Races(object):
    """Competitors Model"""

    def __init__(self, mysql):
        self.cursor = mysql.connect().cursor()

    @staticmethod
    def __result_row_to_dict(db_result):
        """
        convert result array to dict
        :param db_result:
        """
        result = {
            'race_id': db_result[0],
            'year': db_result[1],
            'date': db_result[2],
            'distance': db_result[3],
            'event': db_result[4],
            'venue': db_result[5],
            'country': db_result[6],
            'url': db_result[7],
            'map_m': db_result[8],
            'map_w': db_result[9],
            'iofurl': db_result[10]
        }

        return result

    def get_id(self, race_id):
        """
        get single competitor by competitor_id
        :return {values}
        """
        query = "SELECT * from races WHERE id = %s"
        self.cursor.execute(query, (race_id,))

        db_result = self.cursor.fetchone()

        return self.__result_row_to_dict(db_result)

    def get_all(self):
        """
        get all races
        """
        query = "SELECT * from races"
        self.cursor.execute(query)

        db_result = self.cursor.fetchall()
        result = {}
        for race in db_result:
            result[race[0]] = self.__result_row_to_dict(race)

        return result

    def get_by_event(self, event):
        """
        get all races of given event type
        :param event string
        :return list
        """
        query = "SELECT * FROM races WHERE event = %s ORDER BY year DESC"
        self.cursor.execute(query, (event,))

        db_result = self.cursor.fetchall()

        return db_result

    def get_count_by_event(self, event):
        """
        get count of events of given event type
        :param event string
        :return list
        """
        query = "SELECT COUNT(DISTINCT (year)) AS yrcnt FROM races WHERE event = %s;"
        self.cursor.execute(query, (event,))

        db_result = self.cursor.fetchall()

        return db_result

    def get_by_year(self, year):
        """
        get all races held in given year
        :param year string
        :return list
        """
        query = "SELECT * FROM races WHERE year = %s ORDER BY date DESC"
        self.cursor.execute(query, (year,))

        db_result = self.cursor.fetchall()

        return db_result
