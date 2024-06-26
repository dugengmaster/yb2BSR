# 爬蟲與資料庫
## 引言
- 收集政府開放平台的資料，利用數據擷取與分析的方法，作為網頁建立的基礎。

- 要完成YouBike最佳站點推薦，需要收集YouBike開放平台提供的站點車輛即時資料與氣象署開放平台提供的，影響借車因素的相關資料(如雨量氣溫等)，做為建立預測模型的數據來源。

- 本地開發環境使用 `Sqlite3` 資料庫，正式作業環境使用 `Heroku` 提供的 `Postgres` 資料庫

- 使用 `ORM` 語法，做為存取的媒介與方法。

## 公開資料來源

### YouBike開放資料：
1.	area-all：各縣市YouBike客戶服務相關資料

	https://apis.youbike.com.tw/json/area-all.json

2.	station-yb1：YouBike 1各站點即時資料(更新頻率每五分鐘一次)，因YouBike 1只分布於新北，桃園，苗栗三縣市，故目前網站暫不支援，僅作為未來功能擴充之參考。

	https://apis.youbike.com.tw/json/station-yb1.json

3.	station-yb2：YouBike 2各站點即時資料(更新頻率每五分鐘一次)，系統主要之YouBike資料來源。

	https://apis.youbike.com.tw/json/station-yb2.json

### 氣象署開放平台資料:
1. O-A0001-001：自動氣象站-氣象觀測資料， 最短周期可查詢1小時內氣象資料，主要可查詢天氣(如陰晴雨…等)與氣溫。

	https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={Authorization}&format=JSON

2. O-A0002-001：自動雨量站-雨量觀測資料，最短周期可查詢10分鐘內雨量，做為建立模型的即時雨量參數。

	https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization={Authorization}&format=JSON

3. F-C0032-001：一般天氣預報-今明36小時天氣預報， 包含地區、開始和結束時間、天氣現象、降雨機率、最低和最高溫度等資訊。

	https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={Authorization}&format=JSON&elementName=Wx,PoP,MinT,MaxT

### 行事曆資料:
1. 政府行政機關辦公日曆表：新北市提供之行事曆資料，主要用於某日是否為假日之查詢。

	https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/json?size=2000

## 資料庫操作
- 資料庫表格結構定義於專案資料夾中的models.py檔案裡。
- 若有增刪修改資料表，依照Django的作法，更新資料庫程序如下:

	在終端機執行以下指令:
	```terminal
	.\yb2BSR>python manage.py makemigrations
	.\yb2BSR>python manage.py migrate
	```

- 基本的CRUD操作（建立、讀取、更新、刪除），採用Django的ORM語法，Example：
	1. 建立一筆資料：
		```python
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
		```
	2. 讀取一筆或多筆資料：
		```python
			sorex= Yb_yb.objects.filter(dc_time="2024-05-18 00:16")
				sorexc=sorex.count()
				res = "2024-05-18 00:16  "+str(sorexc)+" records"
				print(res)
				print(list(sorex))
		```
	3. 更新資料：
		取出某筆資料後，修改欄位賦予新值，再save即可。
		```python
		sorex.temp_now=new_temp,
		tpe_yb.save()
		```

	4. 刪除資料:
		取出某筆(或多筆)資料後,以delete()的物件方法刪除
		```python
		sorex.delete()
		```

## 資料表設計
- 資料表設計原則:資料表欄位名稱，保持原 `api` 所用的名稱，除 `_id` 與 `python保留字` 衝突無法使用改為 `uid` 外，其餘名稱皆與原 `api` 使用名稱相同。

### mapAPP 所使用之資料表
- 主鍵的設置:以area_code或station_no為連接資料表間的主鍵。
- 正規化:將station-yb1& station-yb2(兩者格式相同，僅記錄之車輛種類[yb1或 yb2]不同)中固定不變的資料分出並置於單一資料表內，以利於降低資料總量與資料庫維護。變動資料則為另一資料表，兩者以 `station_no` 為主鍵互相關聯。
- 資料表(Yb_cnty)內容:

	```python
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
	```

- 資料表(Yb_stn)內容:

	```python
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
	```

- 資料表(Yb_yb)內容:

	```python
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
	```

- 資料表(Tpe_yb or Twn_yb)內容:

	```python
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
	```

### Line_Official_Account_Bot 所使用之資料表
- 資料表(Line_Official_Account_Bot_weatherrecord)內容:
	儲存： 一般天氣預報-今明36小時天氣預報。

	```python
	class WeatherRecord(models.Model):
		location = models.CharField(max_length=50)
		start_time = models.BigIntegerField()
		end_time = models.BigIntegerField()
		wx = models.CharField(max_length=50, null=True, blank=True)
		weather_code = models.CharField(max_length=10, null=True, blank=True)
		pop_value = models.CharField(max_length=10, null=True, blank=True)
		pop_unit = models.CharField(max_length=10, null=True, blank=True)
		min_temp = models.CharField(max_length=10, null=True, blank=True)
		max_temp = models.CharField(max_length=10, null=True, blank=True)
		temp_unit = models.CharField(max_length=5, null=True, blank=True)
	```
- 資料表(Line_Official_Account_Bot_lineuserlocationsinformation)內容:
	儲存： Line 伺服器回傳的使用者資訊。

	```python
	class LineUserLocationsInformation(models.Model):
		user_id = models.CharField(max_length=50)
		timestamp = models.BigIntegerField()
		address = models.CharField(max_length=1024)
		latitude = models.FloatField()
		longitude = models.FloatField()
	```
- 資料表(bike_status)內容:
	儲存： mapfunctionplus 產生的車站狀態資訊。

	```python
	class LineUserOnTimeBikeStatus(models.Model):
		user_id = models.CharField(max_length=50)
		name = models.CharField(max_length=100)
		available_spaces = models.CharField(max_length=10)
		parking_spaces = models.CharField(max_length=10)
		duration = models.CharField(max_length=10)
		msg = models.CharField(max_length=50)
		update_time = models.CharField(max_length=50)

		class Meta:
			db_table = "bike_status"
	```

### web 所使用之資料表
- 資料表(web_userprofile)內容：
	儲存： 網站註冊用戶的個人訊息以及 line 伺服器回傳的 user id, user name。

	```python
	class UserProfile(AbstractBaseUser):
		line_user_id = models.CharField(max_length=100, blank=True, null=True)
		line_name = models.CharField(max_length=150, blank=True, null=True)
		email = models.EmailField(blank=True, null=True)
		username = models.CharField(max_length=150, blank=True, null=True)
		password = models.CharField(max_length=128, blank=True, null=True)
		telecom = models.CharField(max_length=100, blank=True, null=True)
		registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

		objects = UserProfileManager()

		USERNAME_FIELD = 'username'
		REQUIRED_FIELDS = ['line_user_id']

		def __str__(self):
			return self.username

		def has_perm(self, perm, obj=None):
			return True

		def has_module_perms(self, app_label):
			return True

		@property
		def is_staff(self):
			return False
	```
## 爬蟲操作

### mapAPP 所使用之爬蟲
- takeGpsByIP(self,home_mobile_country_code=None,
              home_mobile_network_code=None, radio_type=None, carrier=None,
              consider_ip=None, cell_towers=None, wifi_access_points=None) -> dict
- getstationbike(coordinates, q)
- tpe_cur_rain(q)
- tpe_cur_temp(q)
- tpe_yb_stn()
- tpe_yb_qy(station_no)
- holiday_qy(date,q)

### Line_Official_Account_Bot 所使用之爬蟲
- weather(Authorization: str) -> dict | None
	1. 功能：取得 F-C0032-001 (一般天氣預報-今明36小時天氣預報)之資料
	2. 輸入參數：`Authorization` 用來認證 API 請求的授權憑證或密鑰。
	3. 返回值：如果成功取得資料，則資料型態為 dict 包含地點、開始和結束時間、天氣現象、降雨機率、最低和最高溫度。若失敗則會返回 None。
		```python
		[
			{
				'locationName': '彰化縣',
				'start_time': 1718013600000,
				'end_time': 1718056800000,
				'Wx': '多雲時陰短暫陣雨或雷雨',
				'weather_code': '16',
				'PoP': '30',
				'pop_unit': '百分比',
				'MinT': '27',
				'MaxT': '31',
				'temp_unit': 'C'
			},
		]
		```
	4. 使用 Django ORM 將取得的資料寫入 `Line_Official_Account_Bot_weatherrecord` 資料表。

## 參考資料
- Django models：

	https://docs.djangoproject.com/en/5.0/topics/db/models/