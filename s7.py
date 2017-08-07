# *-*coding:utf-8*-*
import requests


def check_iata(iata):
    print 'Checking iata START'
    url_check_iata = 'https://service.s7airlines.com/hermes/location/iata/' + iata# + ';lang=ru'
    response_checking_iata = requests.get(url_check_iata)
    result = response_checking_iata.json()
    if 'c' in result:
        return result['c']['code'], result['c']['iataCode']


def requests_s7(code_depart, iata_depart, code_dest, iata_dest):
    url_start = 'https://travelwith.s7.ru/processFlightsSearch.action'
    data_start = {
        'model.page': 'FLIGHTS_SEARCH_PAGE',
        'model.routeType': 'ROUND_TRIP', # ROUND_TRIP, ONE_WAY
        'model.departurePoint': code_depart,
        'model.departureIATAPoint': iata_depart,
        'model.arrivalPoint': code_dest,
        'model.arrivalIATAPoint': iata_dest,
        'model.departureDate': date_depart,
        'model.arrivalDate': date_return,
        'model.adultsCount': '1',
        'model.childrenCount': '0',
        'model.infantsCount': '0',
        'model.promoCode': '',
        '__checkbox_model.s7FlightsOnly': 'true',
        '__checkbox_model.directFlightsOnly': 'true',
        'model.milesEnabled': 'true',
        '__checkbox_model.redemption': 'true',
        'model.currencyType': 'RUB',
        'ibe_conversation_flow_type': 'FLIGHTS',
        'ibe_conversation': '',
    }
    headers_start = {
        'Host': 'travelwith.s7.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    session = requests.Session()
    response = session.post(url_start, headers=headers_start, data=data_start, verify=False)
    return response


iata_departure = 'DME'
iata_destination = 'LED'
date_depart = '30.11.2017'
date_return = '26.12.2017'

code_depart, iata_depart = check_iata(iata_departure)
code_dest, iata_dest = check_iata(iata_destination)

response_s7 = requests_s7(code_depart, iata_depart, code_dest, iata_dest)
with open('s7.html', 'w') as ouf:
    ouf.write(response_s7.content)

# HTTP/1.1 302 Found
# Server: QRATOR
# Date: Fri, 04 Aug 2017 08:56:55 GMT
# Content-Length: 0
# Connection: keep-alive
# Keep-Alive: timeout=15
# Set-Cookie: iberecs="{\"recentSearches\":[{\"type\":\"flightsRecentSearch\",\"rt\":\"ONE_WAY\",\"flexible\":false,\"dp\":\"AIR_GOJ_RU\",\"ap\":\"CITY_BNE_QL_AU\",\"ddasds\":[1520456400000],\"adasd\":null,\"ac\":1,\"cc\":0,\"ic\":0,\"sc\":null,\"rdmptn\":false,\"ct\":\"RUB\",\"s7Only\":false,\"directOnly\":false,\"pc\":\"\",\"dlic\":[\"GOJ\"],\"alic\":[\"BNE\"]},{\"type\":\"flightsRecentSearch\",\"rt\":\"ROUND_TRIP\",\"flexible\":false,\"dp\":\"CITY_MOW_RU\",\"ap\":\"CITY_BNE_QL_AU\",\"ddasds\":[1520456400000],\"adasd\":1520456400000,\"ac\":1,\"cc\":0,\"ic\":0,\"sc\":\"ANY\",\"rdmptn\":false,\"ct\":\"RUB\",\"s7Only\":false,\"directOnly\":false,\"pc\":null,\"dlic\":[\"MOW\"],\"alic\":[\"BNE\"]}]}"; Version=1; Domain=.s7.ru; Max-Age=31536000; Expires=Sat, 04-Aug-2018 08:56:48 GMT; Path=/; Secure
# Location: http://travelwith.s7.ru/selectExactDateSearchFlights.action?ibe_conversation_flow_type=FLIGHTS&ibe_conversation=4XUU3GLNDYSNQGOVLEUGXZGQXGZCCMNG
# Content-Language: ru-RU
# Cache-Control: no-store, no-cache, must-revalidate
# Strict-Transport-Security: max-age=31536000; includeSubDomains



