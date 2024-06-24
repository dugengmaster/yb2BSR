### 目錄
# 1. 概述
# 2. 環境設置
# 3. 匯入庫
# 4. 函數和Class定義
## 4.1. haversine 函數
## 4.2. precisionmatch 函數
## 4.3. GoogleMapforUbike Class
### 4.3.1. init 屬性設置
### 4.3.2. getgeolocation 方法
### 4.3.3. getBikeStation 方法
### 4.3.4. getDuration 方法

## 概述
`GoogleMapforUbike` 程式旨在通過 `Google Maps API` 和 `Django` 框架，提供使用者當前地理位置的 YouBike 站點信息以及步行時間估算。

## 環境設置
在開始使用這段代碼之前，需要進行以下環境設置：
# 1. 安裝 Python 3.x。
# 2. 安裝 Django 框架。
# 3. 確保已安裝所需的第三方庫，如 `googlemaps`, `pandas`, `numpy` 等。

### 安裝指引
使用 `pip` 安裝所需庫：
```sh
pip install django googlemaps pandas numpy
```
## 匯入函式庫
匯入專案所需的第三方函式庫和 `Django` 模型
```python
import googlemaps as gmap
import pandas as pd
import math
import uuid
from datetime import datetime
import time
from mapAPP.models import LtecelltowerTpe, Yb_stn2
from django.db.models import Q
import time
import numpy as np
```
## 函數和Class定義
# haversine
`haversine` 函數用於計算兩個地理坐標之間的距離。
```python
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
    #單位公里
    distance = R*c*1000
    return distance
```
# precisionmatch
`precisionmatch` 函數比較兩個浮點數在指定精度範圍內是否相等。
```python
def precisionmatch(a,b,precision):
for i in range(10,precision,-1):
    if round(a,i)== round(b,i):
        return True
else:
    return False
```
# Class GoogleMapforUbike
該Class包含多個方法，用於與 `Google Maps API` 以及資料庫交互並獲取 YouBike 站點資訊。
# 1. __init__ 屬性定義
```python
def __init__(self, key):
        #使用API token 啟用Google map API
        self.client = gmap.Client(key=key)
        #提取資料庫中的電信基地台資訊表
        self.lteCelltower = LtecelltowerTpe.objects.all()
```
# 2. getgeolocation
使用`Google map API`取得使用者座標位置，藉由輸入最近的電信基地台資訊增加座標定位精確度。
```python
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
            myGPS = self.client.geolocate(home_mobile_country_code=466, home_mobile_network_code=int(pickthem[x[0]]["net"]),
                                        radio_type="lte", carrier=Carrier, consider_ip=True,
                                        cell_towers= cellTower, wifi_access_points=wifiAccessPoint)
        else:
            myGPS = self.client.geolocate(home_mobile_country_code=466, home_mobile_network_code=None,
                                        radio_type="lte", carrier=Carrier, consider_ip=True,
                                        cell_towers= None, wifi_access_points=None)
        return myGPS['location']
```
# 3. getBikeStation
獲取用戶位置周圍的 YouBike 站點信息。
```python
def getBikeStation(self, location) -> dict:
    """
    獲取用戶位置周圍的 YouBike 站點信息

    參數：
    location (dict): 用戶當前地理位置

    返回：
    dict: 最近的 YouBike 站點信息
    """
    staInfo = Yb_stn2.objects.all()#filter(area_code='00')
        sta_info_df = pd.DataFrame([{'lat': float(sta.lat), 'lng': float(sta.lng), 'name_tw': sta.name_tw} for sta in staInfo])
        sta_info_df = sta_info_df.drop_duplicates(subset=['name_tw'])
        sta_info_df['distance']=sta_info_df.apply(lambda row: haversine(location['lat'], location['lng'], row['lat'], row['lng']), axis=1)
        sta_info_df = sta_info_df.sort_values(by='distance')
        sta_info_df = sta_info_df.head(5)
        del sta_info_df['distance']
        result = sta_info_df.to_dict('records')
        return result
```
# 3. getDuration
取得從使用者位置走路到各個目的地所花費的時間。
```python
def getDuration(self, location, destination) -> dict:
        departuretime = datetime.now()
        matrix = self.client.distance_matrix(location, destination, mode='walking', units='metrics', departure_time=departuretime)
        for index, coor in enumerate(destination):
            coor['time_cost'] = matrix['rows'][0]['elements'][index]['duration']['value']
        return destination
```