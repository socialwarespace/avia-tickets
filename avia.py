# -*- coding: utf-8 -*-
import requests
from json import loads
from vk_acc import tickets as vk, vlzhr

def link(dest="MUC"):
    return """http://api.travelpayouts.com/v2/prices/latest?token=33bed699a7afb6ba109520721d1e7c2c&limit=1000&destination={}&origin=MOW""".format(dest)

def int_date(s):
    return int(''.join(s.split('-')))

def good_date(s):
    li = s.split('-')
    return li[2]+'-'+li[1]

def good_price(value):
    s = str(value)
    return s[:-3] + '.' + s[-3] + 'k&#8381;'

start = 20170501
end = 20170509


group_id = 144021649
uis = [163663706]

def get_adresats():
    return [163663706, 41878375]
    users = vlzhr.method('groups.getMembers', {'group_id': group_id, 'count': 1000})['items']
    li = []
    for n in users:
        if vk.method('messages.isMessagesFromGroupAllowed', {'group_id': group_id, 'user_id': n})['is_allowed']:
            li.append(n)
    return li

def send_message(ui, message, at=""):
    vk.method('messages.send', {'peer_id': ui, 'message': message, 'attachment': at})
    print 'Sent to ' + str(ui)
    return True

def find_muc():
    flights = loads(requests.get(link("AER")).text)['data']
    dates = [n for n in flights if n['actual'] and int_date(n['depart_date']) >= start and int_date(n['return_date']) <= end and int_date(n['return_date']) - int_date(n['depart_date']) > 3]
    return dates

def send_muc():
    print 'Collecting tickets'
    li = find_muc()[:27]
    s = u"Билеты в Сочи на майские\n\n"
    for n in li:
        s += u"{} : {} -> {}\n".format(good_price(n['value']), good_date(n['depart_date']), good_date(n['return_date']))
    s += u"\nПодробнее смотрите в Aviasales (нужно вбить интересующие даты)"
    print u'Collecting adresats'
    for ui in get_adresats():
        send_message(ui, s)
    return True

def mass_send(message):
    for ui in get_adresats():
        send_message(ui, message)
    return True    

if __name__ == "__main__":
    pass
    #send_muc()
