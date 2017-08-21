# *-*coding:utf-8*-*
import sys
import requests
import re
from collections import namedtuple
from itertools import product
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
    if not port_depart.code or not port_destin.code:
        print 'Error. IATA-code is not correct.'
        return
    if port_depart.code == port_destin.code:
        print 'Error. IATA-departure is the same as IATA-arrival.'
        return
    return True


def parser(direction, page):
    result_price = []
    tree = html.fromstring(page)
    table = tree.xpath('.//*[@id="{}"]/div[2]/*'.format(direction))
    for row in table:
        time_depart = row.xpath(
            './/*[@data-qa="timeDeparture_flightItem"]/text()')
        time_arriv = row.xpath(
            './/*[@data-qa="timeArrived_flightItem"]/text()')
        duration = row.xpath(
            './/*[@data-qa="durationTotal_flightItemShort"]/text()')
        for column in row.xpath('./*[@class="select-item-simple"]/*'):
            tariff = column.xpath('@data-tariff-type')
            price = column.xpath('.//*[@data-qa="amount"]/text()')
            if price:
                result_price.append([
                    str(time_depart[0]),
                    str(time_arriv[0]),
                    'h'.join(duration[0].encode('ascii', 'ignore').split()),
                    str(tariff[0]),
                    int(price[0].encode('ascii', 'ignore')),
                ])
    return result_price


def check_input_data(args):
    """ Осуществляет разбор параметров полученных из sys.argv и их проверку"""
    if len(args) == 5:
        return args[1:]
    elif len(args) == 4:
        return args[1:] + [None]
    else:
        print ('Error. You entered {} parameters, '
               'you must enter 3 or 4 parameters.').format(len(args[1:]))
        return


def information_output(price_outbound, price_return, currency):
    if price_return:
        price_result = []
        for elem_out, elem_ret in product(price_outbound, price_return):
            price_result.append({
                'track_out': elem_out,
                'track_return': elem_ret,
                'total_sum': elem_out[-1] + elem_ret[-1]
            })
        for elem_res in sorted(price_result, key=lambda x: x['total_sum']):
            print ('Departure-{}, arrival-{}, duration:{}, tariff:{},'
                   ' price:{} ').format(*elem_res['track_out']) + currency
            print ('Departure-{}, arrival-{}, duration:{}, tariff:{}, '
                   'price:{}'.format(*elem_res['track_return']) +
                   currency)
            print 'Total:', elem_res['total_sum'], currency, '\n'
    else:
        for elem_out in sorted(price_outbound, key=lambda x: x[-1]):
            print ('Departure-{}, arrival-{}, duration:{}, tariff:{},' +
                   ' price:{}').format(*elem_out) + currency, '\n'


def main():
    # import pdb; pdb.set_trace()
    # input_data = check_input_data(sys_arg)
    # if not input_data:
    #     return
    # iata_depart, iata_destin, date_depart, date_return = input_data
    iata_depart = 'DME'
    iata_destin = 'GOJ'
    date_depart = '18.12.2017'
    date_return = None#'26.12.2017'
    if not date_validation(date_depart, date_return):
        return
    port_depart = DataAirport(iata_depart)
    port_destin = DataAirport(iata_destin)
    if not code_iata_validation(port_depart, port_destin):
        return
    response_html = requests_s7(
        port_depart,
        port_destin,
        date_depart,
        date_return
    )
    price_outbound = parser(
        'exact_outbound_flight_table',
        response_html.text
    )
    price_return = parser(
        'exact_inbound_flight_table',
        response_html.text
    )
    if not price_outbound:
        print 'Unfortunately, we did not find any suitable flights for you. Try changing the search parameters.'
    else:
        page = html.fromstring(response_html.text)
        currency = page.xpath('.//*[@id="currencyTypeHidden"]/@value')[0]
        information_output(price_outbound, price_return, currency)

main()
# main(sys.argv)
