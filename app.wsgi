#!/usr/bin/env python3

import os
import json
import re
import requests
import csv
import time

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

# import bottle
from bottle import run, route, default_app, template, get, post, delete, request, static_file, response, debug, install


def build_weather_data_list_from_json_openwmpapi(forecast_data):

    weather_data = {}
    
    weather_forecast_resp = requests.get(weather_forecast_api_url)
    weather_forecast_json = weather_forecast_resp.json()['list']

    index = 0
    for item in weather_forecast_json:
        # obtain date & temperature values
        dt_date_str = time.strftime('%Y%m%d', time.gmtime(item['dt']))
        temp_min = item['main']['temp_min']
        temp_max = item['main']['temp_max']

        temp_min = int(temp_min * float(9/5) - 459.69)
        temp_max = int(temp_max * float(9/5) - 459.69)

        if dt_date_str not in weather_data:
            weather_data[dt_date_str] = [temp_min, temp_max, index]
            forecast_data.append({"DATE": dt_date_str,
                                  "TMAX": temp_max,
                                  "TMIN": temp_min})

            if dt_date_str not in dict_main:
                list_dates.append(dt_date_str)

            index += 1

        else:

            if temp_min < weather_data[dt_date_str][0]:
                weather_data[dt_date_str][0] = temp_min
                forecast_data[weather_data[dt_date_str][2]]["TMIN"] = temp_min

            if temp_max > weather_data[dt_date_str][1]:
                weather_data[dt_date_str][1] = temp_max
                forecast_data[weather_data[dt_date_str][2]]["TMAX"] = temp_max

    for key, value in weather_data.items():
        if key not in dict_main:
            dict_main[key] = {"TMAX": value[1], "TMIN": value[0]}
        else:
            dict_main[key]["TMAX"] = value[1]
            dict_main[key]["TMIN"] = value[0]


@get('/getdates/')
def getdates():
    response.content_type = "application/json"
    return json.dumps(list_dates)


@get('/forecast/')
def fetch_weather_data_openweathermap_api():

    forecast_data = []
    build_weather_data_list_from_json_openwmpapi(forecast_data)

    response.content_type = "application/json"
    return json.dumps(forecast_data)
    
@get('/pid/')
def getpid():
    response.content_type = 'text/html'
    return str(os.getpid())

@get('/forecast/<date>')
def getforecastdata(date):
    
    build_weather_data_list_from_json_openwmpapi([])
    
    forecast_data = []
    
    if date not in list_dates:
        response.status = 404
        return "no data"
    
    ind = list_dates.index(date)
    for item in list_dates[ind: ind + 7]:
        forecast_data.append({"DATE":item,
                              "TMAX":dict_main[item]["TMAX"],
                              "TMIN":dict_main[item]["TMIN"]})

    response.content_type = 'application/json'
    return json.dumps(forecast_data)
    
        
@get('/historical/<date>')
def getdataofdate(date):
#    for item in dict_main:      #
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
    dict_return = {"DATE": date, "TMAX": dict_main[date]["TMAX"], "TMIN": dict_main[date]["TMIN"]}
    return json.dumps(dict_return)


@delete('/historical/<date>')
def deletedatefordate(date):
    del dict_main[date]

    response.content_type = 'text/html'
    response.status = 200
    return 

@post('/historical/')
def adddatafordate():
    tmp_list_dates = []
    
    if str(request.headers.raw('Content-Type')) == "application/x-www-form-urlencoded":
        date = request.forms.get('DATE').strip()
        tmax = request.forms.get('TMAX').strip()
        tmin = request.forms.get('TMIN').strip()
    elif str(request.headers.raw('Content-Type')) == "application/json" \
            or str(request.headers.raw('Content-Type')) == "application/json-rpc":
        date = str(request.json["DATE"]).strip()
        tmax = str(request.json["TMAX"]).strip()
        tmin = str(request.json["TMIN"]).strip()

    pattern = r'\d{8}'
    if not (re.match(r'^\d{8}$', date, flags=0) and
            re.match(r'^\d+(\.\d+)?$', tmax, flags=0) and
            re.match(r'^\d+(\.\d+)?$', tmin, flags=0)):
        response.content_type = 'text/html'
        response.status = 400
        return "Error. Malformed Input."

    # if date in dict_main:
    #     response.content_type = 'text/html'
    #     response.status = 400
    #     return "Error. Data for " + str(date) + " already present."

    dict_main[date] = {"TMAX": tmax, "TMIN": tmin}
    return_data = {"DATE": date}

    # response.status_code = 201
    response.status = 201  # created
    response.content_type = 'application/json'

    return json.dumps(return_data)


@get('/historical/')
def getalldates():
    response.content_type = 'application/json'
    return json.dumps(list_dict_dates)


@route('/<filename:re:.*>')
def getdocs(filename):
    if not filename:
        filename = "index.html"

    return static_file(filename, root='docs/')


# MAIN

#swagger_def = _load_swagger_def()
#install(SwaggerPlugin(swagger_def))

dict_main = {}
list_dates = []
list_dict_dates = []
weather_forecast_api_url = "http://api.openweathermap.org/data/2.5/" \
    "forecast?id=4508722&APPID=523d7208c52ada93fac8b64ede3f786f"

with open('dailyweather.csv', mode='r') as csv_file:
    next(csv_file)  # skip first header row

    for csv_line in csv_file:
        vals = csv_line.strip().split(',')
        dict_main[vals[0]] = {"TMAX": vals[1], "TMIN": vals[2]}
        list_dates.append(vals[0])
        list_dict_dates.append({"DATE":vals[0]})

build_weather_data_list_from_json_openwmpapi([])



# debug(mode=True)
application = default_app()


