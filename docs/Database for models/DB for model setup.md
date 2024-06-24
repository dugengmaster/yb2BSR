

# YouBike最佳站點推薦資料庫說明
## 1.	引言
### o	收集政府開放平台的資料,利用數據擷取與分析的方法,作為網頁建立的基礎。
### o	要完成YouBike最佳站點推薦,需要收集YouBike開放平台提供的站點車輛即時資料與氣象署開放平台提供的,影響借車因素的相關資料(如雨量氣溫等),做為建立預測模型的數據來源。
### o	使用Django提供的db.sqlite3資料庫(或Heroku提供的Postgres資料庫)搭配ORM語法,做為存取的媒介與方法。
## 2.	系統資料來源
### o	YouBike開放資料:
1.	area-all.json:各縣市YouBike客戶服務相關資料
2.	station-yb1.json: YouBike 1各站點即時資料(更新頻率每五分鐘一次),因YouBike 1只分布於新北,桃園,苗栗三縣市,故目前網站暫不支援,僅作為未來功能擴充之參考。
3.	station-yb2.json: YouBike 2各站點即時資料(更新頻率每五分鐘一次),系統主要之YouBike資料來源。
### o	氣象署開放平台資料:
1.	O-A0002-001json: 自動雨量站-雨量觀測資料,最短周期可查詢10分鐘內雨量,做為建立模型的即時雨量參數。
2.	O-A0001-001.json: 自動氣象站-氣象觀測資料, 最短周期可查詢1小時內氣象資料,主要可查詢天氣(如陰晴雨…等)與氣溫。
### o	行事曆資料:
1.	308dcd75-6434-45bc-a95f-584da4fed251.json: 新北市提供之行事曆資料,主要用於某日是否為假日之查詢。

## 3.	資料模型
### o	資料庫表格結構定義於專案資料夾中的models.py檔案裡。
### o	若有增刪修改資料表,按照Django的作法,更新資料庫程序如下:
####	終端機底下,執行下列二指令:
1.	python manage.py makemigrations
2.	python manage.py migrate

### o	主鍵的設置:以area_code或station_no為連接資料表間的主鍵

## 4.	資料庫設計
### o	資料庫設計原則:資料庫欄位名稱,保持原json檔案所用的名稱,除_id與python保留字衝突無法使用改為uid外,其餘名稱皆與json檔名稱相同。
### o	正規化:將station-yb1& station-yb2(兩者格式相同,僅記錄之車輛種類[yb1或 yb2]不同)中固定不變的資料分出, 置於單一資料表內,以利於降低資料總量與資料庫維護。變動資料則為另一資料表,兩者以station_no為主鍵互相關聯。
### o	資料表(Yb_cnty)內容:

    class Yb_cnty(models.Model):
        uid = models.CharField(max_length=50)
        area_code = models.CharField(max_length=10)
        area_english = models.CharField(max_length=20)
        bike_code = models.CharField(max_length=10)
        station_start = models.IntegerField()
        station_end = models.IntegerField()
        domain = models.CharField(max_length=50)
        is_open = models.IntegerField()
        is_bind = models.IntegerField()
        register_card = models.CharField(max_length=200)
        contact_phone = models.CharField(max_length=200)
        contact_mail = models.CharField(max_length=100)
        ad_mail = models.CharField(max_length=100)
        lat = models.CharField(max_length=20)
        lng = models.CharField(max_length=20)
        ride_count = models.IntegerField()
        visit_count = models.IntegerField()
        updated_at = models.CharField(max_length=20)
        service_phone = models.CharField(max_length=20)
        contact_phone_2 = models.CharField(max_length=200)
        ride_count2 = models.IntegerField()
        lat2 = models.CharField(max_length=20)
        lng2 = models.CharField(max_length=20)
        bike_type = models.CharField(max_length=20)
        area_code_2 = models.CharField(max_length=10)
        area_name_tw = models.CharField(max_length=30)
        area_name_en = models.CharField(max_length=30)

        class Meta:
        db_table = "yb_cnty"

### o	資料表(Yb_stn)內容:

	class Yb_stn(models.Model):
	    area_code = models.CharField(max_length=10)
	    station_no = models.CharField(max_length=20)
	    name_tw = models.CharField(max_length=30)
	    district_tw = models.CharField(max_length=30)
	    address_tw = models.CharField(max_length=50)
	    name_en = models.CharField(max_length=30)
	    district_en = models.CharField(max_length=30)
	    address_en = models.CharField(max_length=50)
	    lat = models.CharField(max_length=20)
	    lng = models.CharField(max_length=20)
	
	    class Meta:
	        db_table = "yb_stn"


### o	資料表(Yb_yb)內容:

	class Yb_yb(models.Model):
	    type = models.IntegerField()
	    status = models.IntegerField()
	    station_no = models.CharField(max_length=20)
	    parking_spaces = models.IntegerField()
	    available_spaces = models.IntegerField()
	    available_spaces_detail = models.CharField(max_length=50)
	    available_spaces_level = models.IntegerField()
	    empty_spaces = models.IntegerField()
	    forbidden_spaces = models.IntegerField()
	    updated_at = models.CharField(max_length=20)
	
	    class Meta:
	        db_table = "yb_yb"

### o	資料表(Tpe_yb or Twn_yb)內容:

	class Tpe_yb(models.Model):
	    station_no = models.CharField(max_length=20)
	    available_spaces = models.IntegerField()
	    isholiday= models.IntegerField()
	    rain_amt=models.FloatField()
	    temp_now=models.FloatField()
	    updated_at = models.CharField(max_length=20)
	    dc_time = models.CharField(max_length=20)
	
	    class Meta:
	        db_table = "tpe_yb"


## 5.	資料庫操作
### o	基本的CRUD操作（建立、讀取、更新、刪除）:
####	採用Django的ORM語法,例子如下:
1.建立一筆資料:

	sorex = Tpe_yb(
	                station_no = data.iloc[i].station_no,
	                available_spaces =data.iloc[i].available_spaces,
	                isholiday=isholyday,
	                temp_now=temp,
	                rain_amt=rainamt,
	                updated_at = data.iloc[i].updated_at,
	                dc_time=dc_time
	                )
	               sorex.save()

2.讀取一筆或多筆資料:
 
    sorex= Yb_yb.objects.filter(dc_time="2024-05-18 00:16")
        sorexc=sorex.count()
        res = "2024-05-18 00:16  "+str(sorexc)+" records"
        print(res)
        print(list(sorex))

3.更新資料:
取出某筆資料後,修改欄位賦予新值,再save即可。

	sorex.temp_now=new_temp,
	tpe_yb.save()

1. 刪除資料:
取出某筆(或多筆)資料後,以delete()的物件方法刪除

    sorex.delete()



