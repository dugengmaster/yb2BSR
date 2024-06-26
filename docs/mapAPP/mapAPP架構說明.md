# mapAPP 架構說明
1. 本文主旨在說明mapAPP的架構

## 主要三個Side program
1. GoogleMap API 地圖應用程式: GoogleMapForUbike.py
2. Machine Learning-SVM 模型產生程式: StationSuggestAlgorism.py
3. 各項爬蟲訊息更新程式: get_current_info.py

## mapAPP.view.py -> function: mapAPP 流程說明
1. 爬蟲抓取當前雨量{function: tpe_cur_rain}、當前溫度{function: tpe_cur_temp}、今日工作日{function: holiday_qy}
2. 取得使用者的GPS座標{function: GoogleMapforUbike('googlemap API token').getgeolocation()}
   1. 判斷使用者是否在台北市，如果不在台北市，將座標自動定位在台北車站
3. 依據使用者座標取得周邊的Ubike站點位置{function: GoogleMapforUbike('googlemap API token').getstationbike("your coordinates")}
4. 將取得的list of bikestations coordinates 轉換成Station number{function: geo_to_No("list of bikestations coordinates")}，從dir/mapAPP/mlmodels 取得各站點的 mlmodels.joblib
5. 將爬蟲取得的資料轉換為input array[hour, isholiday, rainCheck, temperature]，輸入進各站的model預測使用者走路到該站點的時段有沒有車。
   1. model預測得到的結果為1: 回傳msg: 車輛充足
   2. model預測得到的結果為0: 回傳msg: 這時段車輛可能不足，需要等待幾分鐘
6. 最後將資料彙整並傳入mapAPP.html
