# *-*coding:utf-8*-*
import requests
import re
from collections import namedtuple
from datetime import datetime, date, timedelta
from lxml import html


def requests_s7(port_depart, port_destin, date_depart, date_return):
    url_start = 'https://travelwith.s7.ru/processFlightsSearch.action'
    route_type = 'ROUND_TRIP' if date_return else 'ONE_WAY'
    data_start = {
        'model.page': 'FLIGHTS_SEARCH_PAGE',
        'model.routeType': route_type,
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
        if dtime_depart < today:
            print 'Error. Departure date in past.'
            return
        elif dtime_depart > today + timedelta(360):
            print 'Error. Change the date of departure.'
            return
        if date_return:
            dtime_return = datetime.strptime(date_return, '%d.%m.%Y').date()
            if dtime_return < today:
                print 'Error. Return date in past.'
                return
            elif dtime_return > today + timedelta(360):
                print 'Error. Change the date of return.'
                return
            elif dtime_depart > dtime_return:
                print 'Error. Departure date is longer than the return date.'
                return
    except ValueError:
        print 'Error. Date is not correct.(dd.mm.yyyy)'
        return
    return True


def check_iata_code(port_depart, port_destin):
    if not port_depart.code or not port_destin.code:
        print 'Error. IATA-code is not correct.'
        return
    if port_depart.code == port_destin.code:
        print 'Error. IATA-departure is the same as IATA-arrival.'
        return
    return True


def parser(direction, page):
    types_tariff = [
        'basiceconomy',
        'flexeconomy',
        'basicbusiness',
        'flexbusiness'
    ]
    result_price = []
    tree = html.fromstring(page)
    table = tree.xpath('.//*[@id="{}"]/div[2]/*'.format(direction))
    for row in table:
        time_depart = row.xpath(
            './/*[@data-qa="timeDeparture_flightItem"]/text()')[0]
        time_arriv = row.xpath(
            './/*[@data-qa="timeArrived_flightItem"]/text()')[0]
        duration = row.xpath(
            './/*[@data-qa="durationTotal_flightItemShort"]/text()')[0]
        for num, tariff in enumerate(types_tariff):
            price = row.xpath(
                './/*[@data-tariff-type="' +
                tariff +
                '"]//*[@data-qa="amount"]/text()'
            )
            if price:
                result_price.append([
                    time_depart,
                    time_arriv,
                    duration,
                    tariff,
                    price[0]
                ])
    return result_price


def main():
    iata_depart = 'DME'
    iata_destin = 'LED'
    date_depart = '30.11.2017'
    date_return = '26.12.2017'
    if not date_validation(date_depart, date_return):
        return
    port_depart = DataAirport(iata_depart)
    port_destin = DataAirport(iata_destin)
    if not check_iata_code(port_depart, port_destin):
        return
    response_html = requests_s7(
        port_depart,
        port_destin,
        date_depart,
        date_return
    )
    price_outbound = parser(
        'exact_outbound_flight_table',
        response_html.content
    )
    price_return = parser(
        'exact_inbound_flight_table',
        response_html.content
    )
    for elem in price_outbound:
            print elem

    # with open('s7.html', 'w') as ouf:
    #     ouf.write(response_html.content)
main()
