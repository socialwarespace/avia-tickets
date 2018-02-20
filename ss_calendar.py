import requests
import re
from selenium import webdriver
import time

link = u"https://www.skyscanner.ru/transport/flights/mosc/{city}/cheap-flights-from-moscow-to-amsterdam.html?adults=1&children=0&adultsv2=1&infants=0&cabinclass=economy&rtn=0&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&oym=17{month}&ref=home&selectedoday=01".format(city="ams", month="07")

def one_way():
    #text = requests.get(link).text
    driver = webdriver.Firefox()
    driver.get(link)
    print 'get'
    time.sleep(1)
    text = driver.page_source
    return text
