# -*- coding: utf-8 -*-
from codecs import open
import os
from time import sleep
import time
from json import loads, load
import requests
from flask import Markup

lf = os.path.join(os.path.dirname(__file__), 'logs', 'log.txt')

def daysc(dateString1, dateString2):
        dateString1=dateString1[0:10] # вырезаем такое "2010-03-01"
        dateString2=dateString2[0:10]
        t1=time.mktime(time.strptime(dateString1, '%Y-%m-%d'))
        t2=time.mktime(time.strptime(dateString2, '%Y-%m-%d'))
        t=round((t2-t1)/(60*60*24))+1
        return int(t)

def log(text):
    with open(lf, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        f.seek(0)
        f.writelines( [text+u"<br><br>"]+lines )
    return True

def get_log():
    try:
        with open(lf, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        renew_log()
        return ''

def renew_log(text=""):
    with open(lf, 'w', encoding='utf-8') as f:
        f.write(text)

def link(origin="MOW", dest="MUC", date="2017-05-01", one_way="false", dur=4):#, page=1):
    if not one_way=="true":
        return """http://api.travelpayouts.com/v1/prices/calendar?trip_duration={}&depart_date={}&origin={}&destination={}&calendar_type=departure_date&token=33bed699a7afb6ba109520721d1e7c2c""".format(str(dur), date, origin, dest)
    return """http://api.travelpayouts.com/v2/prices/month-matrix?limit=1000&token=33bed699a7afb6ba109520721d1e7c2c&destination={}&origin={}&show_to_affiliates=false&month={}""".format(dest, origin, date)
    #return """http://api.travelpayouts.com/v1/prices/calendar?transfers=1&limit=1000&token=33bed699a7afb6ba109520721d1e7c2c&destination={}&origin={}&depart_date={}&calendar_type=departure_type&number_of_changes=1""".format(dest, origin, date)
    return """http://api.travelpayouts.com/v2/prices/latest?token=33bed699a7afb6ba109520721d1e7c2c&limit=1000&destination={}&origin={}&one_way={}&page={}&show_to_affiliates=false""".format(dest, origin, one_way, str(page))

def jdate(s):
    return int(''.join((s.split("T")[0]).split('-')))

def sdate(i):
    s = str(jdate(i))
    return s[:4] + '-' + s[4:6] + '-' + s[-2:]

def get_best(origin="MOW", dest="BTS", start=20180915, end=20180930, days=4, daysto=10, transfers=2, one_way="true"):
    ''' актуальная функция поиска билетов '''
    months, year = ["0"*(2-len(str(n)))+str(n) for n in range(int(str(start)[4:-2]), int(str(end)[4:-2])+1)], str(start)[:4]
    li = []
    if one_way == "false":
        for n in range(days, daysto):
            for m in months:
                dic = loads(requests.get(link(origin, dest, year+'-'+m, "false", n)).text)['data']
                print year+'-'+m+','+str(n)+'days'
                li += [dic[it] for it in dic if jdate(dic[it]['departure_at']) >= start and jdate(dic[it]['return_at']) <= end]
        for n in li:
            n['depart_date'] = sdate(n['departure_at'])
            n['return_date'] = sdate(n['return_at'])
            n['value'] = int(n['price'])
    else:
        good = []
        for m in months:
            good += [n for n in loads(requests.get(link(origin, dest, year+'-'+m+'-01', "true")).text)['data'] if int_date(n['depart_date']) >= start and int_date(n['depart_date']) + days <= end]
        for n in good:
            if n['value'] == min([m['value'] for m in good if m['depart_date'] == n['depart_date']]):
                n['value'] = int(n['value'])
                li.append(n)
    li.sort(key = lambda x: x['value'])
    return li
                

def int_date(s):
    if s == 0 or s=='':
        return 0
    return int(''.join(s.split('-')))

def good_date(s):
    li = s.split('-')
    return li[2]+'-'+li[1]

def good_price(value):
    s = str(value)
    return s[:-3] + '.' + s[-3] + 'k&#8381;'


start = 20170501
end = 20170509

cfile = os.path.join(os.path.dirname(__file__), 'cities.json')

def get_cnames():
    ''' возвращает список всех городов, с кодами (для поиска на странице) '''
    with open(cfile, 'r', encoding='utf-8') as f:
        cities = load(f)
    li = []
    for n in cities:
        city = [n['code']]
        city.append(u"{} - {}".format(n['name'], n['name_translations'].get('ru', '')))
        li.append(city)
    return li

def find_dates(page, origin, code, start, end, days=4, transfers=1, one_way="false"):
    ''' старая версия поиска билетов '''
    flights = loads(requests.get(link(origin, code, one_way, page)).text)['data']
    daysto = days*3
    if one_way == "true":
        dates = [n for n in flights if n['actual'] and n['number_of_changes'] <= transfers and int_date(n['depart_date']) >= start and int_date(n['depart_date']) <= end]
    else:
        dates = [n for n in flights if n['actual'] and n['number_of_changes'] <= transfers and int_date(n['depart_date']) >= start and int_date(n['return_date']) <= end and daysc(n['return_date'], n['depart_date']) >= days and daysc(n['return_date'], n['depart_date']) <= daysto]
    return dates

def find(origin="MOW", city="BTS", start = 20180913, end = 20180930, days=2, daysto=6, transfers=1, one_way="false", dic={}):
    ''' находит и выводит билеты в HTML виде '''
    renew_log()
    if not len(dic) == 0:
        origin, city, start, end, days, daysto, transfers, one_way = dic['origin'], dic['city'], dic['start'], dic['end'], dic['daysto'], dic['daysto'], 3, dic['one_way']
    log(u"Собираем билеты ...")
    li = get_best(origin, city, start, end, days, daysto, transfers, one_way)
    s = u"Билеты в {}<br><br>".format(city)
    for n in li:
        if one_way=="false":
            s += u"{} : {} -> {}<br>".format(good_price(n['value']), good_date(n['depart_date']), good_date(n['return_date']))
        else:
            s += u"{} : {}<br>".format(good_price(n['value']), good_date(n['depart_date']))
    s += u"<br>Подробнее смотрите в Aviasales (нужно вбить интересующие даты)"
    log(s)
    return Markup(s)
