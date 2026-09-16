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
            "competitor_id": db_result[0],
            "first": db_result[1],
            "last": db_result[2],
            "nationality": db_result[3],
            "born": db_result[4],
            "gender": db_result[5],
        }

        return result

    def get_nationality_history(self):
        """
        Úseky národností pro závodníky, kteří během kariéry (nebo po ní)
        změnili zemi.

        Řádků je pár desítek, takže se načtou naráz a přiřadí do dictu
        závodníků - dotaz na závodníka by byl 1800 zbytečných dotazů.

        @return {competitor_id: [(country, valid_from, valid_to), ...]}
        """
        query = (
            "SELECT competitor_id, country, valid_from, valid_to"
            " FROM competitor_nationality ORDER BY competitor_id, valid_from"
        )
        self.cursor.execute(query)

        history = {}
        for competitor_id, country, valid_from, valid_to in self.cursor.fetchall():
            history.setdefault(competitor_id, []).append((country, valid_from, valid_to))

        return history

    def get_all_present(self):
        """
        get all competitors with at last one result present
        @return {id : {values}}
        """
        query = "SELECT DISTINCT competitor_id from competitor_race"
        self.cursor.execute(query)

        races = self.cursor.fetchall()

        query = "SELECT DISTINCT competitor_id from competitor_relay"
        self.cursor.execute(query)

        relays = self.cursor.fetchall()
        result = {}

        db_result = races + relays

        for competitor_id in db_result:
            result[competitor_id[0]] = self.get_id(competitor_id)

        # Historie jen tam, kde nějaká je - zbytek závodníků si nechává
        # samotné nationality a rychlou cestu bez dohledávání.
        for competitor_id, history in self.get_nationality_history().items():
            if competitor_id in result:
                result[competitor_id]["nat_history"] = history

        return result
