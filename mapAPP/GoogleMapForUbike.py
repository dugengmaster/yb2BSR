# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:14:59 2024

@author: 88698
"""
import os
import django
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yb2BSR.settings')

# 初始化 Django
django.setup()
import googlemaps as gmap
import pandas as pd
import math
import uuid
from datetime import datetime
# import sqlite3 as sql
import time
from mapAPP.models import LtecelltowerTpe, Yb_stn
from django.db.models import Q


def haversine(lat1, lon1, lat2, lon2):
    """
    在地圖上用經緯度計算距離

    Parameters
    ----------
    lat1 : TYPE
        float
    lon1 : TYPE
        float
    lat2 : TYPE
        float
    lon2 : TYPE
        float

    Returns
    -------
    distance : TYPE
        float

    """
    #經緯度轉為弧度制
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat1-lat2
    dlon = lon1-lon2
    
    a = math.sin(dlat/2)**2+ math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c= 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    #地球半徑
    R = 6371.0
    #單位公里
    distance = R*c*1000
    return distance
    

class GoogleMapforUbike:
    def __init__(self, key):
        self.client = gmap.Client(key=key)
        self.lteCelltower = LtecelltowerTpe.objects.all()

        
        
    def getgeolocation(self, Carrier="中華電信") -> dict:
        #先取得粗略的GPS定位
        gps = self.client.geolocate()
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
        lat1, lon1 = gps["location"]["lat"], gps["location"]["lng"]
        #從表裡面找到最近的基地台資訊
        for tower in towerList:
            distance = haversine(lat1, lon1, tower.lat, tower.lon)
            if distance <= 1000:
                temp = {'lat':tower.lat, 'lng':tower.lon}
                pickthem.append(temp)
                distanceList.append(distance)
        
        x = [i for i in range(len(distanceList)) if distanceList[i] == min(distanceList)]
        print('not in TPE')
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
            myGPS = self.client.geolocate(home_mobile_country_code=466, home_mobile_network_code=int(pickthem[x[0]]["net"]), 
                                        radio_type="lte", carrier=Carrier, consider_ip=True, 
                                        cell_towers= cellTower, wifi_access_points=wifiAccessPoint)    
        else:
            myGPS = self.client.geolocate(home_mobile_country_code=466, home_mobile_network_code=None, 
                                        radio_type="lte", carrier=Carrier, consider_ip=True, 
                                        cell_towers= None, wifi_access_points=None)
        return myGPS['location']

    def getBikeStation(self, location) -> dict:        
        #先取得半徑500m的bike station {'lat': 123456, 'lng':4561}
        place_search = self.client.places_nearby(location, keyword="youbike", radius=500)
        #數量太少再擴大搜尋
        if len(place_search['results']) <5:
            place_search = self.client.places_nearby(location, keyword="youbike", radius=1000)
            if len(place_search['results']) ==0:
                
                return "附近沒有YouBike站點"
        
        #依照目前座標給出距離最近的5個站點
        coordinates = []
        for result in place_search['results']:                    
            if result['business_status']=='OPERATIONAL':
                coordinate = result['geometry']['location']
                coordinate['distance'] = haversine(location['lat'], location['lng'], coordinate['lat'], coordinate['lng'])
                coordinates.append(coordinate)
        df = pd.DataFrame(coordinates)
        df = df.sort_values(by='distance')
        
        top5 = df.head(5)
        del top5['distance']
        staInfo = Yb_stn.objects.filter(area_code='00')
        sta_info_df = pd.DataFrame([{'lat': eval(sta.lat), 'lng': eval(sta.lng), 'name_tw': sta.name_tw} for sta in staInfo])
        top5 = top5.merge(sta_info_df, how='left', left_on=['lat', 'lng'], right_on=['lat', 'lng'])
        result = top5.to_dict('records')
        return result
    
    def getDuration(self, location, destination, departuretime= datetime.now()) -> dict:
        # departuretime = datetime.now()
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
    gmap = GoogleMapforUbike('AIzaSyDeEzYq-fwNLOXJu7XzAXU2NgxJW3th_2A')
    myposi = {'lat': 25.048159037642492, 'lng': 121.51707574725279}
    bike = gmap.getBikeStation(myposi)
    print(gmap.getDuration(myposi,bike))
    
               
    
    