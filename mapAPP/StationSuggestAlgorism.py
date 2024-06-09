# -*- coding: utf-8 -*-
"""
Created on Wed May 22 10:00:04 2024

@author: 88698
"""

import sqlite3 as sql
import pandas as pd
import matplotlib.pyplot as plt
import os
import django
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yb2BSR.settings')

# 初始化 Django
django.setup()
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import  classification_report, accuracy_score
from sklearn.svm import SVC
import seaborn as sns
from datetime import datetime
from mapAPP.models import Tpe_yb, Yb_stn
from django.db.models import Q   

def minuteChange(minute) -> float:
    min_div = 0.083333333333333 #60/12
    level = round(((minute/60)//min_div)*min_div,10)
    return level
def intomodel(list_of_station) -> list:
    ybinfo = Yb_stn.objects.all()
    stationnumbers = []
    for i in range(len(list_of_station)):
        statioNo = ybinfo.filter(Q(lat=list_of_station[i]['lat']) | Q(lng=list_of_station[i]['lng']))
        if statioNo.exists:
            for sta in statioNo:
                stationnumbers.append(sta.station_no)                
        else:
            print('coordinate error')
    models = []
    for number in stationnumbers:
        print(number)
        try:
            table = Tpe_yb.objects.filter(Q(station_no=number) & Q(updated_at__range=('2024-05-23 00:00:00','2024-05-30 02:55:00')))
            
            df = pd.DataFrame([{'station_no':info.station_no, 'available_spaces':info.available_spaces, 'isholiday':info.isholiday, 'rain_amt':info.rain_amt, 'dc_time':info.dc_time, 'temp_now':info.temp_now} for info in table])
            # print(df['dc_time'])
            df['dc_time'] = pd.to_datetime(df['dc_time'])
            df = df.drop_duplicates(subset=['dc_time'])
        
            #將時間變成小時，分鐘變成小數點，例如: 16.5 是下午四點半    
            df['hour'] = df['dc_time'].dt.hour + minuteChange(df['dc_time'].dt.minute)
            #取得時段
            timeSep = list(set(df['hour']))
            #建立所有時間的平均量及標準差並畫出圖表
            avglist = {'time': timeSep, 'avgs': [], 'std':[]}
            for i in timeSep:
                avg = round(df[(df['hour']==i)]['available_spaces'].sum()/df[(df['hour']==i)]['available_spaces'].count(), 2)
                std = round(df[df['hour']==i]['available_spaces'].std(),2)
                avglist['avgs'].append(avg)
                avglist['std'].append(std)
            avgs= pd.DataFrame(avglist).sort_values(by='time').reset_index(drop=True)
            #取得一個標準差的下限值，低於0的值給0
            avgs['bLimit'] = avgs['avgs']-avgs['std']
            avgs.loc[avgs['bLimit'] <1, 'bLimit'] = 0
            #畫圖
            # avgs.plot(kind='line', x='time', y='avgs')
            # plt.plot(avgs['time'], avgs['bLimit'])
            # plt.grid()
            # plt.show()
            #將下限值放值於大表
            for i in avgs.index:
                df.loc[df['hour']==avgs.iloc[i]['time'], 'bLimit'] = avgs.iloc[i]['bLimit']
                
            #分為兩類，下限值低於2或是現有車輛數低於3台為一類，表用量緊張
            df.loc[(df['bLimit'] <= 2) | (df['available_spaces'] <= 3), 'haveBike'] = 0
            #下限值大於2且車輛數大於3台為一類，表示車量充裕
            df.loc[(df['available_spaces'] > 3) & (df['bLimit'] > 2), 'haveBike'] = 1
            
            #定義會影響騎車的雨量
            rain_check = 0.3/6 #微雨界定值0.3mm/6min
            df['raindiff']=df['rain_amt'].diff()
            df.loc[df['raindiff']>rain_check*5, 'rainCheck']=1
            df.loc[df['raindiff']<=rain_check*5, 'rainCheck']=0
            df = df.fillna(0)
            
            X = df[['hour', 'isholiday', 'rainCheck', 'temp_now']]
            
            y = df['haveBike']
            
            # 建模
            x_train, x_test, y_train, y_test = train_test_split(X,y , test_size=0.3)
            
            model = SVC(kernel='rbf', C=1E5)  
            model.fit(x_train, y_train)
            temp = {'stationno':number, 'model':model }
            models.append(temp)
            print(number, 'OK')
        except:
            pass
    return models    
        # y_pred = model.predict(x_test)
        # # 评估模型
        # print("Accuracy:", accuracy_score(y_test, y_pred))
        # print(classification_report(y_test, y_pred))

        
        # now = datetime.now()
        # hour = now.hour+ minuteChange(now.minute + 5)
        # rain = eval(input("rainy?: 0 or 1 :"))
        # hoilday = eval(input("holiday? 0 or 1 :"))
        # to = [hour, hoilday, rain, 25]
        # x = np.reshape(to, (1,len(to)))
        # msg = ["車量吃緊，需要等待幾分鐘", "車量充裕，無需等待"]
        # print(msg[int(model.predict(x))])

       