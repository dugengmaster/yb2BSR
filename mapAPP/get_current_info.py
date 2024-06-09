# -*- coding: utf-8 -*-
"""
Created on Sun May 26 09:46:35 2024

@author: cfchu
"""

import requests
import json
import datetime

agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(agent)

global apis
apis = ["https://apis.youbike.com.tw/json/area-all.json","https://apis.youbike.com.tw/json/station-yb1.json",
       "https://apis.youbike.com.tw/json/station-yb2.json","https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=CWA-BA524CBF-8292-4BCA-9CC1-1AFEB8DF80D2&format=JSON",
       "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWA-BA524CBF-8292-4BCA-9CC1-1AFEB8DF80D2&format=JSON","https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/json?size=2000"]



def tpe_cur_rain(): #got current rain status
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
                   return 1
               else:
                   return 0
            
            
def tpe_cur_temp(): #got current temperature status
    global apis
    url=apis[4]
    
    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        
        for i in data["records"]["Station"]:
            if i["StationName"]=="信義":
               
                return i["WeatherElement"]["AirTemperature"]        

def tpe_yb_stn(): #got Taipei YB ststion No list
    global apis
    url=apis[2]
    tpestn=[]
    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        
        for i in data:
            if i["area_code"]=="00":
               tpestn.append(i["station_no"])
               
        return tpestn  

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

def holiday_qy(date):   #got holoday status date format:20150101
    global apis
    url=apis[5]
    
    response = session.get(url)
    #print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        
        for i in data:
            if i["date"]==date:
               
                return 1  
        return 0
            


if __name__ == "__main__":
    print("Taipei current rain status(Precipitation):",tpe_cur_rain())
    print("Taipei current temperature status(degree C):",tpe_cur_temp())
    #print("Taipei yb station no list:",tpe_yb_stn())
    station_no='500113079' # just for example
    print("Taipei YB station no "+station_no+" available ybs:",tpe_yb_qy(station_no))
    date="20240721" # just for example
    print(date+" is holiday?:",holiday_qy(date))