from collections import defaultdict
import pymysql as mdb
import sys


class Wcup(object):
    """Individual World Cup overall Model"""

    def __init__(self, mysql):
        self.connector = mysql.connect()
        self.cursor = self.connector.cursor()

    def insert_results(self, year, results):
        """
        insert results
        :param results list of {'comp_id': 5812,  'points': 340, 'place': 1}
        :return list
        """
        query = "INSERT IGNORE INTO wcup(competitor_id, year, place, points) VALUES(%s, %s, %s, %s)"

        for res in results:
            try:
                self.cursor.execute(
                    query, (res["comp_id"], year, res["place"], res["points"])
                )
            except mdb.Error as e:
                print("Error %d: %s" % (e.args[0], e.args[1]))
                print("DB Query error {}".format(query))
                print("res", res)

            except mdb.err.Warning as e:
                print("Error %d: %s" % (e.args[0], e.args[1]))
                print(res)
                sys.exit(1)

        self.connector.commit()

    def get_overall_summary(self, category="M"):
        query = "SELECT * FROM wcup WHERE place IN (1,2,3) AND competitor_id IN (SELECT id FROM competitors WHERE gender=%s) ORDER BY year DESC, place"
        self.cursor.execute(query, (category,))
        data = self.cursor.fetchall()
        results = defaultdict(list)
        for comp_id, year, place, points in data:
            results[year].append((comp_id, place))

        return results
