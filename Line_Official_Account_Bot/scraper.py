import requests
from datetime import datetime

agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(agent)

def weather(Authorization: str) -> dict | None:
    """
    獲取氣象資料

    Args:
        Authorization (str): 氣象資料API的授權金鑰

    Returns:
        dict | None: 氣象資料的列表，每個元素包含地點、開始和結束時間、天氣現象、降雨機率、最低和最高溫度等資訊

    Example:
        回傳值大概長這樣：
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
            }
        ]
        """
    api = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={Authorization}&format=JSON&elementName=Wx,PoP,MinT,MaxT"
    response = session.get(api)

    if response.status_code == 200:
        data = response.json()
        locations = data['records']['location']
        weather_data_list = []
        weather_unit = ["weather_code", "pop_unit", None, "temp_unit"]

        for location in locations:
            # 創建生命週期在每個location之間的三個空字典來存儲每個時間段之天氣資料
            weather_dict = [{} for _ in range(3)]

            locationName = location.get('locationName')
            weatherElements = location.get('weatherElement')
            # len == 4
            for i, weatherElement in enumerate(weatherElements):
                elementName = weatherElement.get('elementName')
                times = weatherElement.get('time')
                # len == 3
                for j, time in enumerate(times):
                    # 將時間轉為 timestamp 以符合 line message api 的回傳值
                    startTime = int(datetime.strptime(times[j].get('startTime'), '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                    endTime = int(datetime.strptime(times[j].get('endTime'), '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                    weather_dict[j].update({'locationName': locationName,
                                            'start_time': startTime,
                                            'end_time': endTime
                                            })
                    # 將天氣的參數轉換成列表以進行更方便的指定索引值
                    parameters = list(time.get('parameter').values())
                    # 如果天氣單位為 "None"，只更新元素名稱和其值
                    if weather_unit[i] is not None:
                        weather_dict[j].update({elementName: parameters[0],
                                                weather_unit[i]: parameters[1]})
                    else:
                        weather_dict[j].update({elementName: parameters[0]})
            # 將區域天氣資料（包括三個不同時間段的資料）添加到最終的天氣資料列表中
            weather_data_list.extend(weather_dict)

        return weather_data_list
    else:
        return None

if __name__ == "__main__":
    weather()