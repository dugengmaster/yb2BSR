# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:14:59 2024

@author: Eason Liao
"""
import os
import django
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yb2BSR.settings')
django.setup()
import googlemaps as gmap
import pandas as pd
import math
import uuid
from datetime import datetime
# import sqlite3 as sql
import time
from mapAPP.models import LtecelltowerTpe, Yb_stn2
from django.db.models import Q
import time
import numpy as np
import requests


def haversine(lat1, lon1, lat2, lon2):
    """
    在地圖上用經緯度計算距離
    Parameters
    ----------
    lat1 : TYPE float
    lon1 : TYPE float
    lat2 : TYPE float
    lon2 : TYPE float

    Returns
    -------
    distance : TYPE float
    """
    #經緯度轉為弧度制
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])


    dlat = lat1-lat2
    dlon = lon1-lon2


    a = math.sin(dlat/2)**2+ math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c= 2*math.atan2(math.sqrt(a), math.sqrt(1-a))


    #地球半徑
    R = 6371.0
    #單位公里換算成公尺
    distance = R*c*1000
    return distance

def precisionmatch(a,b,precision):
    for i in range(10,precision,-1):
        if round(a,i)== round(b,i):
            return True
    else:
        return False


class GoogleMapforUbike:
    def __init__(self, key):
        self.client = gmap.Client(key=key)
        self.lteCelltower = LtecelltowerTpe.objects.all()
        self.key = key

    def takeGpsByIP(self,home_mobile_country_code=None,
              home_mobile_network_code=None, radio_type=None, carrier=None,
              consider_ip=None, cell_towers=None, wifi_access_points=None) -> dict:
        # Geolocation API URL
        geolocation_url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + self.key
        params={}
        if home_mobile_country_code is not None:
            params["homeMobileCountryCode"] = home_mobile_country_code
        if home_mobile_network_code is not None:
            params["homeMobileNetworkCode"] = home_mobile_network_code
        if radio_type is not None:
            params["radioType"] = radio_type
        if carrier is not None:
            params["carrier"] = carrier
        if consider_ip is not None:
            params["considerIp"] = consider_ip
        if cell_towers is not None:
            params["cellTowers"] = cell_towers
        if wifi_access_points is not None:
            params["wifiAccessPoints"] = wifi_access_points
        # Send request to Google Geolocation API
        response = requests.post(geolocation_url, params)
        data = response.json()

        if 'location' in data:
            latitude = data['location']['lat']
            longitude = data['location']['lng']
        else:
            latitude = None
            longitude = None

        return {
            'lat': latitude,
            'lng': longitude
        }

    def getgeolocation(self, Carrier="中華電信") -> dict:
        #先取得粗略的GPS定位
        gps = self.takeGpsByIP()
        carrier = {'1':"遠傳電信", "5":"遠傳電信","89":"台灣大哥大","92":"中華電信","97":"台灣大哥大"}
        Net = []
        for key, value in carrier.items():
            if value == Carrier: Net.append(int(key))

        if len(Net) >1:
            towerList = self.lteCelltower.filter(Q(net=Net[0]) | Q(net=Net[1]))
        else:
            towerList = self.lteCelltower.filter(Q(net=Net[0]))
        pickthem = []
        distanceList= []
        lat1, lon1 = gps["lat"], gps["lng"]
        #從表裡面找到最近的基地台資訊
        for tower in towerList:
            distance = haversine(lat1, lon1, float(tower.lat), float(tower.lon))
            if distance <= 1000:
                temp = {'lat':tower.lat, 'lng':tower.lon}
                pickthem.append(temp)
                distanceList.append(distance)


        x = [i for i in range(len(distanceList)) if distanceList[i] == min(distanceList)]
        if len(x) > 0:
            cellTower = [{
                "cellId": int(pickthem[x[0]]["cell"]),
                "locationAreaCode": int(pickthem[x[0]]["area"]),
                "mobileCountryCode": int(pickthem[x[0]]["mcc"]),
                "mobileNetworkCode": int(pickthem[x[0]]["net"]),
                "age": 0,
                "signalStrength": -60,
                "timingAdvance": 15
                }]
            #取得本機wifi實體位置
            mac = hex(uuid.getnode())[2:]
            macAddress = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
            wifiAccessPoint = [{
            "macAddress": macAddress,
            "signalStrength": -43,
            "signalToNoiseRatio": 0,
            "channel": 36,
            "age": 0
            }]
            myGPS = self.takeGpsByIP(ip,home_mobile_country_code=466, home_mobile_network_code=int(pickthem[x[0]]["net"]),
                                        radio_type="lte", carrier=Carrier, consider_ip=True,
                                        cell_towers= cellTower, wifi_access_points=wifiAccessPoint)
        else:
            myGPS = gps
        return myGPS

    def getBikeStation(self, location) -> dict:
        # #先取得半徑500m的bike station {'lat': 123456, 'lng':4561}
        # place_search = self.client.places_nearby(location, keyword="youbike", radius=500)
        # #數量太少再擴大搜尋
        # if len(place_search['results']) <5:
        #     place_search = self.client.places_nearby(location, keyword="youbike", radius=1000)
        #     if len(place_search['results']) ==0:

        #         return "附近沒有YouBike站點"


        # #依照目前座標給出距離最近的5個站點
        # coordinates = []

        # for result in place_search['results']:
        #     if result['business_status']=='OPERATIONAL':
        #         coordinate = result['geometry']['location']
        #         coordinate['distance'] = haversine(location['lat'], location['lng'], coordinate['lat'], coordinate['lng'])
        #         coordinates.append(coordinate)
        # df = pd.DataFrame(coordinates)
        # df = df.sort_values(by='distance')

        # top5 = df.head(5)
        # del top5['distance']
        staInfo = Yb_stn2.objects.all()#filter(area_code='00')
        sta_info_df = pd.DataFrame([{'lat': float(sta.lat), 'lng': float(sta.lng), 'name_tw': sta.name_tw} for sta in staInfo])
        # 排重
        sta_info_df = sta_info_df.drop_duplicates(subset=['name_tw'])
        sta_info_df['distance']=sta_info_df.apply(lambda row: haversine(location['lat'], location['lng'], row['lat'], row['lng']), axis=1)
        sta_info_df = sta_info_df.sort_values(by='distance')
        sta_info_df = sta_info_df.head(5)
        del sta_info_df['distance']
        # for line in top5.index:
        #     for l in sta_info_df.index:
        #         if precisionmatch(top5.loc[line,'lat'],sta_info_df.loc[l,'lat'],4) and  precisionmatch(top5.loc[line,'lng'],sta_info_df.loc[l,'lng'],4):
        #             top5.loc[line,'name_tw'] = sta_info_df.loc[l,'name_tw']
        #         elif precisionmatch(top5.loc[line,'lat'],sta_info_df.loc[l,'lat'],3) and  precisionmatch(top5.loc[line,'lng'],sta_info_df.loc[l,'lng'],3):
        #             top5.loc[line,'name_tw'] = sta_info_df.loc[l,'name_tw']
        #         elif precisionmatch(top5.loc[line,'lat'],sta_info_df.loc[l,'lat'],2) and  precisionmatch(top5.loc[line,'lng'],sta_info_df.loc[l,'lng'],2):
        #             top5.loc[line,'name_tw'] = sta_info_df.loc[l,'name_tw']
        # top5 = top5.merge(sta_info_df, how='left', left_on=['lat', 'lng'], right_on=['lat', 'lng'])
        result = sta_info_df.to_dict('records')
        return result


    def getDuration(self, location, destination) -> dict:
        departuretime = datetime.now()

        matrix = self.client.distance_matrix(location, destination, mode='walking', units='metrics', departure_time=departuretime)

        for index, coor in enumerate(destination):
            coor['time_cost'] = matrix['rows'][0]['elements'][index]['duration']['value']
        return destination
# goodRestoraunt = []
# #Listing the Rating > 4.7
# for i in range(len(place_search['results'])):
#     temp = {}
#     if place_search['results'][i]['rating'] >= 4.7:
#         temp['name'] = place_search['results'][i]['name']
#         temp['geometry'] = place_search['results'][i]['geometry']
#         temp['rating'] = place_search['results'][i]['rating']
#         goodRestoraunt.append(temp)




if __name__ == '__main__':
    # gmap = GoogleMapforUbike('AIzaSyDeEzYq-fwNLOXJu7XzAXU2NgxJW3th_2A')
    gmap = gmap.Client(key='')
    start = time.time()
    posi = gmap.geolocate()
    end = time.time()
    # myposi = {'lat': 25.048159037642492, 'lng': 121.51707574725279}
    # bike = gmap.getBikeStation(myposi)
    # print(gmap.getDuration(myposi,bike))



