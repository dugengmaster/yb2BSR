import requests
import json
import datetime

agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(agent)

fn1="D:\\LC\\ubike\\raw\\area-all-"+str(datetime.datetime.now())[:16].replace(":","_")+".json"
fn2="D:\\LC\\ubike\\raw\\station-yb1-"+str(datetime.datetime.now())[:16].replace(":","_")+".json"
fn3="D:\\LC\\ubike\\raw\\station-yb2-"+str(datetime.datetime.now())[:16].replace(":","_")+".json"
fn4="D:\\LC\\ubike\\raw\\weather-"+str(datetime.datetime.now())[:16].replace(":","_")+".json"
fn5="D:\\LC\\ubike\\raw\\weather2-"+str(datetime.datetime.now())[:16].replace(":","_")+".json"

fns = [fn1,fn2,fn3,fn4,fn5]

apis = ["https://apis.youbike.com.tw/json/area-all.json","https://apis.youbike.com.tw/json/station-yb1.json",
       "https://apis.youbike.com.tw/json/station-yb2.json","https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=CWA-BA524CBF-8292-4BCA-9CC1-1AFEB8DF80D2&format=JSON",
       "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWA-BA524CBF-8292-4BCA-9CC1-1AFEB8DF80D2&format=JSON"]
for index, api in enumerate(apis):
    response = session.get(api)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        with open(fns[index], "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)