from django.shortcuts import render
from django.conf import settings
from mapAPP.GoogleMapForUbike import GoogleMapforUbike
from mapAPP.models import LtecelltowerTpe, Yb_stn
from django.db.models import Q
from django.http import HttpResponse
import os
import time
from datetime import datetime
import pandas as pd
import re
import requests
import json
from mapAPP.StationSuggestAlgorism import minuteChange, geo_to_No
from mapAPP.get_current_info import tpe_cur_rain, tpe_cur_temp, holiday_qy, getstationbike
import numpy as np
import joblib
import threading
import queue
# Create your views here.


# 顯示有地圖的頁面
def mapAPP(request):
    start = time.time()
    now = datetime.now()

    #多工緒處理爬蟲
    q = queue.Queue()
    rainthread = threading.Thread(target=tpe_cur_rain, args=(q,))
    tempthread = threading.Thread(target=tpe_cur_temp, args=(q,))
    holidaythread = threading.Thread(target=holiday_qy, args=(now.date().strftime("%Y%m%d"), q))
    rainthread.start()
    tempthread.start()
    holidaythread.start()

    #取得使用者GPS
    gmap = GoogleMapforUbike(settings.GOOGLE_MAPS_API_KEY)
    myPosition = gmap.getgeolocation()

    #台北市的經緯度範圍，不再這範圍內的人，會定位在台北車站，並以定位點為中心取得周邊的Ubike站點
    lat_min, lat_max = 24.97619, 25.14582
    lng_min, lng_max = 121.46288, 121.62306
    bikeStation ={}
    tpeStaion = {'lat': 25.048159037642492, 'lng': 121.51707574725279}#台北車站座標
    if (myPosition['lat']<lat_min or myPosition['lat']>lat_max) or (myPosition['lng']<lng_min or myPosition['lng']>lng_max):
        temp = "{lat: 25.048159037642492, lng: 121.51707574725279}"
        msg = "您不在台北市，請使用大眾交通工具移動到台北市"
        bikeStation = gmap.getBikeStation(tpeStaion)
        myPosition = tpeStaion
    else:
        temp = "{lat:"+str(myPosition['lat'])+","+"lng:"+str(myPosition['lng'])+'}'
        bikeStation = gmap.getBikeStation(myPosition)

    #多工爬蟲抓取站點即時資料
    statusthread = threading.Thread(target=getstationbike, args=(bikeStation,q))
    statusthread.start()

    #從./mlmodles 取得各站點的預測模型
    station_no = geo_to_No(bikeStation)
    models = []
    for x in station_no:
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'mlmodels', f'model{x}.joblib')
            model = joblib.load(model_path)
            models.append(model)
        except:
            pass

    #取回各個爬蟲的回傳值
    rainthread.join()
    tempthread.join()
    holidaythread.join()
    statusthread.join()
    raincheck = q.get()
    temperature = q.get()
    isholiday = q.get()
    bikeStatus = q.get()

    #取得走路到各站點需要花費的時間，並轉換為時段
    bikestations = []
    duration = gmap.getDuration(myPosition,bikeStation)
    timeSwap = [minuteChange(dur['time_cost']/60 + now.minute) for dur in duration]

    #輸入參數hour(00.00), isholiday(0,1), rainCheck(0,1), temp_now
    X_input = [pd.DataFrame([{'hour':(now.hour+timeSwap[i]), 'isholiday':isholiday, 'rainCheck':raincheck, 'temp_now':temperature}]) for i in range(len(timeSwap))]
    have_bike = [models[j].predict(X_input[j]) for j in range(len(timeSwap))]

    #訓練結果轉換為msg
    for i in range(len(bikeStatus)):
        if have_bike[i]==1:
            bikeStatus[i]['msg']="車輛充足"
            bikeStatus[i]['duration'] = round(duration[i]['time_cost']/60,1)
        else:
            bikeStatus[i]['msg']="這時段車輛可能不足，需要等待幾分鐘"
            bikeStatus[i]['duration'] = round(duration[i]['time_cost']/60,1)

    #轉換地理座標格式，JS可讀取格式
    for sta in bikeStation:
        change = "{lat:"+str(sta['lat'])+","+"lng:"+str(sta['lng'])+'}'
        bike = {sta['name_tw']: change}
        bikestations.append(bike)

    #資料彙整成dict傳入html
    parameter = {
        "api_key": settings.GOOGLE_MAPS_API_KEY,
        'coordinates':temp,
        'msg':msg,
        'bikeStation':bikestations,
        'bikeStatus':bikeStatus
    }
    end = time.time()
    return render(request, "mapAPP.html", parameter)


# 查詢特定站點

# 推薦站點

# 站點分析





# by C F Chu for yb data collection and yb model setup

# from django.shortcuts import render
# from django.shortcuts import render,redirect

# from mapAPP.models import Yb_cnty, Yb_stn,Yb_yb,Tpe_yb

# # Create your views here.
# global dcflg
# dcflg=0

# def yb_cnty_upd(request):
#     fn="D:\\LC\\ubike\\area-all-2024-05-13 02_40.json"
#     data=pd.read_json(fn)
#     #print(data)
#     #print("len",len(data))
#     # for i in range(len(data)):
#     #     print(data.iloc[i]._id)

#     # Creating an entry
#     for i in range(len(data)):
#         print(data.iloc[i])
#         yb_cnty = Yb_cnty(
#         uid = data.iloc[i]._id,
#         area_code = data.iloc[i].area_code,
#         area_english = data.iloc[i].area_english,
#         bike_code = data.iloc[i].bike_code,
#         station_start = data.iloc[i].station_start,
#         station_end = data.iloc[i].station_end,
#         domain = data.iloc[i].domain,
#         is_open = data.iloc[i].is_open,
#         is_bind = data.iloc[i].is_bind,
#         register_card = data.iloc[i].register_card,
#         contact_phone = data.iloc[i].contact_phone,
#         contact_mail = data.iloc[i].contact_mail,
#         ad_mail = data.iloc[i].ad_mail,
#         lat = data.iloc[i].lat,
#         lng = data.iloc[i].lng,
#         ride_count = data.iloc[i].ride_count,
#         visit_count = data.iloc[i].visit_count,
#         updated_at = data.iloc[i].updated_at,
#         service_phone = data.iloc[i].service_phone,
#         contact_phone_2 = data.iloc[i].contact_phone_2,
#         ride_count2 = data.iloc[i].ride_count2,
#         lat2 = data.iloc[i].lat2,
#         lng2 = data.iloc[i].lng2,
#         bike_type = data.iloc[i].bike_type,
#         area_code_2 = data.iloc[i].area_code_2,
#         area_name_tw = data.iloc[i].area_name_tw,
#         area_name_en = data.iloc[i].area_name_en
#             )

#         yb_cnty.save()

#     # Read ALL entries

#     # objects = Dreamreal.objects.all()
#     res = 'Saving all entries in the '+fn+ ' <br>'

#     # for elt in objects:
#     #     res += elt.name + "<br>"

#     # #Read a specific entry:
#     # sorex = Dreamreal.objects.get(name="cfchu3")
#     # print("sorex:",sorex)
#     # res += 'Printing One entry <br>'
#     # res += sorex.name

#     # Delete an entry
#     # res += '<br> Deleting an entry <br>'
#     # sorex.delete()

#     # # Update
#     # dreamreal = Dreamreal(
#     #     website="www.google.com",
#     #     mail="cfchu04@google.com.com",
#     #     name="cfchu3",
#     #     phonenumber="0911123456"
#     # )

#     # dreamreal.save()

#     # res += 'Updating entry<br>'

#     # dreamreal = Dreamreal.objects.get(name='cfchu3')
#     # dreamreal.name = 'mary'
#     # dreamreal.password = '111222'
#     # dreamreal.save()

#     return HttpResponse(res)


# def yb_stn_upd(request):
#     fn="D:\\LC\\ubike\\station-yb2-2024-05-15 04_49.json"
#     data=pd.read_json(fn)
#     #print(data)
#     #print("len",len(data))
#     # for i in range(len(data)):
#     #     print(data.iloc[i]._id)

#     # Creating an entry
#     for i in range(len(data)):
#         print(data.iloc[i].station_no)
#         yb_stn = Yb_stn(
#         area_code = data.iloc[i].area_code,
#         station_no = data.iloc[i].station_no,
#         name_tw = data.iloc[i].name_tw,
#         district_tw = data.iloc[i].district_tw,
#         address_tw = data.iloc[i].address_tw,
#         name_en = data.iloc[i].name_en,
#         district_en = data.iloc[i].district_en,
#         address_en = data.iloc[i].address_en,
#         lat = data.iloc[i].lat,
#         lng = data.iloc[i].lng
#             )

#         yb_stn.save()


#     res = 'Saving all entries in the '+fn+ ' <br>'



#     return HttpResponse(res)


# def daily_dc(request):
#     global dcflg
#     if dcflg==0:
#         dcflg=1
#         yb_yb_upd()

#     res = 'Saving all entries done <br>'
#     return HttpResponse(res)

# def yb_yb_upd(): #only for yb1&yb2 processing
#     rawfolder="D:\\LC\\ubike\\raw"
#     sample_tree=os.walk(rawfolder)
#     #print(list(sample_tree))
#     for dirname,subdir,files in sample_tree:
#         print("檔案路徑:",dirname)
#         print("目錄串列:",subdir)
#         print("檔案串列:",files)
#         print()

#     for f in range(0,len(files),2):
#         fn=files[f]
#         rawfn=rawfolder+"\\"+fn
#         data=pd.read_json(rawfn)
#         print("processing:",rawfn,".....")


#         # Creating an entry
#         for i in range(len(data)):
#             #print(data.iloc[i].station_no)
#             yb_yb = Yb_yb(
#             type = data.iloc[i].type,
#             status = data.iloc[i].status,
#             station_no = data.iloc[i].station_no,
#             parking_spaces = data.iloc[i].parking_spaces,
#             available_spaces = data.iloc[i].available_spaces,
#             available_spaces_detail = data.iloc[i].available_spaces_detail,
#             available_spaces_level = data.iloc[i].available_spaces_level,
#             empty_spaces = data.iloc[i].empty_spaces,
#             forbidden_spaces = data.iloc[i].forbidden_spaces,
#             updated_at = data.iloc[i].updated_at
#                 )

#             yb_yb.save()

# def tpe_dc(request):
#     global dcflg
#     if dcflg==0:
#         dcflg=1
#         tpe_yb_upd2()

#     res = 'Saving all entries done <br>'
#     return HttpResponse(res)


# def tpe_yb_upd():
#     holidayL=["2024-05-18","2024-05-19"]

#     staL= Yb_stn.objects.filter(area_code="00") #Taipei city
#     # print(staL)
#     # print(len(staL))

#     for i in staL:
#         ybL= Yb_yb.objects.filter(station_no=i.station_no)
#         print(i.station_no)
#         print(len(ybL))
#         #
#         for j in ybL:
#             if j.updated_at[:10]=="2024-05-13":
#                 rain_amt=14
#             elif j.updated_at[:10]=="2024-05-14":
#                 rain_amt=0.5
#             else:
#                 rain_amt=0

#             if j.updated_at[:10] in holidayL:
#                 isholyday=1
#             else:
#                 isholyday=0

#             tpe_yb = Tpe_yb(
#             station_no = j.station_no,
#             available_spaces =j.available_spaces,
#             isholiday=isholyday,
#             rain_amt=rain_amt,
#             updated_at = j.updated_at
#             )

#             tpe_yb.save()


#     #return HttpResponse("tpe_yb_upd is done!")


# # get real time rain in 10min.
# def get_rain(fn):
#     # fn="D:\\LC\\ubike\\weather-2024-05-24 00_52.json"
#     data=pd.read_json(fn)

#     for i in data["records"]["Station"]:
#         #if i["GeoInfo"]["CountyName"]=="臺北市":
#         # if i["GeoInfo"]["TownName"]=="松山區":
#         #     print(i["StationName"],i["GeoInfo"]["CountyName"],i["GeoInfo"]["TownName"],end="")
#         #     print(" rain:",i["RainfallElement"]["Now"]["Precipitation"])
#         if i["StationName"]=="松山":
#             # print(i["StationName"],i["GeoInfo"]["CountyName"],i["GeoInfo"]["TownName"],end="")
#             # print(" rain:",i["RainfallElement"]["Now"]["Precipitation"])
#             return i["RainfallElement"]["Past10Min"]["Precipitation"]

# # get real time temperature in 1 hour.
# def get_temp(fn):
#     if "2024-05-24 00" in fn: #due to no weather2 file before 2024-05-24 01
#         return 24.1

#     data=pd.read_json(fn)

#     for i in data["records"]["Station"]:
#         #if i["GeoInfo"]["CountyName"]=="臺北市":
#         # if i["GeoInfo"]["TownName"]=="松山區":
#         #     print(i["StationName"],i["GeoInfo"]["CountyName"],i["GeoInfo"]["TownName"],end="")
#         #     print(" rain:",i["RainfallElement"]["Now"]["Precipitation"])
#         if i["StationName"]=="松山":
#             # print(i["StationName"],i["GeoInfo"]["CountyName"],i["GeoInfo"]["TownName"],end="")
#             # print(" rain:",i["RainfallElement"]["Now"]["Precipitation"])
#             return i["WeatherElement"]["AirTemperature"]





# def tpe_yb_upd2():
#     #exclude=["00","01","02","03","04"] #exclude 00~04 o'clock
#     holidayL=["2024-05-18","2024-05-19","2024-05-25","2024-05-26","2024-06-01","2024-06-02"]
#     may23temp={"00": "24.1","01": "24.1", "02": "24.1", "03": "24.0", "04": "24.0", "05": "24.0", "06": "24.1",
#                "07": "24.4", "08": "24.7", "09": "25.6", "10": "26.1", "11": "26.0", "12": "25.6",
#                "13": "25.9", "14": "26.4", "15": "26.4", "16": "25.4", "17": "24.9", "18": "24.4",
#                  "19": "24.3", "20": "24.3", "21": "24.2", "22": "24.3", "23": "24.2", "24": "24.1"}

#     staO= Yb_stn.objects.filter(area_code="00") #Taipei city
#     print(staO)
#     staL=[]
#     for i in staO:
#         print(i.station_no,end=" ")
#         staL.append(i.station_no)
#     print(len(staL))
#     # input()

#     files=[]
#     rawfolder="D:\\LC\\ubike\\raw"
#     sample_tree=os.walk(rawfolder)
#     #print(list(sample_tree))
#     for dirname,subdir,rawfiles in sample_tree:
#         print("檔案路徑:",dirname)
#         print("目錄串列:",subdir)
#         print("檔案串列:",rawfiles)
#         print()

#     for i in rawfiles:
#         if i[:11]=="station-yb2":
#             # if i[23:25] not in exclude:
#             files.append(i)

#     print(files)
#     #input()

#     for f in range(len(files)):
#         fn=files[f]
#         dc_time=fn[12:28].replace("_",":")
#         print("dc_time",dc_time,"\t",end="")
#         # input()
#         rawfn=rawfolder+"\\"+fn
#         rainfn=rawfn.replace("station-yb2","weather")
#         rainamt=get_rain(rainfn)
#         print("rain amount:",rainamt,"\t",end="")

#         if fn[12:22]=="2024-05-23":
#             temp=may23temp[fn[23:25]]
#         else:
#             tempfn=rawfn.replace("station-yb2","weather2")
#             temp=get_temp(tempfn)
#         print("temp:",temp,"\t",end="")


#         if fn[12:22] in holidayL:
#             isholyday=1
#         else:
#             isholyday=0
#         print("isholyday:",isholyday)
#         #input()

#         data=pd.read_json(rawfn)
#         print("processing:",rawfn,".....")
#         #print(data)
#         # break

#         for i in range(len(data)):
#             if str(data.iloc[i].station_no)[0:4]=="5001":
#                 tpe_yb = Tpe_yb(
#                 station_no = data.iloc[i].station_no,
#                 available_spaces =data.iloc[i].available_spaces,
#                 isholiday=isholyday,
#                 temp_now=temp,
#                 rain_amt=rainamt,
#                 updated_at = data.iloc[i].updated_at,
#                 dc_time=dc_time
#                 )
#                 tpe_yb.save()

#     #  # Creating an entry
#     #     for i in range(len(data)):
#     #         #print(data.iloc[i].station_no)
#     #         yb_yb = Yb_yb(
#     #         type = data.iloc[i].type,
#     #         status = data.iloc[i].status,
#     #         station_no = data.iloc[i].station_no,
#     #         parking_spaces = data.iloc[i].parking_spaces,
#     #         available_spaces = data.iloc[i].available_spaces,
#     #         available_spaces_detail = data.iloc[i].available_spaces_detail,
#     #         available_spaces_level = data.iloc[i].available_spaces_level,
#     #         empty_spaces = data.iloc[i].empty_spaces,
#     #         forbidden_spaces = data.iloc[i].forbidden_spaces,
#     #         updated_at = data.iloc[i].updated_at
#     #             )

#     #         yb_yb.save()

#     # for i in staL:
#     #     ybL= data[["station_no"==i.station_no]]
#     #     break
#     # print(ybl)
#     #     print(i.station_no)
#     #     print(len(ybL))
#     #     #
#     #     for j in ybL:
#     #         if j.updated_at[:10]=="2024-05-13":
#     #             rain_amt=14
#     #         elif j.updated_at[:10]=="2024-05-14":
#     #             rain_amt=0.5
#     #         else:
#     #             rain_amt=0

#     #         if j.updated_at[:10] in holidayL:
#     #             isholyday=1
#     #         else:
#     #             isholyday=0

#     #         tpe_yb = Tpe_yb(
#     #         station_no = j.station_no,
#     #         available_spaces =j.available_spaces,
#     #         isholiday=isholyday,
#     #         rain_amt=rain_amt,
#     #         updated_at = j.updated_at
#     #         )

#     #         tpe_yb.save()


#     return HttpResponse("tpe_yb_upd is done!")


# def data_quy(request):
#     stn_no="500101001"
#     objects = Tpe_yb.objects.filter(station_no=stn_no)
#     res = 'Printing all Dreamreal entries for:'+stn_no+' <br>'

#     for elt in objects:
#         if elt.station_no==stn_no:
#             print(elt.available_spaces,end=" ")

#     print(len(objects))

#     #res += elt.name + "<br>"
#     return HttpResponse(res)


# def crudops(request):
#     # Creating an entry

#     # dreamreal = Dreamreal(
#     #     website="www.google.com",
#     #     mail="cfchu04@google.com.com",
#     #     name="cfchu2",
#     #     phonenumber="0911222333"
#     # )

#     # dreamreal.save()

#     # Read ALL entries

#     # objects = Dreamreal.objects.all()
#     # res = 'Printing all Dreamreal entries in the DB : <br>'

#     # for elt in objects:
#     #     res += elt.name + "<br>"

#     # #Read a specific entry:
#     sorex= Yb_yb.objects.filter(updated_at>"2024-05-18 00:15:20")
#     sorexc=sorex.count()
#     res = "2024-05-18 00:15:20  "+str(sorexc)+" records"
#     print(res)
#     print(list(sorex))
#     # print("sorex:",sorex)
#     # res += 'Printing One entry <br>'
#     # res += sorex.name

#     # Delete an entry
#     # res += '<br> Deleting an entry <br>'
#     # sorex.delete()

#     # # Update
#     # dreamreal = Dreamreal(
#     #     website="www.google.com",
#     #     mail="cfchu04@google.com.com",
#     #     name="cfchu3",
#     #     phonenumber="0911123456"
#     # )

#     # dreamreal.save()

#     # res += 'Updating entry<br>'

#     # dreamreal = Dreamreal.objects.get(name='cfchu3')
#     # dreamreal.name = 'mary'
#     # dreamreal.password = '111222'
#     # dreamreal.save()

#     return HttpResponse(res)
