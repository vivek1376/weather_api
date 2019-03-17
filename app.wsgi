#!/usr/bin/env python3

import os
import json
import re
import requests
import csv

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

# import bottle
from bottle import run, route, default_app, template, get, post, request, static_file, response, debug

dict_main = {}
with open('dailyweather.csv', mode='r') as csv_file:
    next(csv_file)
    for csv_line in csv_file:
        vals = csv_line.strip().split(',')
        dict_main[vals[0]] = {"TMAX":vals[1], "TMIN":vals[2]}


@get('/historical/<date>')
def getdataofdate(date):
    if date not in dict_main:
        response.status = 404
        str_404 = """
<pre>
 _|_|_|_|                                                  _|      _|  _|      _|    _|  _|        _|      
 _|        _|  _|_|  _|  _|_|    _|_|    _|  _|_|        _|        _|  _|    _|  _|  _|  _|          _|    
 _|_|_|    _|_|      _|_|      _|    _|  _|_|          _|          _|_|_|_|  _|  _|  _|_|_|_|          _|  
 _|        _|        _|        _|    _|  _|              _|            _|    _|  _|      _|          _|    
 _|_|_|_|  _|        _|          _|_|    _|                _|          _|      _|        _|        _|    
</pre>
"""
        return str_404

    response.content_type = 'application/json'
    dict_return = {"DATE":date, "TMAX":dict_main[date]["TMAX"], "TMIN":dict_main[date]["TMIN"]}
    return json.dumps(dict_return)


@post('/historical/')
def adddatafordate():

    print(str(request.url_args))
    print(str(request.method))
    print(str(request.headers.raw('Content-Type')))
    # print(request.query)
    # print(request.params)
    # print(request.json["DATE"])
    # print(request.body)

    if str(request.headers.raw('Content-Type')) == "application/x-www-form-urlencoded":
        date = request.forms.get('DATE').strip()
        tmax = request.forms.get('TMAX').strip()
        tmin = request.forms.get('TMIN').strip()
    elif str(request.headers.raw('Content-Type')) == "application/json" \
            or str(request.headers.raw('Content-Type')) == "application/json-rpc":
        date = str(request.json["DATE"]).strip()
        tmax = str(request.json["TMAX"]).strip()
        tmin = str(request.json["TMIN"]).strip()
        # print(type(request.json))

    response.status = 201
    response.content_type = 'application/json'


    # print(date)
    pattern = r'\d{8}'
    if re.match(pattern, date, flags=0) is None:
        print("date error")
        return "Error"

    # print(tmax)
    pattern = r'\d+(\.\d+)?'
    if re.match(pattern, tmax, flags=0) is None or re.match(pattern, tmin, flags=0) is None:
        print("tmax error")
        return "Error"

    # print(tmin)
    if date in dict_main:
        response.content_type = 'text/html'
        response.status = 400
        return "Error. Data for " + str(date) + " already present."

    dict_main[date] = {"TMAX":tmax, "TMIN":tmin}
    return_data = {"DATE": date}
    return json.dumps(return_data)

@get('/historical/')
def getalldates():
    response.content_type = 'application/json'
    dates_list = list(dict_main.keys())
    return json.dumps(dates_list)


run(reloader=True, debug=True)

