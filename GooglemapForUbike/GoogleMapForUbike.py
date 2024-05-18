# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:14:59 2024

@author: 88698
"""

import googlemaps as gmap
import pandas as pd
import math
import uuid
from datetime import datetime


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
        self.lteCelltower = pd.read_csv("CellTower LTE.csv")
        
    def getgeolocation(self, Carrier="中華電信"):
        #先取得粗略的GPS定位
        gps = self.client.geolocate()
        carrier = {'1':"遠傳電信", "5":"遠傳電信","89":"台灣大哥大","92":"中華電信","97":"台灣大哥大"}
        Net = []
        for key, value in carrier.items():
            if value == Carrier: Net.append(int(key))
        towerList = 0
        if len(Net) >1:
            towerList = self.lteCelltower[(self.lteCelltower['net']==Net[0]) | (self.lteCelltower['net']==Net[1])]
        else:
            towerList = self.lteCelltower[self.lteCelltower['net']==Net[0]]
        pickthem = []
        distanceList= []
        lat1, lon1 = gps["location"]["lat"], gps["location"]["lng"]
        #從表裡面找到最近的基地台資訊
        for i in range(len(towerList)):
            distance = haversine(lat1, lon1, towerList.iloc[i]["lat"], towerList.iloc[i]["lon"])
            if distance <= 1000:
                
                pickthem.append(dict(towerList.iloc[i]))
                distanceList.append(distance)
        
        x = [i for i in range(len(distanceList)) if distanceList[i] == min(distanceList)]
        print('x:', x)
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
        return myGPS['location']

    def getBikeStation(self, location):        
        #先取得半徑500m的bike station
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
        return [dict(top5.iloc[i]) for i in range(len(top5.index))]
    
    def getDuration(self, location, destination, departuretime= datetime.now()):
        # departuretime = datetime.now()
        matrix = self.client.distance_matrix(location, top5, mode='walking', units='metrics', departure_time=departuretime)
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
    #輸入API啟用googlemapAPI
    test = GoogleMapforUbike('你的Google map API-key')
    #取得目前的GPS座標
    location = test.getgeolocation()
    #取得附近最近距離的五個站點座標
    top5 = test.getBikeStation(location)
    #取得附近最近距離的五個站點座標及走路前往的時間
    matrix = test.getDuration(location, top5)
    
    
               
    
    