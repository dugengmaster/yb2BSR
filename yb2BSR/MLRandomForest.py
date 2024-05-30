# -*- coding: utf-8 -*-
"""
Created on Wed May 22 10:00:04 2024

@author: 88698
"""

import sqlite3 as sql
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression
import seaborn as sns
from datetime import datetime
from GoogleMapForUbike import GoogleMapforUbike 
import time


def stationSuggest(list_of_station):
    
    db_path = r'D:\pythonproject\GooglemapForUbike/db.sqlite3'
    errorstation = []
    with sql.connect(db_path) as db:
        for i in range(len(list_of_station)):
            query = "SELECT station_no FROM yb_stn WHERE area_code='00' AND lat='"+str(list_of_station[i]['lat'])+"' AND lng='"+str(list_of_station[i]['lng'])+"'"
            df = pd.read_sql_query(query, db)
            list_of_station[i]['station_no']=df.iloc[0][0]
       
    for i in range(len(list_of_station)):        
        try:
            with sql.connect(db_path) as db:
               
                query = "SELECT * FROM tpe_yb WHERE station_no='"+list_of_station[i]['station_no']+"' AND updated_at BETWEEN '2024-05-13 04:00:00' AND '2024-05-17 23:55:00'"
                df = pd.read_sql_query(query, db)
                
            
                cur = db.cursor()
                cur.execute("PRAGMA table_info(tpe_yb)")
                columns_info = cur.fetchall()
                columns = [info[1] for info in columns_info]
                
            
                df.columns = columns
                #轉換時間格式
                df['updated_at'] = pd.to_datetime(df['updated_at'])
                df = df.drop_duplicates(subset=['updated_at'])
                    
                #將時間變成小時，分鐘變成小數點，例如: 16.5 是下午四點半
                df['hour'] = df['updated_at'].dt.hour + round((df['updated_at'].dt.minute)/60, 2)
                # df['minute'] = (df['updated_at'].dt.minute)/60
                #新增工作日，目前只有一周資料所以用不到
                df['DayofWeek'] = df['updated_at'].dt.dayofweek
                #計算站點的車輛流動率
                df['timediff'] = df['hour'].diff()*60
                df['bikediff'] = df['available_spaces'].diff()
                df['flowrate'] = df['bikediff']/df['timediff']
                df = df.dropna()
                #判斷站點三分鐘後有沒有車
                df['checknum'] = df['available_spaces']+round(df['flowrate']*3,0)
                df.loc[df['checknum'] > 0, 'haveBike'] = 1
                df.loc[df['checknum'] <= 0, 'haveBike'] = 0
                X = df[['hour']]
                y = df['haveBike']
                
                # df = df[['available_spaces', 'hour']]
                # df.plot(kind='line',y='available_spaces', x='updated_at', color='blue')
                # plt.plot(df['updated_at'], df['available_spaces'].rolling(6).mean(), color='yellow')
                # plt.show()
                # print(df.info())
                # print(df.describe())
                
                # sns.pairplot(df)
                # plt.show()
                
                # df=df[['available_spaces', 'hour', 'flowrate', 'haveBike']]
                # sns.heatmap(df.corr(), annot=True)
                # 建模
                x_train, x_test, y_train, y_test = train_test_split(X,y , test_size=0.3)
               
                model = RandomForestClassifier(n_estimators=100)
                # model = LogisticRegression(C=0.01)
                model.fit(x_train, y_train)
                   
                y_pred = model.predict(x_test)
                # 评估模型
                print("Accuracy:", accuracy_score(y_test, y_pred))
                print(classification_report(y_test, y_pred))
                
                list_of_station[i]['model'] = [model, accuracy_score(y_test, y_pred)]
                # count+=1
        except:
            errorstation.append(list_of_station[i]['station_no'])
            print("有問題的站別:",list_of_station[i]['station_no'])
            pass
    now = datetime.now()
    time = np.reshape((now.hour + now.minute/60), (1,1))
    temp = []
    for x in  range(len(list_of_station)):
        print(list_of_station[x]['model'][0].predict(time)[0])              
        if int(list_of_station[x]['model'][0].predict(time)[0]) ==1:
            temp.append(list_of_station[x])

    bestone = min(temp, key=lambda x: x['time_cost'])
    return bestone
start = time.time()
gmap = GoogleMapforUbike('AIzaSyDeEzYq-fwNLOXJu7XzAXU2NgxJW3th_2A')
lcc = {'lat':25.01698661283618, 'lng':121.53187622210271}
ubikeCoord = gmap.getBikeStation(lcc)
ubikeDuration = gmap.getDuration(lcc, ubikeCoord)  
print(stationSuggest(ubikeDuration))
end = time.time()   
print(end-start)          