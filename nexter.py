from codecs import open
from math import fabs, sqrt
from json import loads
import os


routes = os.path.join(os.path.dirname(__file__), 'routes.json')
cities = os.path.join(os.path.dirname(__file__), 'cities.json')
airports_file = os.path.join(os.path.dirname(__file__), 'airports.json')

def get_city(code):
    li = get_cities()
    for n in li:
        if n['code'].lower() == code.lower():
            return n
    return ''

def get_cities():
    with open(cities, 'r', encoding='utf-8') as f:
        return loads(f.read())

def get_airports():
    with open(airports_file, 'r', encoding='utf-8') as f:
        return loads(f.read())

def get_routes():
    with open(routes, 'r', encoding='utf-8') as f:
        return loads(f.read())

def get_dist(cities):
    try:
        l = 111 * (cities[0]['coordinates']['lon'] - cities[1]['coordinates']['lon'])
        w = 111 * (cities[0]['coordinates']['lat'] - cities[1]['coordinates']['lat'])
    except TypeError:
        return 1000000
    dist = sqrt(l**2 + w**2)
    return dist

def get_cairs(city):
    li = get_airports()
    good = []
    for n in li:
        if n['city_code'].lower() == city.lower():
            good.append(n['code'])
    return good

def get_next(code):
    city = get_city(code)
    good = []
    for n in get_cities():
        dist = get_dist([city, n])
        if dist < 400:
            n['s'] = int(dist)
            good.append(n)
    return good

def get_ways(fr, to):
    fr = fr.lower()
    frairs = get_cairs(fr)
    ne = get_next(to)
    routes = get_routes()
    ways = [n["arrival_airport_iata"].lower() for n in routes if n["departure_airport_iata"] in frairs]
    good = [n for n in ne if n['code'].lower() in ways]
    return good
    
    

