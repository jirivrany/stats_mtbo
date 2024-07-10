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
            model.get_competitor_place_count(competitor_id, place, event.upper(), table)
            for place in range(1, 4)
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
    gold_rank = reversed(
        [y[1] for y in sorted([(converted[x], x) for x in converted.keys()])]
    )

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
