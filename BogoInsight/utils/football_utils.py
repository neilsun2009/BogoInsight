NATION_CODE_MAP = {
    # Europe
    'England': 'gb-eng',
    'Scotland': 'gb-sct',
    'Wales': 'gb-wls',
    'Northern Ireland': 'gb-nir',
    'Germany': 'de',
    'Spain': 'es',
    'Italy': 'it',
    'France': 'fr',
    'Portugal': 'pt',
    'Netherlands': 'nl',
    'Belgium': 'be',
    'Russia': 'ru',
    'Turkey': 'tr',
    'Ukraine': 'ua',
    'Austria': 'at',
    'Denmark': 'dk',
    'Switzerland': 'ch',
    'Greece': 'gr',
    'Sweden': 'se',
    'Czech Republic': 'cz',
    'Croatia': 'hr',
    'Serbia': 'rs',
    'Poland': 'pl',
    'Hungary': 'hu',
    'Iceland': 'is',
    'Slovakia': 'sk',
    'Romania': 'ro',
    'Bulgaria': 'bg',
    'Slovenia': 'si',
    'Republic of Ireland': 'ie',
    'Norway': 'no',
    'FR Yugoslavia': 'yu',
    # Americas
    'Brazil': 'br',
    'Argentina': 'ar',
    'Uruguay': 'uy',
    'Paraguay': 'py',
    'Chile': 'cl',
    'Colombia': 'co',
    'Ecuador': 'ec',
    'Mexico': 'mx',
    'United States': 'us',
    'Costa Rica': 'cr',
    # Asia
    'China': 'cn',
    'Japan': 'jp',
    'South Korea': 'kr',
    'Australia': 'au',
    'Iran': 'ir',
    'Saudi Arabia': 'sa',
    # Africa
    'Nigeria': 'ng',
    'Cameroon': 'cm',
    'Ghana': 'gh',
    'Ivory Coast': 'ci',
    'Egypt': 'eg',
    'Morocco': 'ma',
    'Senegal': 'sn',
    'Algeria': 'dz',
}

def get_nation_flag_html(nation):
    if nation not in NATION_CODE_MAP:
        url = 'https://hatscripts.github.io/circle-flags/flags/xx.svg'
    elif nation == 'FR Yugoslavia':
        url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Civil_ensign_of_Serbia_and_Montenegro.svg/320px-Civil_ensign_of_Serbia_and_Montenegro.svg.png'
    elif nation in ['Spain']:
        url = f'https://flagicons.lipis.dev/flags/4x3/{NATION_CODE_MAP[nation]}.svg'
    else:
        url = f'https://flagicons.lipis.dev/flags/1x1/{NATION_CODE_MAP[nation]}.svg'
    return f'''
    <div style="width: 50px; height: 50px; border-radius: 100%; overflow: hidden; display: inline-block; margin: 2px; box-shadow: inset 0 0 0 2px rgba(0, 0, 0, .18);">
        <img src="{url}" alt="{nation}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;" />
    </div>
    '''