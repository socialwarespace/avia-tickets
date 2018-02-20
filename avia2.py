# -*- coding: utf-8 -*-

import requests
from json import loads, load
from codecs import open
from avia import mass_send
import os

routes = os.path.join(os.path.dirname(__file__), 'routes.json')
cities = os.path.join(os.path.dirname(__file__), 'cities.json')
airports_file = os.path.join(os.path.dirname(__file__), 'airports.json')

def get_routes():
    with open(routes, 'r', encoding='utf-8') as f:
        dic = load(f)
    return dic

def get_destinations(depart=["DME", "VKO", "SVO"], transfers=0):
    #text = requests.get('http://api.travelpayouts.com/data/routes.json').text
    #dic = loads(text)
    dic = get_routes()
    destinations = []
    for n in dic:
        if n['departure_airport_iata'] in depart and n['transfers'] <= transfers:
            destinations.append(n['arrival_airport_iata'])
    return destinations

def get_cities():
    #text = requests.get('http://api.travelpayouts.com/data/cities.json').text
    with open(cities, 'r', encoding='utf-8') as f:
        return load(f)

def get_city(li, code):
    for n in li:
        if n['code'] == code:
            return n['name']
    return ''

def get_airports():
    with open(airports_file, 'r', encoding='utf-8') as f:
        airports = load(f)
    return airports

def get_europe_dests(depart=["DME", "VKO", "SVO"]):
    li = get_destinations(depart)
    airports = get_airports()
    good = []
    for n in airports:
        if n['code'] in li and n['time_zone'].split('/')[0] == 'Europe' and not n['country_code'] == 'RU':
            good.append(n['code'])
    return good

def get_country_dests(country, depart=["DME", "VKO", "SVO"], transfers=0):
    li = get_airports()
    good = []
    for n in li:
        if n['country_code'].lower() == country.lower():
            good.append(n['code'])
    return good
    li = get_destinations(depart, transfers)
    airports = get_airports()
    good = []
    for n in airports:
        if n['code'] in li and n['country_code'] == country:
            good.append(n['code'])
    return good

def link(dest="MUC", origin="MOW"):
    return """http://api.travelpayouts.com/v2/prices/latest?token=33bed699a7afb6ba109520721d1e7c2c&limit=1000&destination={}&origin={}""".format(dest, origin)

def int_date(s):
    return int(''.join(s.split('-')))

def good_date(s):
    li = s.split('-')
    return li[2]+'-'+li[1]

def good_price(value):
    s = str(value)
    return s[:-3] + '.' + s[-3] + 'k&#8381;'

old_min = min
def min(li):
    try:
        return old_min(li)
    except Exception:
        return '-'

start = 20170501
end = 20170509

def get_cairs(city):
    li = get_airports()
    good = []
    for n in li:
        if n['city_code'].lower() == city.lower():
            good.append(n['code'])
    return good

def find_flights(dest, origin, start, end, days_count = 4):
    flights = loads(requests.get(link(dest, origin)).text)['data']
    dates = [n for n in flights if n['actual'] and int_date(n['depart_date']) >= start and int_date(n['return_date']) <= end and int_date(n['return_date']) - int_date(n['depart_date']) >= days_count]
    return dates

def get_country_routes(country, start, end, days=5, origin="MOW"):
    departs = get_cairs(origin)
    dests = get_country_dests(country, depart, transfers=3)
    print 'Dests downloaded'
    cities = get_cities()
    print 'Cities downloaded'
    li = []
    for n in dests:
        dic = {}
        flights = find_flights(n, origin, start, end, days)
        min_price = min([m['value'] for m in flights])
        if len(flights) > 0:
            dic = {'port': n, 'city': get_city(cities, n), 'flights': flights, 'min_price': min_price}
            dic['flights'].sort(key = lambda x: x['value'])
            li.append(dic)
        print dic.get('city', n) + ': found {} flights, min price: {}'.format(str(len(flights)), str(min_price))
    li.sort(key = lambda x: x['min_price'])
    return li

def get_may_routes(depart=["DME", "VKO", "SVO"], origin="MOW"):
    dests = get_europe_dests(depart)
    print 'Dests downloaded'
    cities = get_cities()
    print 'Cities downloaded'
    li = []
    for n in dests:
        dic = {}
        flights = find_flights(n, origin)
        min_price = min([m['value'] for m in flights])
        if len(flights) > 0:
            dic = {'port': n, 'city': get_city(cities, n), 'flights': flights, 'min_price': min_price}
            dic['flights'].sort(key = lambda x: x['value'])
            li.append(dic)
        print dic.get('city', n) + ': found {} flights, min price: {}'.format(str(len(flights)), str(min_price))
    li.sort(key = lambda x: x['min_price'])
    return li

def good_flight(flight):
    return good_price(flight['value']) + ': ' + good_date(flight['depart_date']) + ' -> ' + good_date(flight['return_date'])

def show():
    message = ''
    city = "MOW"
    depart=get_cairs(city)
    li = get_may_routes(depart, city)
    for n in li:
        if n['min_price'] < 18000:
            message += n['city'] + '\n' + good_flight(n['flights'][0]) + '\n'
            try:
                message += good_flight(n['flights'][1]) + '\n\n'
            except IndexError:
                message += '\n'
    return message

if __name__ == "__main__":
    pass
    #mass_send(show())
        

