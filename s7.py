# *-*coding:utf-8*-*
import requests
import re
from collections import namedtuple
from datetime import datetime, date, timedelta


def requests_s7(port_depart, port_destin, date_depart, date_return):
    url_start = 'https://travelwith.s7.ru/processFlightsSearch.action'
    data_start = {
        'model.page': 'FLIGHTS_SEARCH_PAGE',
        'model.routeType': 'ROUND_TRIP',  # ROUND_TRIP, ONE_WAY
        'model.departurePoint': port_depart.code,
        'model.departureIATAPoint': port_depart.iata,
        'model.arrivalPoint': port_destin.code,
        'model.arrivalIATAPoint': port_destin.iata,
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
    response = session.post(
        url_start,
        headers=headers_start,
        data=data_start,
        verify=False
    )
    return response


class DataAirport(namedtuple('DataAirport', ['iata', 'code'])):
    def __new__(cls, iata):
        return super(DataAirport, cls).__new__(cls, iata, get_inner_code(iata))


def get_inner_code(iata):
    if not re.match('^[A-Z]{3}$', iata):
        return
    url_check_iata = 'https://service.s7airlines.com/hermes/location/iata/' + iata
    response_checking_iata = requests.get(url_check_iata)
    result = response_checking_iata.json()
    if 'c' in result:
        return result['c']['code']


def date_validation(date_depart, date_return=None):
    today = date.today()
    try:
        dtime_depart = datetime.strptime(date_depart, '%d.%m.%Y').date()
        dtime_return = datetime.strptime(date_return, '%d.%m.%Y').date()
    except ValueError:
        print 'Error. Date is not correct.(dd.mm.yyyy)'
        return
    if dtime_depart < today:
        print 'Error. Departure date in past.'
        return
    if date_return:
        if dtime_return < today:
            print 'Error. Return date in past.'
            return
    if dtime_return > today + timedelta(365):
        print 'Error. Change the date of return.'
        return
    if dtime_depart > dtime_return:
        print 'Error. Departure date is longer than the return date.'
        return
    return True


def main():
    iata_depart = 'DME'
    iata_destin = 'LED'
    date_depart = '15.11.2017'
    date_return = '10.08.2018'
    if not date_validation(date_depart, date_return):
        return

    port_depart = DataAirport(iata_depart)
    port_destin = DataAirport(iata_destin)

    if not port_depart.code or not port_destin.code:
        print 'Error. IATA-code is not correct.'
        return
    if port_depart.code == port_destin.code:
        print 'Error. IATA-departure is the same as IATA-arrival.'
        return

    response_s7_html = requests_s7(
        port_depart,
        port_destin,
        date_depart,
        date_return
    )
    
    with open('s7.html', 'w') as ouf:
        ouf.write(response_s7_html.content)


main()
