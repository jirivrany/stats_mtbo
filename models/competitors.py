# -*- coding: utf-8 -*-


class Competitors(object):
    """Competitors Model"""
    def __init__(self, mysql):
        self.cursor = mysql.connect().cursor()

    def get_id(self, competitor_id):
        """
        get single competitor by competitor_id
        @return {values}
        """
        query = "SELECT * from competitors WHERE id = %s"
        self.cursor.execute(query, (competitor_id,))

        db_result = self.cursor.fetchone()

        result = {
            'competitor_id': db_result[0],
            'first': db_result[1],
            'last': db_result[2],
            'nationality': db_result[3],
            'born': db_result[4],
            'gender': db_result[5]
        }

        return result

    def get_all_present(self):
        """
        get all competitors with at last one result present
        @return {id : {values}}
        """
        query = "SELECT DISTINCT competitor_id from competitor_race"
        self.cursor.execute(query)

        db_result = self.cursor.fetchall()
        result = {}

        for competitor_id in db_result:
            result[competitor_id[0]] = self.get_id(competitor_id)

        return result
