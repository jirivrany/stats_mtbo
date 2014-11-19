from datetime import date

IOC_INDEX = {'LIE': 'LI', 'EGY': 'EG', 'LIB': 'LB', 'QAT': 'QA', 'SOM': 'SO', 'BOT': 'BW', 'PAR': 'PY', 'NAM': 'NA', 'FIJ': 'FJ', 'BOL': 'BO', 'GHA': 'GH', 'PAK': 'PK', 'SIN': 'SG', 'CPV': 'CV', 'JOR': 'JO', 'LBR': 'LR', 'SAM': 'WS', 'PUR': 'PR', 'POL': 'PL', 'PRK': 'KP', 'LBA': 'LY', 'LUX': 'LU', 'MYA': 'MM', 'ETH': 'ET', 'UAE': 'AE', 'HKG': 'HK', 'CHA': 'TD', 'TPE': 'TW', 'VAN': 'VU', 'SVK': 'SK', 'CHI': 'CL', 'PHI': 'PH', 'CHN': 'CN', 'SMR': 'SM', 'URU': 'UY', 'JAM': 'JM', 'MRI': 'MU', 'DJI': 'DJ', 'ZIM': 'ZW', 'FIN': 'FI', 'THA': 'TH', 'MAS': 'MY', 'LAO': 'LA', 'YEM': 'YE', 'MAW': 'MW', 'VIE': 'VN', 'KIR': 'KI', 'VIN': 'VC', 'AHO': 'AN', 'ROU': 'RO', 'SYR': 'SY', 'MAD': 'MG', 'LAT': 'LV', 'KAZ': 'KZ', 'TUR': 'TR', 'SUR': 'SR', 'DMA': 'DM', 'GUA': 'GT', 'BEN': 'BJ', 'BEL': 'BE', 'TOG': 'TG', 'GUI': 'GN', 'GUM': 'GU', 'NIG': 'NE', 'CRC': 'CR', 'KSA': 'SA', 'GBS': 'GW', 'DEN': 'DK', 'BER': 'BM', 'GUY': 'GY', 'SKN': 'KN', 'CMR': 'CM', 'GER': 'DE', 'GEQ': 'GQ', 'MAR': 'MA', 'BUR': 'BF', 'HUN': 'HU', 'TKM': 'TM', 'PAN': 'PA', 'BUL': 'BG', 'GEO': 'GE', 'MNE': 'ME', 'TRI': 'TT', 'MHL': 'MH', 'AFG': 'AF', 'BDI': 'BI', 'BLR': 'BY', 'GRE': 'GR', 'GRN': 'GD', 'AND': 'AD', 'MOZ': 'MZ', 'ANG': 'AO', 'IVB': 'VG', 'TJK': 'TJ', 'MGL': 'MN', 'ANT': 'AG', 'MON': 'MC', 'LCA': 'LC', 'IND': 'IN', 'MTN': 'MR', 'INA': 'ID', 'NOR': 'NO', 'CZE': 'CZ',
             'SUD': 'SD', 'MLT': 'MT', 'DOM': 'DO', 'KUW': 'KW', 'ISR': 'IL', 'NED': 'NL', 'FSM': 'FM', 'PER': 'PE', 'COD': 'CD', 'ISL': 'IS', 'COK': 'CK', 'COM': 'KM', 'COL': 'CO', 'NEP': 'NP', 'CGO': 'CG', 'MDA': 'MD', 'STP': 'ST', 'ASA': 'AS', 'SEY': 'SC', 'ECU': 'EC', 'SEN': 'SN', 'MDV': 'MV', 'SRB': 'RS', 'FRA': 'FR', 'ZAM': 'ZM', 'LTU': 'LT', 'RWA': 'RW', 'SRI': 'LK', 'FRO': 'FO', 'UKR': 'UA', 'CRO': 'HR', 'AUS': 'AU', 'GBR': 'GB', 'AUT': 'AT', 'VEN': 'VE', 'TAN': 'TZ', 'PLW': 'PW', 'KEN': 'KE', 'OMA': 'OM', 'ALG': 'DZ', 'BRU': 'BN', 'ALB': 'AL', 'TUV': 'TV', 'ITA': 'IT', 'BRN': 'BH', 'PLE': 'PS', 'LES': 'LS', 'TUN': 'TN', 'RUS': 'RU', 'MEX': 'MX', 'BRA': 'BR', 'CIV': 'CI', 'TLS': 'TL', 'CAY': 'KY', 'MKD': 'MK', 'BAR': 'BB', 'NGR': 'NG', 'USA': 'US', 'HAI': 'HT', 'SWE': 'SE', 'AZE': 'AZ', 'SWZ': 'SZ', 'CAN': 'CA', 'CAM': 'KH', 'BAN': 'BD', 'KOR': 'KR', 'CAF': 'CF', 'BAH': 'BS', 'CYP': 'CY', 'BIH': 'BA', 'POR': 'PT', 'SOL': 'SB', 'UZB': 'UZ', 'ERI': 'ER', 'GAM': 'GM', 'TGA': 'TO', 'BIZ': 'BZ', 'GAB': 'GA', 'EST': 'EE', 'ESP': 'ES', 'HON': 'HN', 'IRQ': 'IQ', 'MLI': 'ML', 'IRI': 'IR', 'SLO': 'SI', 'IRL': 'IE', 'ESA': 'SV', 'SSD': 'SS', 'SLE': 'SL', 'NZL': 'NZ', 'SUI': 'CH', 'ISV': 'VI', 'ARU': 'AW', 'JPN': 'JP', 'KGZ': 'KG', 'RSA': 'ZA', 'UGA': 'UG', 'PNG': 'PG', 'ARG': 'AR', 'NCA': 'NI', 'BHU': 'BT', 'ARM': 'AM', 'NRU': 'NR', 'CUB': 'CU'}

def years():
    """
    prepare list of years from 2002 till now
    exclude 2003
    """

    years = [2002,]
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
