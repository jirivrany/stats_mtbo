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

EVENT_NAMES = {
    "WMTBOC": "World MTBO championship",
    "EMTBOC": "European MTBO championship",
    "WCUP": "MTBO World Cup",
}


def prepare_relay_output(source_list):
    output = defaultdict(list)
    for wom in source_list:
        output[wom[5]].append(wom)

    wmn = {key: sorted(wom, key=lambda x: x[4]) for key, wom in output.items()}

    output = {}
    for ioc_code, team in wmn.items():
        country = team[0][5].upper()
        output[ioc_code] = {
            "place": team[0][2],
            "country": country,
            "flag": IOC_INDEX[country].lower(),
            "time": team[0][3],
            "members": [(x[0], x[4]) for x in team],
        }

    return output


def prepare_medal_table(model, competitor_id, table="race"):
    if table == "relay":
        mkeys = ["WMTBOC", "EMTBOC", "WCUP"]
    else:
        mkeys = ["WMTBOC", "EMTBOC", "WCUP"]

    medal_table = dict.fromkeys(mkeys, [])
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
    career_best = {
        "WMTBOC": {"individual": {}, "relay": {}},
        "EMTBOC": {"individual": {}, "relay": {}},
        "WCUP": {"individual": {}, "relay": {}},
    }

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
    career_best = {
        "WMTBOC": {"individual": {}, "relay": {}},
        "EMTBOC": {"individual": {}, "relay": {}},
        "WCUP": {"individual": {}, "relay": {}},
    }

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
    # Define all possible distances
    WMTBOC_DISTANCES = ["sprint", "middle", "long", "mass_start", "relay"]
    ALL_DISTANCES = ["relay", "mix_relay", "sprint_relay", "sprint", "middle", "long", "mass_start"]

    distance_mapping = {"WMTBOC": WMTBOC_DISTANCES, "EMTBOC": ALL_DISTANCES, "WCUP": ALL_DISTANCES}

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
    for distance in distance_mapping.get(event, []):
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
