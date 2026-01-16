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
            "race_id": db_result[0],
            "year": db_result[1],
            "date": db_result[2],
            "distance": db_result[3],
            "event": db_result[4],
            "venue": db_result[5],
            "country": db_result[6],
            "url": db_result[7],
            "map_m": db_result[8],
            "map_w": db_result[9],
            "iofurl": db_result[10],
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

    def get_by_event(self, event, individual_only=False):
        """
        get all races of given event type
        :param event string
        :return list
        """
        if individual_only:
            query = (
                "SELECT * FROM races WHERE event = %s AND team = 0 ORDER BY year DESC"
            )
        else:
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

    def get_individual_ids_by_year(self, year, team=False):
        """
        get team or individual races id held in given year
        :param year string
        :return list
        """
        if team:
            query = "SELECT id FROM races WHERE year = %s AND team=1 ORDER BY date"
        else:
            query = "SELECT id FROM races WHERE year = %s AND team=0 ORDER BY date"

        self.cursor.execute(query, (year,))

        db_result = self.cursor.fetchall()
        res = [x[0] for x in db_result]

        return res

    def get_event_years(self, event):
        """
        get count of events of given event type
        :param event string
        :return list
        """
        query = "SELECT DISTINCT (year), country FROM races WHERE event = %s ORDER BY year DESC;"
        self.cursor.execute(query, (event,))

        db_result = self.cursor.fetchall()

        return db_result

    def get_distances_by_year(self, event):
        """
        Get a dictionary mapping years to distances held for a given event.

        Args:
            event: Event type (WMTBOC, EMTBOC, WCUP)

        Returns:
            dict: {year: [list of distances]}
            Example: {
                2002: ['sprint', 'long', 'relay'],
                2024: ['sprint', 'middle', 'long', 'mass_start', 'relay']
            }
        """
        query = """
            SELECT year, distance
            FROM races
            WHERE event = %s
            GROUP BY year, distance
            ORDER BY year
        """
        self.cursor.execute(query, (event,))
        db_result = self.cursor.fetchall()

        distances_by_year = {}
        for year, distance in db_result:
            distance_normalized = distance.replace("-", "_")
            if year not in distances_by_year:
                distances_by_year[year] = []
            distances_by_year[year].append(distance_normalized)

        return distances_by_year
