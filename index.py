# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, url_for, Markup
from avia_finder import find, get_log, renew_log, get_cnames
from codecs import open
import os
#import sys

#reload(sys)
#sys.setdefaultencoding("utf-8")

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = u'fgавп'
app.debug = True

months = ["Jan", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

@app.route("/")
def index():
    return render_template("index.html", cities=get_cnames(), enumerate=enumerate, months=months, range=range)

@app.route("/norway")
def norway():
    return render_template("norway.html")

@app.route("/find_osl")
def find_osl():
    a = request.args
    result = find("MOW", "OSL", int(a['start']), int(a['end']), int(a['days']), int(a['trans']), a['one_way'])
    return result

@app.route("/panel")
def panel():
    log = get_log()
    args = request.args
    return render_template("panel.html", log=log, args=args)

@app.route("/work")
def work():
    renew_log()
    a = request.args
    start = 20180000 + int(a['startd']) + int(a['startm'])*100
    end = 20180000 + int(a['endd']) + int(a['endm'])*100
    days = int(a['daysfrom'])
    daysto = int(a['daysto'])
    return jsonify({'result': find(a['origin'].upper(), a['city'].upper(), start, end, days, daysto, 3, a['one_way'])})

@app.route("/log")
def log():
    log = get_log()
    return render_template("log.html", log=log)

@app.route("/clean_log")
def clean_log():
    renew_log()
    return ''

@app.route("/load_log")
def load_log():
    with open('logs/log.txt', 'r', encoding='utf-8') as f:
        return f.read()
    def generate():
        with open('logs/log.txt', 'r', encoding='utf-8') as f:
            while True:
                yield f.read()
                sleep(1)
    return app.response_class(generate(), mimetype='text/plain')
    #return jsonify({'text': get_log()})

@app.route('/static/docsupport/<filename>')
def send_js_2(filename):
    with open(os.path.join('static', 'docsupport', filename), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/static/<filename>')
def send_js(filename):
    with open(os.path.join('static', filename), 'r', encoding='utf-8') as f:
        return Markup(f.read())

if __name__ == "__main__":
    app.run('127.0.0.1', 81)
    
