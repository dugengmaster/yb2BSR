# -*- coding: utf-8 -*-
"""
Created on Sun May 26 09:46:35 2024

@author: cfchu
"""

import requests
import json
import datetime
import queue
import pandas as pd
from django.conf import settings


agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(agent)
auth = settings.METEOROLOGICAL_DATA_OPEN_PLATFORM

global apis
apis = ["https://apis.youbike.com.tw/json/area-all.json",
        "https://apis.youbike.com.tw/json/station-yb1.json",
        "https://apis.youbike.com.tw/json/station-yb2.json",
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization={auth}&format=JSON",
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={auth}&format=JSON",
        "https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/json?size=2000"]

#取得最新的站點狀態
def getstationbike(coordinates, q) -> list:
    header = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
    dfs = []
    sess = requests.session()
    for url in apis[1:3]:
        r = sess.get(url, headers = header)
        if r.status_code==requests.codes.ok:
            data = json.loads(r.text)
            tpeStation = [sta for sta in data] 
            df = pd.DataFrame(tpeStation)
            df['lat']= df['lat'].astype(float)
            df['lng']= df['lng'].astype(float)
            dfs.append(df)        
    stationStatus = []
    for coor in coordinates:
        condition1 = dfs[0]['name_tw']==coor['name_tw']
        condition2 = dfs[1]['name_tw']==coor['name_tw']
        availabel_spaces = 0
        parking_spaces = 0
        updated_time = None
        if condition1.any():
            availabel_spaces += dfs[0].loc[condition1,'available_spaces'].iloc[0]
            parking_spaces += dfs[0].loc[condition1,'parking_spaces'].iloc[0]
            updated_time = dfs[0].loc[condition1,'updated_at'].iloc[0] 
        if condition2.any():
            availabel_spaces += dfs[1].loc[condition2,'available_spaces'].iloc[0]
            parking_spaces += dfs[1].loc[condition2,'parking_spaces'].iloc[0]
            try:
                if dfs[1].loc[condition2,'updated_at'].iloc[0] > updated_time:
                    updated_time = dfs[1].loc[condition2,'updated_at'].iloc[0] 
            except:
                updated_time = dfs[1].loc[condition2,'updated_at'].iloc[0]
        temp = {
            'name':coor['name_tw'],
            'available_spaces': str(availabel_spaces)+'/'+str(parking_spaces),
            'update_time': updated_time
            }

        stationStatus.append(temp)
            
    q.put(stationStatus)
    


#got current rain status
def tpe_cur_rain(q):
    global apis
    url=apis[3]

    response = session.get(url)

    if response.status_code == 200:
        data = response.json()
        #print(data)
        # print(type(data))
        for i in data["records"]["Station"]:

            if i["StationName"]=="信義":
                rain_amt = i["RainfallElement"]["Past10Min"]["Precipitation"]
                if rain_amt/10 >(0.3/6):
                    # print(rain_amt)
                #    return 1
                    r = 1
                    q.put(r)
                    break
                    # return
                else:
                    # print(rain_amt)
                #    return 0
                    r = 0
                    q.put(r)
                    break
                    # return

#got current temperature status
def tpe_cur_temp(q):
    global apis
    url=apis[4]

    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()

        for i in data["records"]["Station"]:
            if i["StationId"]=="C0I080":
                # print(i["WeatherElement"]["AirTemperature"])
                # print(type(i["WeatherElement"]["AirTemperature"]))
                # return i["WeatherElement"]["AirTemperature"]
                q.put(i["WeatherElement"]["AirTemperature"])

#got Taipei YB station No list
def tpe_yb_stn():
    global apis
    url=apis[2]
    tpeStn=[]
    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()

        for i in data:
            if i["area_code"]=="00":
               tpeStn.append(i["station_no"])

        return tpeStn

def tpe_yb_qy(station_no): #got the available ybs for a station in Taipei
    global apis
    url=apis[2]

    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()

        for i in data:
            if i["station_no"]==station_no:

                return i["available_spaces"]

            #Taipei station_no range:5001xxxxx

#got holoday status date format:20150101
def holiday_qy(date,q):
    global apis
    url=apis[5]

    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()

        for i in data:
            if i["date"]==date:
                q.put(1)
                return
            else:
                q.put(0)
                return


if __name__ == "__main__":
    print("Taipei current rain status(Precipitation):",tpe_cur_rain())
    print("Taipei current temperature status(degree C):",tpe_cur_temp())
    #print("Taipei yb station no list:",tpe_yb_stn())
    station_no='500113079' # just for example
    print("Taipei YB station no "+station_no+" available ybs:",tpe_yb_qy(station_no))
    date="20240721" # just for example
    print(date+" is holiday?:",holiday_qy(date))