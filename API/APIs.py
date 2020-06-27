from wordnik import swagger, WordApi, WordsApi
import json
import urllib.error
import bs4
import datetime
import requests
import random
import urllib
from urllib.request import urlopen
import urllib.request

def picture_of_the_day():
    session = requests.Session()
    endpoint = 'https://en.wikipedia.org/w/api.php'

    date = datetime.datetime.today().strftime('%Y-%m-%d')
    title = 'Template:POTD_protected/' + date

    params = {
        'action': 'query',
        'format': 'json',
        'formatversion': '2',
        'prop': 'images',
        'titles': title
    }
    res = session.get(url=endpoint, params=params).json()
    filename = res['query']['pages'][0]['images'][0]['title']
    image_url = 'https://en.wikipedia.org/wiki/' + title
    image_data = {
        'title': filename,
        'image_page_url': image_url,

    }

    return [image_data['title'][5:-4], image_data['image_page_url']]

def art_of_the_day():
    with requests.request('GET', 'https://collectionapi.metmuseum.org/public/collection/v1/objects') as met_link:
        lb = json.loads(met_link.text.encode('utf8'))
        obj_ids = lb['objectIDs']
        index = random.randrange(0, len(obj_ids))
        while True:
            '''
            with requests.request('GET',
                                  'https://collectionapi.metmuseum.org/public/collection/v1/objects/679500') as art:
                                  '''
            with requests.request('GET',
            'https://collectionapi.metmuseum.org/public/collection/v1/objects/{0}'.format(obj_ids[index])) as art:

                img = json.loads(art.text.encode('utf8'))

                if img['primaryImage']:
                    pic_response = requests.get(img['primaryImageSmall'])
                    pic = pic_response.content
                    print(pic)
                    print(type(pic))
                    if img['artistDisplayName']:
                        artist = img['artistDisplayName']
                    else:
                        artist = 'Unknown Artist'
                    bio = img['artistDisplayBio']
                    if img['objectURL']:
                        more_info = img['objectURL']
                    else:
                        more_info = None
                    if img['title']:
                        title = img['title']
                    else:
                        title = 'Untitled'
                    break
                else:
                    index = random.randrange(0, len(obj_ids))

        return pic, artist, bio, more_info, title


class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

def make_dict():
    # this is just used to get a dictionary of country names matched with their country/flag codes
    # keeping it just in case something happens to the flag dict.
    page = requests.get('https://www.countryflags.io/')
    flag_soup = bs4.BeautifulSoup(page.text, features="html.parser")
    pElems = flag_soup.select('div > p')
    flag_dict = {}
    for i in range(0, (len(pElems)-3)//2):
        flag_dict[pElems[(i*2)+1].getText()] = pElems[i*2].getText()
    print(flag_dict)

def make_countries():
    # same but gets the name of the countries.  if re running either make_ function, remember to chop off some trailing
    # html stuff thats not country info.
    page = requests.get('https://www.countryflags.io/')
    flag_soup = bs4.BeautifulSoup(page.text, features="html.parser")
    pElems = flag_soup.select('div > p')
    countries = []
    for i in range(0, (len(pElems) - 3) // 2):
        country = pElems[(i * 2) + 1].getText()
        if country:
            countries.append(pElems[(i * 2) + 1].getText())
    print(countries)

flag_dict = {'Andorra': 'AD', 'United Arab Emirates': 'AE', 'Afghanistan': 'AF', 'Antigua and Barbuda': 'AG',
             'Anguilla': 'AI', 'Albania': 'AL', 'Armenia': 'AM', 'Netherlands Antilles': 'AN', 'Angola': 'AO',
             'Antarctica': 'AQ', 'Argentina': 'AR', 'American Samoa': 'AS', 'Austria': 'AT', 'Australia': 'AU',
             'Aruba': 'AW', 'Åland Islands': 'AX', 'Azerbaijan': 'AZ', 'Bosnia and Herzegovina': 'BA', 'Barbados': 'BB',
             'Bangladesh': 'BD', 'Belgium': 'BE', 'Burkina Faso': 'BF', 'Bulgaria': 'BG', 'Bahrain': 'BH',
             'Burundi': 'BI', 'Benin': 'BJ', 'Saint Barthélemy': 'BL', 'Bermuda': 'BM', 'Brunei Darussalam': 'BN',
             'Bolivia': 'BO', 'Bonaire, Sint Eustatius and Saba': 'BQ', 'Brazil': 'BR', 'Bahamas': 'BS', 'Bhutan': 'BT',
             'Bouvet Island': 'BV', 'Botswana': 'BW', 'Belarus': 'BY', 'Belize': 'BZ', 'Canada':
                 'CA', 'Cocos (Keeling) Islands': 'CC', 'Congo, The Democratic Republic Of The': 'CD',
             'Central African Republic': 'CF', 'Congo': 'CG', 'Switzerland': 'CH', "Côte D'Ivoire": 'CI',
             'Cook Islands': 'CK', 'Chile': 'CL', 'Cameroon': 'CM', 'China': 'CN', 'Colombia': 'CO', 'Costa Rica': 'CR',
             'Cuba': 'CU', 'Cape Verde': 'CV', 'Curaçao': 'CW', 'Christmas Island': 'CX', 'Cyprus': 'CY',
             'Czech Republic': 'CZ', 'Germany': 'DE', 'Djibouti': 'DJ', 'Denmark': 'DK', 'Dominica': 'DM',
             'Dominican Republic': 'DO', 'Algeria': 'DZ', 'Ecuador': 'EC', 'Estonia': 'EE', 'Egypt': 'EG',
             'Western Sahara': 'EH', 'Eritrea': 'ER', 'Spain': 'ES', 'Ethiopia': 'ET', 'Finland': 'FI', 'Fiji': 'FJ',
             'Falkland Islands (Malvinas)': 'FK', 'Micronesia, Federated States Of': 'FM', 'Faroe Islands': 'FO',
             'France': 'FR', 'Gabon': 'GA', 'United Kingdom': 'GB', 'Grenada': 'GD', 'Georgia': 'GE', 'French Guiana':
                 'GF', 'Guernsey': 'GG', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Greenland': 'GL', 'Gambia': 'GM', 'Guinea':
                 'GN', 'Guadeloupe': 'GP', 'Equatorial Guinea': 'GQ', 'Greece': 'GR',
             'South Georgia and the South Sandwich Islands': 'GS', 'Guatemala': 'GT', 'Guam': 'GU', 'Guinea-Bissau':
                 'GW', 'Guyana': 'GY', 'Hong Kong': 'HK', 'Heard and McDonald Islands': 'HM', 'Honduras': 'HN',
             'Croatia': 'HR', 'Haiti': 'HT', 'Hungary': 'HU', 'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL',
             'Isle of Man': 'IM', 'India': 'IN', 'British Indian Ocean Territory': 'IO', 'Iraq': 'IQ',
             'Iran, Islamic Republic Of': 'IR', 'Iceland': 'IS', 'Italy': 'IT', 'Jersey': 'JE', 'Jamaica': 'JM',
             'Jordan': 'JO', 'Japan': 'JP', 'Kenya': 'KE', 'Kyrgyzstan': 'KG', 'Cambodia': 'KH', 'Kiribati': 'KI',
             'Comoros': 'KM', 'Saint Kitts And Nevis': 'KN', "Korea, Democratic People's Republic Of": 'KP',
             'Korea, Republic of': 'KR', 'Kuwait': 'KW', 'Cayman Islands': 'KY', 'Kazakhstan': 'KZ',
             "Lao People's Democratic Republic": 'LA', 'Lebanon': 'LB', 'Saint Lucia': 'LC', 'Liechtenstein': 'LI',
             'Sri Lanka': 'LK', 'Liberia': 'LR', 'Lesotho': 'LS', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV',
             'Libya': 'LY', 'Morocco': 'MA', 'Monaco': 'MC', 'Moldova, Republic of': 'MD', 'Montenegro': 'ME',
             'Saint Martin': 'MF', 'Madagascar': 'MG', 'Marshall Islands': 'MH',
             'Macedonia, the Former Yugoslav Republic Of': 'MK', 'Mali': 'ML', 'Myanmar': 'MM', 'Mongolia': 'MN',
             'Macao': 'MO', 'Northern Mariana Islands': 'MP', 'Martinique': 'MQ', 'Mauritania': 'MR', 'Montserrat':
                 'MS', 'Malta': 'MT', 'Mauritius': 'MU', 'Maldives': 'MV', 'Malawi': 'MW', 'Mexico': 'MX', 'Malaysia':
                 'MY', 'Mozambique': 'MZ', 'Namibia': 'NA', 'New Caledonia': 'NC', 'Niger': 'NE', 'Norfolk Island':
                 'NF', 'Nigeria': 'NG', 'Nicaragua': 'NI', 'Netherlands': 'NL', 'Norway': 'NO', 'Nepal': 'NP', 'Nauru':
                 'NR', 'Niue': 'NU', 'New Zealand': 'NZ', 'Oman': 'OM', 'Panama': 'PA', 'Peru': 'PE',
             'French Polynesia': 'PF', 'Papua New Guinea': 'PG', 'Philippines': 'PH', 'Pakistan': 'PK', 'Poland': 'PL',
             'Saint Pierre And Miquelon': 'PM', 'Pitcairn': 'PN', 'Puerto Rico': 'PR', 'Palestine, State of': 'PS',
             'Portugal': 'PT', 'Palau': 'PW', 'Paraguay': 'PY', 'Qatar': 'QA', 'Réunion': 'RE', 'Romania': 'RO',
             'Serbia': 'RS', 'Russian Federation': 'RU', 'Rwanda': 'RW', 'Saudi Arabia': 'SA', 'Solomon Islands': 'SB',
             'Seychelles': 'SC', 'Sudan': 'SD', 'Sweden': 'SE', 'Singapore': 'SG', 'Saint Helena': 'SH', 'Slovenia':
                 'SI', 'Svalbard And Jan Mayen': 'SJ', 'Slovakia': 'SK', 'Sierra Leone': 'SL', 'San Marino': 'SM',
             'Senegal': 'SN', 'Somalia': 'SO', 'Suriname': 'SR', 'South Sudan': 'SS', 'Sao Tome and Principe': 'ST',
             'El Salvador': 'SV', 'Sint Maarten': 'SX', 'Syrian Arab Republic': 'SY', 'Swaziland': 'SZ',
             'Turks and Caicos Islands': 'TC', 'Chad': 'TD', 'French Southern Territories': 'TF', 'Togo': 'TG',
             'Thailand': 'TH', 'Tajikistan': 'TJ', 'Tokelau': 'TK', 'Timor-Leste': 'TL', 'Turkmenistan': 'TM',
             'Tunisia': 'TN', 'Tonga': 'TO', 'Turkey': 'TR', 'Trinidad and Tobago': 'TT', 'Tuvalu': 'TV',
             'Taiwan, Republic Of China': 'TW', 'Tanzania, United Republic of': 'TZ', 'Ukraine': 'UA', 'Uganda': 'UG',
             'United States Minor Outlying Islands': 'UM', 'United States': 'US', 'Uruguay': 'UY', 'Uzbekistan': 'UZ',
             'Holy See (Vatican City State)': 'VA', 'Saint Vincent And The Grenadines': 'VC',
             'Venezuela, Bolivarian Republic of': 'VE', 'Virgin Islands, British': 'VG', 'Virgin Islands, U.S.': 'VI',
             'Vietnam': 'VN', 'Vanuatu': 'VU', 'Wallis and Futuna': 'WF', 'Samoa': 'WS', 'Yemen': 'YE', 'Mayotte': 'YT',
             'South Africa': 'ZA', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'}
countries = ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Anguilla', 'Albania', 'Armenia',
             'Netherlands Antilles', 'Angola', 'Antarctica', 'Argentina', 'American Samoa', 'Austria', 'Australia',
             'Aruba', 'Åland Islands', 'Azerbaijan', 'Bosnia and Herzegovina', 'Barbados', 'Bangladesh', 'Belgium',
             'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin', 'Saint Barthélemy', 'Bermuda',
             'Brunei Darussalam', 'Bolivia', 'Bonaire, Sint Eustatius and Saba', 'Brazil', 'Bahamas', 'Bhutan',
             'Bouvet Island', 'Botswana', 'Belarus', 'Belize', 'Canada', 'Cocos (Keeling) Islands',
             'Congo, The Democratic Republic Of The', 'Central African Republic', 'Congo', 'Switzerland',
             "Côte D'Ivoire", 'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba',
             'Cape Verde', 'Curaçao', 'Christmas Island', 'Cyprus', 'Czech Republic', 'Germany', 'Djibouti', 'Denmark',
             'Dominica', 'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea',
             'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'Micronesia, Federated States Of',
             'Faroe Islands', 'France', 'Gabon', 'United Kingdom', 'Grenada', 'Georgia', 'French Guiana', 'Guernsey',
             'Ghana', 'Gibraltar', 'Greenland', 'Gambia', 'Guinea', 'Guadeloupe', 'Equatorial Guinea', 'Greece',
             'South Georgia and the South Sandwich Islands', 'Guatemala', 'Guam', 'Guinea-Bissau', 'Guyana', 'Hong Kong'
             ,'Heard and McDonald Islands', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel',
             'Isle of Man', 'India', 'British Indian Ocean Territory', 'Iraq', 'Iran, Islamic Republic Of', 'Iceland',
             'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros',
             'Saint Kitts And Nevis', "Korea, Democratic People's Republic Of", 'Korea, Republic of', 'Kuwait',
             'Cayman Islands', 'Kazakhstan', "Lao People's Democratic Republic", 'Lebanon', 'Saint Lucia',
             'Liechtenstein', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco'
             , 'Monaco', 'Moldova, Republic of', 'Montenegro', 'Saint Martin', 'Madagascar', 'Marshall Islands',
             'Macedonia, the Former Yugoslav Republic Of', 'Mali', 'Myanmar', 'Mongolia', 'Macao',
             'Northern Mariana Islands', 'Martinique', 'Mauritania', 'Montserrat', 'Malta', 'Mauritius', 'Maldives',
             'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Norfolk Island',
             'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue', 'New Zealand', 'Oman', 'Panama',
             'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines', 'Pakistan', 'Poland',
             'Saint Pierre And Miquelon', 'Pitcairn', 'Puerto Rico', 'Palestine, State of', 'Portugal', 'Palau',
             'Paraguay', 'Qatar', 'Réunion', 'Romania', 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia',
             'Solomon Islands', 'Seychelles', 'Sudan', 'Sweden', 'Singapore', 'Saint Helena', 'Slovenia',
             'Svalbard And Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal', 'Somalia', 'Suriname',
             'South Sudan', 'Sao Tome and Principe', 'El Salvador', 'Sint Maarten', 'Syrian Arab Republic', 'Swaziland',
             'Turks and Caicos Islands', 'Chad', 'French Southern Territories', 'Togo', 'Thailand', 'Tajikistan',
             'Tokelau', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Tonga', 'Turkey', 'Trinidad and Tobago', 'Tuvalu',
             'Taiwan, Republic Of China', 'Tanzania, United Republic of', 'Ukraine', 'Uganda',
             'United States Minor Outlying Islands', 'United States', 'Uruguay', 'Uzbekistan',
             'Holy See (Vatican City State)', 'Saint Vincent And The Grenadines', 'Venezuela, Bolivarian Republic of',
             'Virgin Islands, British', 'Virgin Islands, U.S.', 'Vietnam', 'Vanuatu', 'Wallis and Futuna', 'Samoa',
             'Yemen', 'Mayotte', 'South Africa', 'Zambia', 'Zimbabwe']


def flag_of_the_day():
    country_index = random.randrange(0, len(countries))
    flag_code = flag_dict[countries[country_index]]
    opener = AppURLopener()
    flag_url = "https://www.countryflags.io/{0}/flat/64.png".format(flag_code)
    with opener.open(flag_url) as u:
        raw_data = u.read()
    img = raw_data
    other_countries = []
    while len(other_countries) < 3:
        cn = countries[random.randrange(0, len(countries))]
        if cn != countries[country_index]:
            other_countries.append(cn)

    return countries[country_index], img, other_countries


def word_of_the_day():
    apiUrl = 'http://api.wordnik.com/v4'
    apiKey = '***'
    client = swagger.ApiClient(apiKey, apiUrl)


    words_api = WordsApi.WordsApi(client)
    day_word = words_api.getWordOfTheDay()

    word_api = WordApi.WordApi(client)
    '''
    ugly but sometimes the word of the day wont have IPA pronunciation.  Probably I should figure out what type of
    pron it does have.
    '''
    try:
        pron = word_api.getTextPronunciations(day_word.word, typeFormat='IPA')
    except urllib.error.HTTPError:
        pron = ''

    # word of the day .definitions returns a list with a custom object (SimpleDefinitions) inside.
    # index 0 gets us that object, then we use .text to get the definition text.
    # pron.raw gives us the pronunciation as a string in IPA format per kwarg above.  Not sure what pron.raw[0] is,
    # but it isnt in IPA format, so I'm going to just use [1]

    if pron:
        return day_word.word, day_word.definitions[0].text, pron[0].raw # error is here b/c according to the try/except
                                                                        # block up there, pron is a string. because of
                                                                        # the if statement, tho, pron wont ever be a str
                                                                        # if we're at this point in the code.
    else:
        return day_word.word, day_word.definitions[0].text, pron
