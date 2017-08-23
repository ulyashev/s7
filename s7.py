"""
S7 airline scraper.

The module is designed to provide information on availability and cost
Tickets on the site s7.ru. The main function takes an input
of four parameters:
  - IATA code of outbound (required),
  - IATA code of inbound (required),
  - Date of departure (required),
  - Date of return (optional).

Produces the search for possible options for flying and displaying
information on the screen. Input format: IATA-code, consisting of
three Latin letters, date in the format (YYYY-MM-DD).
"""

from collections import namedtuple
from datetime import datetime, date, timedelta
from itertools import product
import re
import sys

from lxml import html
import requests


def make_request(port_depart, port_destin, date_depart, date_return):
    """Make a request."""
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


class Airport(namedtuple('Airport', ('iata', 'code'))):
    """
    Class for airport objects.

    Automatically gets S7 internal airport code on creation. It has attributes
    `iata` (with iata code) and `code` (with airport internal code).
    """

    def __new__(cls, iata):
        return super(Airport, cls).__new__(cls, iata, get_inner_code(iata))


def get_inner_code(iata):
    """Get S7 internal code from IATA airport code."""
    if not re.match('^[A-Z]{3}$', iata):
        return
    url_verif = 'https://service.s7airlines.com/hermes/location/iata/' + iata
    response_checking_iata = requests.get(url_verif)
    result = response_checking_iata.json()
    if 'c' in result:
        return result['c']['code']


def date_validation(date_depart, date_return=None):
    """Date validate."""
    today = date.today()
    try:
        dtime_depart = datetime.strptime(date_depart, '%d.%m.%Y').date()
        if dtime_depart < today:
            print 'Error. Departure date in past.'
            return
        elif dtime_depart > today + timedelta(365):
            print 'Error. Change the date of departure.'
            return
        if date_return:
            dtime_return = datetime.strptime(date_return, '%d.%m.%Y').date()
            if dtime_return < today:
                print 'Error. Return date in past.'
                return
            elif dtime_return > today + timedelta(365):
                print 'Error. Change the date of return.'
                return
            elif dtime_depart > dtime_return:
                print 'Error. Departure date is longer than the return date.'
                return
    except ValueError:
        print 'Error. Date is not correct.(dd.mm.yyyy)'
        return
    return True


def code_iata_validation(port_depart, port_destin):
    """Code IATA validate."""
    if not port_depart.code or not port_destin.code:
        print 'Error. IATA-code is not correct.'
        return
    if port_depart.code == port_destin.code:
        print 'Error. IATA-departure is the same as IATA-arrival.'
        return
    return True


def parser(direction, page):
    """Parsing and forming a price list."""
    price = []
    tree = html.fromstring(page)
    table = tree.xpath('.//*[@id="{}"]/div[2]/*'.format(direction))
    for row in table:
        time_depart = row.xpath(
            './/*[@data-qa="timeDeparture_flightItem"]/text()')
        time_arriv = row.xpath(
            './/*[@class="arrival-time"]/time/text()')
        duration = row.xpath(
            './/*[@data-qa="durationTotal_flightItemShort"]/text()')
        for column in row.xpath('./*[@class="select-item-simple"]/*'):
            tariff = column.xpath('@data-tariff-type')
            cost = column.xpath('.//*[@data-qa="amount"]/text()')
            if cost:
                price.append([
                    str(time_depart[0]),
                    str(time_arriv[0]),
                    'h'.join(duration[0].encode('ascii', 'ignore').split()),
                    str(tariff[0]),
                    int(cost[0].encode('ascii', 'ignore')),
                    list()
                ])
                for row_connect in row.xpath(
                        './/*[@class="select-item-full"]/*'):
                    time_depart_conn = row_connect.xpath(
                        './/*[@data-qa="timeDeparture_flightItem"]/text()')
                    port_depart_conn = row_connect.xpath(
                        './/*[@data-qa="airportDeparture_flightItem"]/text()')
                    time_arriv_conn = row_connect.xpath(
                        './/*[@data-qa="timeArrived_flightItem"]/text()')
                    port_arriv_conn = row_connect.xpath(
                        './/*[@data-qa="airportArrived_flightItem"]/text()')
                    if time_depart_conn:
                        price[-1][-1].append([
                            time_depart_conn[0],
                            port_depart_conn[0],
                            time_arriv_conn[0],
                            port_arriv_conn[0]
                        ])

    return price


def check_input_data(args):
    """Checking input data."""
    if len(args) == 5:
        return args[1:]
    elif len(args) == 4:
        return args[1:] + [None]
    else:
        print ('Error. You entered {} parameters, '
               'you must enter 3 or 4 parameters.').format(len(args[1:]))
        return


def print_flight(status_flight):
    """Printing a status flight."""
    if not status_flight:
        print 'Direct flight.', '\n'
    else:
        print 'Connecting flight:'
        for point in status_flight:
            print ', '.join(point)


def print_price(price, currency):
    """Printing a price."""
    print ('Departure-{}, arrival-{}, duration:{}, tariff:{},'
           ' price:{} ').format(*price) + currency


def information_output(price_depart, price_return, currency):
    """

    Print  of flight parameters.

    If there is a return route, consider the total cost of the flight.
    """

    if price_return:
        price_result = []
        for elem_dep, elem_ret in product(price_depart, price_return):
            price_result.append({
                'track_dep': elem_dep,
                'track_return': elem_ret,
                'total_sum': elem_dep[-2] + elem_ret[-2]
            })
        for elem_res in sorted(price_result, key=lambda x: x['total_sum']):
            print_price(elem_res['track_dep'], currency)
            print_flight(elem_res['track_dep'][-1])
            print_price(elem_res['track_return'], currency)
            print_flight(elem_res['track_return'][-1])
            print 'Total:', elem_res['total_sum'], currency, '\n'
    else:
        for elem_dep in sorted(price_depart, key=lambda x: x[-2]):
            print_price(elem_dep, currency)
            print_flight(elem_dep[-1])
            print '\n'


def main(sys_arg):
    input_data = check_input_data(sys_arg)
    if not input_data:
        return
    iata_depart, iata_destin, date_depart, date_return = input_data
    if not date_validation(date_depart, date_return):
        return
    port_depart = Airport(iata_depart)
    port_destin = Airport(iata_destin)
    if not code_iata_validation(port_depart, port_destin):
        return
    response_html = make_request(
        port_depart,
        port_destin,
        date_depart,
        date_return
    )
    price_depart = parser(
        'exact_outbound_flight_table',
        response_html.text
    )
    price_return = parser(
        'exact_inbound_flight_table',
        response_html.text
    )
    if not price_depart:
        print 'Unfortunately, we did not find any suitable flights for you. Try changing the search parameters.'
    else:
        page = html.fromstring(response_html.text)
        currency = page.xpath('.//*[@id="currencyTypeHidden"]/@value')[0]
        information_output(price_depart, price_return, currency)


main(sys.argv)
