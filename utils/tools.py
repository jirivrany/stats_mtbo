from collections import defaultdict
from datetime import date
from operator import itemgetter

IOC_INDEX = {
    "LIE": "LI",
    "EGY": "EG",
    "LIB": "LB",
    "QAT": "QA",
    "SOM": "SO",
    "BOT": "BW",
    "PAR": "PY",
    "NAM": "NA",
    "FIJ": "FJ",
    "BOL": "BO",
    "GHA": "GH",
    "PAK": "PK",
    "SIN": "SG",
    "CPV": "CV",
    "JOR": "JO",
    "LBR": "LR",
    "SAM": "WS",
    "PUR": "PR",
    "POL": "PL",
    "PRK": "KP",
    "LBA": "LY",
    "LUX": "LU",
    "MYA": "MM",
    "ETH": "ET",
    "UAE": "AE",
    "HKG": "HK",
    "CHA": "TD",
    "TPE": "TW",
    "VAN": "VU",
    "SVK": "SK",
    "CHI": "CL",
    "PHI": "PH",
    "CHN": "CN",
    "SMR": "SM",
    "URU": "UY",
    "JAM": "JM",
    "MRI": "MU",
    "DJI": "DJ",
    "ZIM": "ZW",
    "FIN": "FI",
    "THA": "TH",
    "MAS": "MY",
    "LAO": "LA",
    "YEM": "YE",
    "MAW": "MW",
    "VIE": "VN",
    "KIR": "KI",
    "VIN": "VC",
    "AHO": "AN",
    "ROU": "RO",
    "SYR": "SY",
    "MAD": "MG",
    "LAT": "LV",
    "KAZ": "KZ",
    "TUR": "TR",
    "SUR": "SR",
    "DMA": "DM",
    "GUA": "GT",
    "BEN": "BJ",
    "BEL": "BE",
    "TOG": "TG",
    "GUI": "GN",
    "GUM": "GU",
    "NIG": "NE",
    "CRC": "CR",
    "KSA": "SA",
    "GBS": "GW",
    "DEN": "DK",
    "BER": "BM",
    "GUY": "GY",
    "SKN": "KN",
    "CMR": "CM",
    "GER": "DE",
    "GEQ": "GQ",
    "MAR": "MA",
    "BUR": "BF",
    "HUN": "HU",
    "TKM": "TM",
    "PAN": "PA",
    "BUL": "BG",
    "GEO": "GE",
    "MNE": "ME",
    "TRI": "TT",
    "MHL": "MH",
    "AFG": "AF",
    "BDI": "BI",
    "BLR": "BY",
    "GRE": "GR",
    "GRN": "GD",
    "AND": "AD",
    "MOZ": "MZ",
    "ANG": "AO",
    "IVB": "VG",
    "TJK": "TJ",
    "MGL": "MN",
    "ANT": "AG",
    "MON": "MC",
    "LCA": "LC",
    "IND": "IN",
    "MTN": "MR",
    "INA": "ID",
    "NOR": "NO",
    "CZE": "CZ",
    "SUD": "SD",
    "MLT": "MT",
    "DOM": "DO",
    "KUW": "KW",
    "ISR": "IL",
    "NED": "NL",
    "FSM": "FM",
    "PER": "PE",
    "COD": "CD",
    "ISL": "IS",
    "COK": "CK",
    "COM": "KM",
    "COL": "CO",
    "NEP": "NP",
    "CGO": "CG",
    "MDA": "MD",
    "STP": "ST",
    "ASA": "AS",
    "SEY": "SC",
    "ECU": "EC",
    "SEN": "SN",
    "MDV": "MV",
    "SRB": "RS",
    "FRA": "FR",
    "ZAM": "ZM",
    "LTU": "LT",
    "RWA": "RW",
    "SRI": "LK",
    "FRO": "FO",
    "UKR": "UA",
    "CRO": "HR",
    "AUS": "AU",
    "GBR": "GB",
    "AUT": "AT",
    "VEN": "VE",
    "TAN": "TZ",
    "PLW": "PW",
    "KEN": "KE",
    "OMA": "OM",
    "ALG": "DZ",
    "BRU": "BN",
    "ALB": "AL",
    "TUV": "TV",
    "ITA": "IT",
    "BRN": "BH",
    "PLE": "PS",
    "LES": "LS",
    "TUN": "TN",
    "RUS": "RU",
    "MEX": "MX",
    "BRA": "BR",
    "CIV": "CI",
    "TLS": "TL",
    "CAY": "KY",
    "MKD": "MK",
    "BAR": "BB",
    "NGR": "NG",
    "USA": "US",
    "HAI": "HT",
    "SWE": "SE",
    "AZE": "AZ",
    "SWZ": "SZ",
    "CAN": "CA",
    "CAM": "KH",
    "BAN": "BD",
    "KOR": "KR",
    "CAF": "CF",
    "BAH": "BS",
    "CYP": "CY",
    "BIH": "BA",
    "POR": "PT",
    "SOL": "SB",
    "UZB": "UZ",
    "ERI": "ER",
    "GAM": "GM",
    "TGA": "TO",
    "BIZ": "BZ",
    "GAB": "GA",
    "EST": "EE",
    "ESP": "ES",
    "HON": "HN",
    "IRQ": "IQ",
    "MLI": "ML",
    "IRI": "IR",
    "SLO": "SI",
    "IRL": "IE",
    "ESA": "SV",
    "SSD": "SS",
    "SLE": "SL",
    "NZL": "NZ",
    "SUI": "CH",
    "ISV": "VI",
    "ARU": "AW",
    "JPN": "JP",
    "KGZ": "KG",
    "RSA": "ZA",
    "UGA": "UG",
    "PNG": "PG",
    "ARG": "AR",
    "NCA": "NI",
    "BHU": "BT",
    "ARM": "AM",
    "NRU": "NR",
    "CUB": "CU",
}

# Věkové kategorie. Youth se zavede, až budou data - registr s ním počítá,
# aby přidání znamenalo jeden záznam a nic víc.
ELITE = "elite"
JUNIOR = "junior"
YOUTH = "youth"

# Disciplíny, které se u dané události mohly jet. WMTBOC nikdy nemělo
# smíšenou ani sprintovou štafetu, ostatní ano.
WMTBOC_DISTANCES = ["sprint", "middle", "long", "mass_start", "relay"]
ALL_DISTANCES = [
    "relay",
    "mix_relay",
    "sprint_relay",
    "sprint",
    "middle",
    "long",
    "mass_start",
]

# Jediný seznam událostí v aplikaci. Pořadí klíčů je zároveň pořadím
# zobrazení - dict si ho v Pythonu drží, takže není druhý seznam, který by
# se mohl rozejít. Přesně tím se to dřív rozbíjelo.
#
#   kind            věková kategorie, rozhoduje o oddělení medailí
#   scores_wcup     počítá se do Světového poháru (junioři ne)
#   needs_organizer shrnutí ročníku potřebuje i pořadatele (jen WCUP)
#   title_noun      jak se jmenuje vítěz, do textů na stránce závodníka
#   since           první ročník, do hlášky "nikdy se nezúčastnil"
EVENTS = {
    "WMTBOC": {
        "name": "World MTBO championship",
        "kind": ELITE,
        "slug": "wmtboc",
        "scores_wcup": True,
        "needs_organizer": False,
        "title_noun": "World Champion",
        "since": 2002,
        "distances": WMTBOC_DISTANCES,
    },
    "EMTBOC": {
        "name": "European MTBO championship",
        "kind": ELITE,
        "slug": "emtboc",
        "scores_wcup": True,
        "needs_organizer": False,
        "title_noun": "European Champion",
        "since": 2006,
        "distances": ALL_DISTANCES,
    },
    "WCUP": {
        "name": "MTBO World Cup",
        "kind": ELITE,
        "slug": "wcup",
        "scores_wcup": True,
        "needs_organizer": True,
        "title_noun": "World Cup winner",
        "since": 2010,
        "distances": ALL_DISTANCES,
    },
    "JWMTBOC": {
        "name": "Junior World MTBO championship",
        "kind": JUNIOR,
        "slug": "jwmtboc",
        "scores_wcup": False,
        "needs_organizer": False,
        "title_noun": "Junior World Champion",
        "since": 2008,
        "distances": ALL_DISTANCES,
    },
    "EJMTBOC": {
        "name": "European Junior MTBO championship",
        "kind": JUNIOR,
        "slug": "ejmtboc",
        "scores_wcup": False,
        "needs_organizer": False,
        "title_noun": "European Junior Champion",
        "since": 2018,
        "distances": ALL_DISTANCES,
    },
    # Mistrovství světa pro kategorii M17/W17 neexistuje, jezdí se jen
    # evropské. Nekonalo se 2018 (výsledky nejsou v Eventoru) a 2020 (covid).
    "EYMTBOC": {
        "name": "European Youth MTBO championship",
        "kind": YOUTH,
        "slug": "eymtboc",
        "scores_wcup": False,
        "needs_organizer": False,
        "title_noun": "European Youth Champion",
        "since": 2016,
        "distances": ALL_DISTANCES,
    },
}

# Zpětná kompatibilita - spousta míst hledá jen název události.
EVENT_NAMES = {code: meta["name"] for code, meta in EVENTS.items()}


def get_event(code):
    """
    Popis události podle kódu, nebo None. Kód je case-insensitive, protože
    v URL chodí malými písmeny.
    """
    if not code:
        return None

    return EVENTS.get(code.upper())


def event_codes(kind=None):
    """
    Kódy událostí v pořadí registru.

    :param kind: jedna kategorie ("elite") nebo víc ({"junior", "youth"});
                 None vrátí všechny
    """
    if kind is None:
        return list(EVENTS)

    wanted = {kind} if isinstance(kind, str) else set(kind)

    return [code for code, meta in EVENTS.items() if meta["kind"] in wanted]


def non_elite_codes():
    """
    Všechno, co není elita. Až přibude youth, spadne sem sám - proto se
    nikde neptáme "je to junior", ale "není to elita".
    """
    return event_codes({JUNIOR, YOUTH})


def is_junior(code):
    """Je to mládežnická kategorie (junioři nebo youth)?"""
    meta = get_event(code)

    return bool(meta) and meta["kind"] in (JUNIOR, YOUTH)


def wcup_scoring_events():
    """
    Události, které se počítají do Světového poháru.

    Juniorské závody se jezdí ve stejných letech jako elitní, takže bez
    tohohle filtru by se dostaly do tabulek Světového poháru jako prázdné
    sloupce.
    """
    return [code for code, meta in EVENTS.items() if meta["scores_wcup"]]


def prepare_relay_output(source_list):
    """
    Rozděluje výsledky štafet na dva seznamy - oficiálně hodnocené týmy
    a ostatní (druhé týmy federace bez umístění, chyby ražení).

    Klíčem je dvojice (země, stav): jedna federace může mít víc týmů,
    ale jen jeden z nich je hodnocený.
    """
    teams = defaultdict(list)
    for row in source_list:
        teams[(row[5], row[7])].append(row)

    classified = {}
    others = []
    for (ioc_code, state), members in teams.items():
        members = sorted(members, key=lambda x: x[4])
        country = ioc_code.upper()
        team = {
            "place": members[0][2],
            "country": country,
            "flag": IOC_INDEX[country].lower(),
            "time": members[0][3],
            "state": state,
            "members": [(x[0], x[4]) for x in members],
        }
        if state == "counted":
            classified[ioc_code] = team
        else:
            others.append(team)

    others.sort(key=lambda t: (t["time"] is None, t["time"] or ""))

    return classified, others


def prepare_medal_table(model, competitor_id, table="race", events=None):
    """
    Medaile závodníka po událostech.

    :param events: které události počítat; None vezme všechny z registru.
                   Elitní a juniorské se zobrazují odděleně, takže si volající
                   řekne o jednu skupinu.
    :return: {kód události: [zlaté, stříbrné, bronzové]} v pořadí registru
    """
    mkeys = list(events) if events else event_codes()

    medal_table = {event: [0, 0, 0] for event in mkeys}
    for event in mkeys:
        medal_lines = [
            model.get_competitor_place_count(competitor_id, place, event.upper(), table) for place in range(1, 4)
        ]

        converted = merge_medal_lines(*medal_lines)
        try:
            medal_table[event] = converted[int(competitor_id)]
        except KeyError:
            medal_table[event] = [0, 0, 0]

    return medal_table


def merge_medal_dicts(rank_a, rank_b):
    """
    rank_a = {270: [2, 2, 2], 313: [2, 1, 1]}
    rank_b = {270: [1, 1, 0], 230: [1, 1, 1]}

    expected_result = {
      270: [3, 3, 2],
      313: [2, 1, 1],
      230: [1, 1, 1]
    }
    """
    result = {}
    for key, val in rank_a.items():
        try:
            result[key] = [a + b for a, b in zip(val, rank_b[key])]
        except KeyError:
            result[key] = val

    have = set(result.keys())
    intheb = set(rank_b.keys())
    needed = intheb.difference(have)

    for key in needed:
        result[key] = rank_b[key]

    return result


def sort_medal_table(converted):
    gold_rank = reversed([y[1] for y in sorted([(converted[x], x) for x in converted.keys()])])

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

    return ranking


def years():
    """
    prepare list of years from 2002 till now
    exclude 2003
    """

    years = [
        2002,
    ]
    years.extend(range(2004, date.today().year + 1))
    years.reverse()

    return years


def create_base_dict(line_a, line_b, line_c):
    """
    base dict for medal table merging
    :return {id: [0, 0, 0]}
    """
    lines = line_a + line_b + line_c
    return {val[0]: [0, 0, 0] for val in lines}


def merge_medal_lines(line_a, line_b, line_c):
    """
    return: merged medal lines lines
    """
    result = create_base_dict(line_a, line_b, line_c)

    lines = [line_a, line_b, line_c]
    for pos, line in enumerate(lines):
        for id_, val in line:
            result[id_][pos] = val

    return result


def format_competitor_row(row, races):
    """
    :param row: result from competitor_race
    :param races: races info
    :return: list of formated values
    """
    daystr = races[row[1]]["date"].strftime("%a %b %d %Y")

    return {
        "race_id": row[1],
        "date": daystr,
        "result": row[2],
        "dist": races[row[1]]["distance"].lower().replace("-", "_"),
        "event": races[row[1]]["event"],
        "rtime": row[3],
    }


def make_worldup_results(races, results, counted=6):
    """
    create sorted worlcup results list
    :param races: list of races in year
    :param results: tuple of (comp_id, race_id, place) from db
    """

    results_basic = defaultdict(dict)
    for comp_id, race_id, place in results:
        results_basic[comp_id][race_id] = place

    results_full = []
    for comp_id, comp_races in results_basic.items():
        scores = sorted(comp_races.values(), reverse=True)
        results_full.append(
            {
                "comp_id": comp_id,
                "results": [comp_races.get(race_id, "-") for race_id in races],
                "mark_results": scores[:counted],
                "points": sum(scores[:counted]),
                "b1": max(scores),
                "b2": scores[1] if len(scores) > 1 else 0,
                "b3": scores[2] if len(scores) > 2 else 0,
            }
        )

    return sort_full_results(results_full)


def sort_full_results(results):
    results.sort(key=itemgetter("points", "b1", "b2", "b3"), reverse=True)
    for i in range(len(results)):
        results[i]["place"] = i + 1 if results[i]["points"] > 0 else ""

    return results


def make_team_worldup_results_base(results, category="M"):
    """
    create sorted team worlcup results list
    :param races: list of races in year
    :param results: tuple of (comp_id, race_id, place) from db
    :param competitors: dictionary with competitors
    """
    results_basic = defaultdict(dict)
    all_races = set()
    for comp_id, race_id, team, score in results:
        key = f"{race_id}-{category}"
        results_basic[team][key] = {"members": [], "points": 0}
        all_races.add(key)

    for comp_id, race_id, team, score in results:
        key = f"{race_id}-{category}"
        results_basic[team][key]["points"] = score
        results_basic[team][key]["members"].append(comp_id)

    return results_basic, all_races


def make_team_worldup_results(season_race, men={}, women={}, mix={}):
    res = merge_res_dicts(men, women, mix)

    resu = {}
    for key, vals in res.items():
        resu[key] = {
            "members": [vvv["members"] for vvv in vals.values()],
            "races": {k: v["points"] for k, v in vals.items()},
            "points": sum(www["points"] for www in vals.values()),
        }

    for key in resu.keys():
        resu[key]["members"] = list(set(flatten(resu[key]["members"])))
        temp = {k: v for k, v in sorted(resu[key]["races"].items())}
        scores = sorted((int(i) for i in temp.values()))
        resu[key]["team"] = key
        resu[key]["b1"] = max(scores)
        resu[key]["b2"] = scores[1] if len(scores) > 1 else 0
        resu[key]["b3"] = scores[2] if len(scores) > 2 else 0
        resu[key]["races"] = [temp.get(race_id, "-") for race_id in sorted(season_race)]

    return sort_full_results(list(resu.values()))


def merge_res_dicts(dict1, dict2, dict3):
    keyset = set(dict1.keys()) | set(dict2.keys()) | set(dict3.keys())
    result = {key: {} for key in keyset}
    for key in keyset:
        if key in dict1:
            result[key].update(dict1[key])
        if key in dict2:
            result[key].update(dict2[key])
        if key in dict3:
            result[key].update(dict3[key])

    return result


def flatten(data: list):
    return [item for sublist in data for item in sublist]


def aggregate_medals_by_country(converted, competitors):
    converted_by_country = defaultdict(list)
    for com_id, medals in converted.items():
        country = competitors[com_id]["nationality"]
        # list have exactly 3 items, one for each medal place, we need to sum position 1 with postiton 1 in list, etc.
        current = converted_by_country[country]
        if not current:
            converted_by_country[country] = medals
        else:
            converted_by_country[country] = [sum(x) for x in zip(current, medals)]

    return converted_by_country


def medal_countries(converted, competitors):
    """
    Kódy zemí, které mají v tabulce aspoň jednu medaili.

    Staví se ze sloučené tabulky (individuál + štafety), aby žádná vlajka
    nevedla na prázdnou stránku - SVK má třeba na WMTBOC jen štafetové
    medaile, ale filtr pro něj smysl má.
    """
    return sorted({competitors[com_id]["nationality"] for com_id in converted if com_id in competitors})


def filter_medal_table(converted, ranking, competitors, country=None):
    """
    Podmnožina medailové tabulky pro jednu zemi.

    Globální pořadí se nepočítá znovu - bere se z už hotového žebříčku nad
    celým polem, takže i po odfiltrování sedí včetně dělených míst.

    :param converted: {competitor_id: [zlato, stříbro, bronz]}
    :param ranking: [(globální_pořadí, competitor_id), ...] nad celým polem
    :param competitors: registr závodníků kvůli národnosti
    :param country: kód země, None nechá tabulku beze změny
    :return: (filtrovaný dict, [(lokální_pořadí, globální_pořadí, competitor_id), ...])

    Bez filtru je lokální pořadí rovno globálnímu - šablona tak má pořád
    stejný tvar řádku a nemusí se ptát, jestli se filtruje.
    """
    if country is None:
        return converted, [(rank, rank, com_id) for rank, com_id in ranking]

    filtered = {
        com_id: medals
        for com_id, medals in converted.items()
        if com_id in competitors and competitors[com_id]["nationality"] == country
    }

    filtered_ranking = []
    local = -1
    skip = 1
    prev = None
    for global_rank, com_id in ranking:
        if com_id not in filtered:
            continue

        # Stejný počet medailí = stejné místo i v národní tabulce.
        current = filtered[com_id]
        if current == prev:
            skip += 1
        else:
            local += skip
            skip = 1

        filtered_ranking.append((local, global_rank, com_id))
        prev = current

    return filtered, filtered_ranking


def get_career_best_by_event_and_distance(competitor_results, races):
    """
    Calculate career best results grouped by event and distance.

    Args:
        competitor_results: List of formatted competitor results with structure:
            [{'race_id': int, 'date': str, 'result': int, 'dist': str, 'event': str, 'rtime': str}, ...]
        races: Dictionary of race information keyed by race_id

    Returns:
        Dictionary with structure:
        {
            'WMTBOC': {
                'individual': {'sprint': {...}, 'middle': {...}, ...},
                'relay': {'relay': {...}, 'mix_relay': {...}, ...}
            },
            'EMTBOC': {...},
            'WCUP': {...}
        }
    """
    # Define distance categories
    INDIVIDUAL_DISTANCES = ["sprint", "middle", "long", "mass_start"]
    RELAY_DISTANCES = ["relay", "mix_relay", "sprint_relay"]

    # Initialize result structure
    career_best = {code: {"individual": {}, "relay": {}} for code in event_codes()}

    # Process each result
    for result in competitor_results:
        event = result["event"]
        distance = result["dist"]
        place = result["result"]
        race_id = result["race_id"]

        # Skip if event not recognized
        if event not in career_best:
            continue

        # Determine if individual or relay
        if distance in INDIVIDUAL_DISTANCES:
            category = "individual"
        elif distance in RELAY_DISTANCES:
            category = "relay"
        else:
            continue

        # Get race details
        race_info = races.get(race_id, {})

        # Check if this is a better result than existing
        existing = career_best[event][category].get(distance)

        if existing is None or place < existing["place"]:
            # Get team info for relay races
            team = None
            if category == "relay" and race_id in races:
                # Team info would need to come from competitor_relay table
                # For now, we'll leave it as None and handle it in database query
                team = None

            career_best[event][category][distance] = {
                "place": place,
                "year": race_info.get("year"),
                "race_id": race_id,
                "time": result.get("rtime"),
                "date": race_info.get("date"),
                "team": team,
            }

    return career_best


def process_career_best_from_db(individual_results, relay_results):
    """
    Process raw database results into career best structure grouped by event.

    Args:
        individual_results: Tuple from get_career_best_with_teams() - individual races
            Format: (distance, event, place, year, race_id, time, date)
        relay_results: Tuple from get_career_best_with_teams() - relay races
            Format: (distance, event, place, year, race_id, time, date, team)

    Returns:
        Dictionary with structure:
        {
            'WMTBOC': {'individual': {}, 'relay': {}},
            'EMTBOC': {'individual': {}, 'relay': {}},
            'WCUP': {'individual': {}, 'relay': {}}
        }
    """
    career_best = {code: {"individual": {}, "relay": {}} for code in event_codes()}

    # Process individual results
    for row in individual_results:
        distance, event, place, year, race_id, time, date = row

        # Normalize distance name (replace hyphens with underscores)
        distance_normalized = distance.replace("-", "_")

        # Skip if event not recognized
        if event not in career_best:
            continue

        # Check if this is better than existing result
        existing = career_best[event]["individual"].get(distance_normalized)

        if existing is None or place < existing["place"]:
            career_best[event]["individual"][distance_normalized] = {
                "place": place,
                "year": year,
                "race_id": race_id,
                "time": time,
                "date": date,
            }

    # Process relay results
    for row in relay_results:
        distance, event, place, year, race_id, time, date, team = row

        # Normalize distance name
        distance_normalized = distance.replace("-", "_")

        # Skip if event not recognized
        if event not in career_best:
            continue

        # Check if this is better than existing result
        existing = career_best[event]["relay"].get(distance_normalized)

        if existing is None or place < existing["place"]:
            career_best[event]["relay"][distance_normalized] = {
                "place": place,
                "year": year,
                "race_id": race_id,
                "time": time,
                "date": date,
                "team": team,
            }

    return career_best


def analyze_event_completeness(career_best_data, event="WMTBOC"):
    """
    Analyze how complete a competitor's results are for a given event.
    Useful for finding "Grand Slam" winners or versatile competitors.

    Args:
        career_best_data: Output from get_career_best_by_event_and_distance
        event: 'WMTBOC', 'EMTBOC', or 'WCUP'

    Returns:
        Dictionary with analysis:
        {
            'individual_distances_competed': 4,
            'relay_distances_competed': 2,
            'has_medal_all_individual': False,
            'has_won_all_individual': False,
            'medal_count_individual': 2,
            'medal_count_relay': 1,
            'distances_best': {'sprint': 1, 'middle': 3, 'long': 5, ...}
        }
    """
    event_data = career_best_data.get(event, {"individual": {}, "relay": {}})

    individual = event_data.get("individual", {})
    relay = event_data.get("relay", {})

    # Count medals (places 1-3)
    individual_medals = sum(1 for dist, data in individual.items() if data["place"] <= 3)
    relay_medals = sum(1 for dist, data in relay.items() if data["place"] <= 3)

    # Count wins (place 1)
    individual_wins = sum(1 for dist, data in individual.items() if data["place"] == 1)
    relay_wins = sum(1 for dist, data in relay.items() if data["place"] == 1)

    # Build distances_best dictionary with all possible distances
    # Use 99999 for distances never competed (DNF/DSQ equivalent)
    distances_best = {}

    # Fill in best places for each distance competed, pass if not competed
    meta = get_event(event)
    for distance in meta["distances"] if meta else ALL_DISTANCES:
        if distance in individual:
            distances_best[distance] = individual[distance]["place"]
        elif distance in relay:
            distances_best[distance] = relay[distance]["place"]

    distances_score = sum(distances_best.values())

    return {
        "individual_distances_competed": len(individual),
        "relay_distances_competed": len(relay),
        "total_distances_competed": len(individual) + len(relay),
        "individual_medals": individual_medals,
        "relay_medals": relay_medals,
        "total_medals": individual_medals + relay_medals,
        "individual_wins": individual_wins,
        "relay_wins": relay_wins,
        "total_wins": individual_wins + relay_wins,
        "has_medal_all_individual": individual_medals == len(individual) and len(individual) > 0,
        "has_won_all_individual": individual_wins == len(individual) and len(individual) > 0,
        "distances_best": distances_best,
        "distances_score": distances_score,
        "has_won_all": individual_wins + relay_wins == len(individual) + len(relay)
        and (len(individual) + len(relay)) > 0,
    }


def calculate_grand_slam_score(career_best_data, distances_by_year, event="WMTBOC"):
    """
    Calculate Grand Slam score considering historical distance availability.

    A competitor is a Grand Slam winner if they won all distances that existed
    during any year they competed (career-based), with a minimum of 3 wins.

    Args:
        career_best_data: Output from process_career_best_from_db()
        distances_by_year: Dict mapping years to list of distances, from Races.get_distances_by_year()
        event: Event type (WMTBOC, EMTBOC, WCUP)

    Returns:
        Dictionary with:
        - is_grand_slam_winner: True if won all available distances AND at least 3 wins
        - available_distances: set of distances that existed during competitor's career
        - won_distances: set of distances won (place=1)
        - completion_percentage: won_distances / available_distances (0-100)
        - years_competed: set of years the competitor has results
    """
    event_data = career_best_data.get(event, {"individual": {}, "relay": {}})
    individual = event_data.get("individual", {})
    relay = event_data.get("relay", {})

    # Find years the competitor competed in (from their best results)
    years_competed = set()
    for dist_data in individual.values():
        if "year" in dist_data:
            years_competed.add(dist_data["year"])
    for dist_data in relay.values():
        if "year" in dist_data:
            years_competed.add(dist_data["year"])

    # Get union of all distances available during those years
    available_distances = set()
    for year in years_competed:
        if year in distances_by_year:
            available_distances.update(distances_by_year[year])

    # Find distances won (place == 1)
    won_distances = set()
    for distance, data in individual.items():
        if data["place"] == 1:
            won_distances.add(distance)
    for distance, data in relay.items():
        if data["place"] == 1:
            won_distances.add(distance)

    # Calculate completion percentage
    if available_distances:
        completion_percentage = (len(won_distances) / len(available_distances)) * 100
    else:
        completion_percentage = 0

    # Grand Slam: won all available distances AND at least 3 wins
    is_grand_slam_winner = (
        len(won_distances) >= 3
        and len(won_distances) == len(available_distances)
        and len(available_distances) > 0
    )

    return {
        "is_grand_slam_winner": is_grand_slam_winner,
        "available_distances": available_distances,
        "won_distances": won_distances,
        "completion_percentage": completion_percentage,
        "years_competed": years_competed,
    }


def count_medals_by_event(individual_results, relay_results, event):
    """
    Count total medals (gold, silver, bronze) for a competitor at a specific event.

    Args:
        individual_results: Raw results from get_career_best_with_teams() - individual races
            Format: (distance, event, place, year, race_id, time, date)
        relay_results: Raw results from get_career_best_with_teams() - relay races
            Format: (distance, event, place, year, race_id, time, date, team)
        event: Event type to filter (WMTBOC, EMTBOC, WCUP)

    Returns:
        Dictionary with:
        - gold: count of 1st places
        - silver: count of 2nd places
        - bronze: count of 3rd places
        - medals_str: formatted string "G-S-B" (e.g., "4-2-0")
    """
    gold = 0
    silver = 0
    bronze = 0

    # Count from individual results
    for row in individual_results:
        row_event = row[1]
        place = row[2]
        if row_event == event and place <= 3:
            if place == 1:
                gold += 1
            elif place == 2:
                silver += 1
            elif place == 3:
                bronze += 1

    # Count from relay results
    for row in relay_results:
        row_event = row[1]
        place = row[2]
        if row_event == event and place <= 3:
            if place == 1:
                gold += 1
            elif place == 2:
                silver += 1
            elif place == 3:
                bronze += 1

    return {
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
        "medals_str": f"{gold}-{silver}-{bronze}",
    }


# Práh mezi ID z IOF archivu a ID z Eventoru. Archivní ID jsou v datech
# 0-457, eventorová od 3868 výš, takže se rozsahy nepřekrývají.
IOF_ARCHIVE_MAX_ID = 1000

IOF_ARCHIVE_URL = "https://old.orienteering.sport/events/{}/"
EVENTOR_EVENT_URL = "https://eventor.orienteering.sport/Events/Show/{}"


def results_link(race):
    """
    Odkaz na oficiální výsledky závodu.

    Zdroj se pozná podle hodnoty iofurl:
        < 1000  ID v IOF archivu (staré závody, dnes na old.orienteering.sport)
        >= 1000 Eventor ID, když se liší od primárního klíče
        None    Eventor ID je zároveň primární klíč závodu

    Staré štafety (id 1-23) jsou v databázi od začátku a v Eventoru nejsou
    vůbec - jejich id není eventorové, takže odkaz nevzniká.

    :param race: dict závodu z models.races
    :return: (text odkazu, url) nebo None, když odkaz sestavit nejde
    """
    iofurl = race.get("iofurl")

    if iofurl is None:
        race_id = race.get("race_id")
        if not race_id or race_id < IOF_ARCHIVE_MAX_ID:
            return None
        return ("Eventor results page", EVENTOR_EVENT_URL.format(race_id))

    if iofurl < IOF_ARCHIVE_MAX_ID:
        return ("IOF results page", IOF_ARCHIVE_URL.format(iofurl))

    return ("Eventor results page", EVENTOR_EVENT_URL.format(iofurl))


# Kategorie vítězů v přehledu závodů. Pohlaví je u závodníka jako F/M,
# štafetové třídy jsou W/M/X - sjednocuje se na W/M/X, aby stačil jeden
# slovník názvů (RELAY_FORMATS ve flaskapp).
WINNER_GROUP_ORDER = ("W", "M", "X")


def _champion(group, members, team=False):
    """Jeden vítěz do přehledu - jednotlivec i štafeta vypadají stejně."""
    return {"group": group, "team": team, "members": members}


def build_race_history(races, individual_winners, relay_winners, competitors):
    """
    Závody jedné události spolu s vítězi, připravené pro šablonu.

    Individuální vítěz je člověk (dva na závod - muž a žena), štafetový je
    tým. Šablona to nesmí rozlišovat, proto mají oba stejný tvar: seznam
    členů, kde každý nese i svou zemi. Jednotlivec je tedy tým o jednom,
    dělené první místo tým o dvou, štafeta o třech.

    Země je u každého člena zvlášť, protože dělená první místa bývají
    napříč státy - u štafety se jen třikrát zopakuje ta samá.

    :param races: řádky z Races.get_by_event
    :param individual_winners: (race_id, competitor_id) z Results
    :param relay_winners: (race_id, class, team, competitor_id) z Results
    :param competitors: slovník závodníků (flaskapp.COMPETITORS)
    :return: seznam dictů, nejnovější závod první
    """
    def named(competitor_id):
        person = competitors.get(competitor_id)
        if not person:
            return None

        return (competitor_id, f"{person['first']} {person['last']}", person["nationality"])

    # individuálové: nejdřív podle závodu, pak podle pohlaví
    by_race = {}
    for race_id, competitor_id in individual_winners:
        person = competitors.get(competitor_id)
        entry = named(competitor_id)
        if not person or not entry:
            continue
        group = "W" if person["gender"] == "F" else "M"
        by_race.setdefault(race_id, {}).setdefault(group, []).append(entry)

    # štafety: podle závodu, třídy a týmu
    by_relay = {}
    for race_id, klasa, team, competitor_id in relay_winners:
        entry = named(competitor_id)
        if not entry:
            continue
        by_relay.setdefault(race_id, {}).setdefault((klasa, team), []).append(entry)

    history = []
    for row in races:
        race_id = row[0]
        champions = []

        for group in WINNER_GROUP_ORDER:
            members = by_race.get(race_id, {}).get(group)
            if members:
                champions.append(_champion(group, members))

        relays = by_relay.get(race_id, {})
        for klasa, team in sorted(
            relays, key=lambda key: (WINNER_GROUP_ORDER.index(key[0]), key[1])
        ):
            champions.append(_champion(klasa, relays[(klasa, team)], team=True))

        history.append(
            {
                "race_id": race_id,
                "year": row[1],
                "date": row[2],
                "distance": row[3],
                "venue": row[5],
                "country": row[6],
                "champions": champions,
            }
        )

    # nejnovější první; datum a id dělají řazení jednoznačné, protože
    # v jeden den se jede víc závodů
    history.sort(key=lambda race: (race["year"], race["date"], race["race_id"]), reverse=True)

    return history


# --- Progression: z juniorů mezi elitu ---

# Větve kariéry. Každá je uzavřená sama v sobě - světové a evropské
# tituly se nemíchají, protože "juniorský mistr světa se stal mistrem
# Evropy" je jiný příběh než postup uvnitř téže soutěže.
#
# Youth má jen evropskou variantu, mistrovství světa pro M17/W17
# neexistuje. WCUP tu není vůbec - juniorský ani mládežnický Světový
# pohár se nejede, takže by nebylo co s čím párovat.
#
# Kódy jsou vyjmenované schválně, ne odvozené z event_codes(kind) -
# ten by slil JWMTBOC s EJMTBOC do jedné skupiny.
CAREER_PATHS = {
    "world": {
        "name": "World",
        "groups": (("Junior", ("JWMTBOC",)), ("Elite", ("WMTBOC",))),
    },
    "europe": {
        "name": "European",
        "groups": (("Junior", ("EJMTBOC",)), ("Elite", ("EMTBOC",))),
    },
    "full": {
        "name": "European",
        "groups": (
            ("Youth", ("EYMTBOC",)),
            ("Junior", ("EJMTBOC",)),
            ("Elite", ("EMTBOC",)),
        ),
    },
}


def career_path(path):
    """Popis větve podle klíče z URL, nebo None."""
    if not path:
        return None

    return CAREER_PATHS.get(path.lower())


def path_events(groups):
    """Všechny kódy událostí větve - na filtr dotazu do databáze."""
    return [code for _, codes in groups for code in codes]


def build_progression(medals, competitors, groups, place=3):
    """
    Závodníci, kteří získali medaili v KAŽDÉ etapě kariéry.

    Čistá funkce nad výstupem Results.get_individual_medals(), aby šla
    testovat bez databáze.

    :param medals: (competitor_id, event, year, race_id, distance, place)
    :param competitors: mapa id -> závodník (COMPETITORS)
    :param groups: ((jméno, (kódy událostí, ...)), ...) v pořadí kariéry
    :param place: nejhorší započítané umístění; 1 dělá variantu "champions"
    :return: [{competitor_id, name, nationality, stages, gap}] seřazené
             podle roku první medaile v poslední etapě
    """
    # kód události -> jméno etapy
    stage_of = {code: stage for stage, codes in groups for code in codes}

    collected = {}
    for competitor_id, event, year, race_id, distance, result in medals:
        stage = stage_of.get(event)
        if stage is None or not result or result > place:
            continue

        stages = collected.setdefault(competitor_id, {})
        entry = stages.setdefault(stage, {"first": None, "medals": [0, 0, 0]})
        entry["medals"][result - 1] += 1

        # první medaile = nejstarší; při shodě roku lepší umístění
        current = entry["first"]
        candidate = (year, race_id, distance, result)
        if current is None or (year, result) < (current[0], current[3]):
            entry["first"] = candidate

    wanted = [stage for stage, _ in groups]

    progression = []
    for competitor_id, stages in collected.items():
        if not all(stage in stages for stage in wanted):
            continue

        person = competitors.get(competitor_id)
        if person is None:
            continue

        first_year = stages[wanted[0]]["first"][0]
        last_year = stages[wanted[-1]]["first"][0]
        progression.append(
            {
                "competitor_id": competitor_id,
                "name": f"{person['first']} {person['last']}",
                "nationality": person["nationality"],
                "stages": stages,
                "gap": last_year - first_year,
            }
        )

    # Řadí se podle počtu let, za které to jezdec zvládl - nejrychlejší
    # přechod první. Původně to bylo podle roku první elitní medaile, jenže
    # to nebyl žebříček, ale časová osa: nahoru se dostal ten, kdo závodil
    # dřív, ne ten, komu se to povedlo nejlíp. Gap je srovnatelný napříč
    # generacemi. Při shodě rozhoduje starší přechod.
    progression.sort(
        key=lambda row: (
            row["gap"],
            row["stages"][wanted[-1]]["first"][0],
            row["name"],
        )
    )

    return progression
