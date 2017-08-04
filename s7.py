# *-*coding:utf-8*-*
import requests
str_iata = 'dme'
#url_checking_iata = 'https://www.s7.ru/app/LocationService?action=get_locations&searchType=avia&str=' + str_iata + '&lang=ru'
# # json {
#     stc : 200
#     std : 'Requests succcees'
#     c: [{},]

url_checking_iata = 'https://service.s7airlines.com/hermes/location/iata/GOJ;lang=ru'
# json
# stc: 200
# std: Запрос выполнен успешно


session = requests.Session()
response_checking_iata = session.get(url_checking_iata)
# print response.json()

# for key, val in response_checking_iata.json().items():
#     print key, val

url_start = 'https://travelwith.s7.ru/processFlightsSearch.action'
data_start = {
    'model.page': 'FLIGHTS_SEARCH_PAGE',
    'model.routeType': 'ONE_WAY',
    'model.departurePoint': 'AIR_DME_RU',
    'model.departureIATAPoint': 'dme',
    'model.arrivalPoint': 'CITY_BNE_QL_AU',
    'model.arrivalIATAPoint': 'BNE',
    'model.departureDate': '08.03.2018',
    'model.arrivalDate': '' ,
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
response = session.post(url_start, headers=headers_start, data=data_start, verify=False)

with open('s7.html', 'w') as ouf:
    ouf.write(response.content)
 
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



