# *-*coding:utf-8*-*
import requests
str_iata = 'dme'
url_iata_out = 'https://www.s7.ru/app/LocationService?action=get_locations&searchType=avia&str=' + str_iata + '&lang=ru'
# # json {
#     stc : 200
#     std : 'Requests succcees'

session = requests.Session()
response_iata = session.get(url_iata_out)
# print response.json()
# 
for key, val in response_iata.json().items():
    print key, val
