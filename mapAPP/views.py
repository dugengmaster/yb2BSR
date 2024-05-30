from django.shortcuts import render
from django.conf import settings
from mapAPP.GoogleMapForUbike import GoogleMapforUbike
from mapAPP.models import LtecelltowerTpe, YbStn
from django.db.models import Q
from django.http import HttpResponse
# Create your views here.


# 顯示有地圖的頁面
def mapAPP(request):
    gmap = GoogleMapforUbike(settings.GOOGLE_MAPS_API_KEY)
    myPosition = gmap.getgeolocation()
    lat_min, lat_max = 24.97619, 25.14582
    lng_min, lng_max = 121.46288, 121.62306
    bikeStation ={}
    tpeStaion = {'lat': 25.048159037642492, 'lng': 121.51707574725279}#台北車站座標
    if (myPosition['lat']<lat_min or myPosition['lat']>lat_max) or (myPosition['lng']<lng_min or myPosition['lng']>lng_max):
        temp = "{lat: 25.048159037642492, lng: 121.51707574725279}"
        msg = "您不在台北市，請使用大眾交通工具移動到台北市"
        bikeStation = gmap.getBikeStation(tpeStaion)
    else:
        temp = "{lat:"+str(myPosition['lat'])+","+"lng:"+str(myPosition['lng'])+'}'
        bikeStation = gmap.getBikeStation(myPosition)
    bikestations = []
    
    for sta in bikeStation:
        change = "{lat:"+str(sta['lat'])+","+"lng:"+str(sta['lng'])+'}'
        bike = {sta['name_tw']: change}
        bikestations.append(bike)
        
    parameter = {"api_key": settings.GOOGLE_MAPS_API_KEY, 'coordinates':temp, 'msg':msg, 'bikeStation':bikestations}
    return render(request, "mapAPP.html", parameter)

def test(request):
    ob = LtecelltowerTpe.objects
    towerList = ob.filter(net__in=['1','97'])
    netlist = [i.lat for i in towerList]
    return HttpResponse(netlist)
#
# 查詢特定站點

# 推薦站點

# 站點分析
