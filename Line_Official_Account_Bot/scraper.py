import requests
from datetime import datetime

agent = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(agent)

def weather(api):
    response = session.get(api)

    if response.status_code == 200:
        data = response.json()
        locations = data['records']['location']

        weather_data_list = []

        for location in locations:
            locationName = location.get('locationName')
            weatherElements = location.get('weatherElement')

            # 初始化一個字典來存儲各時間段的天氣數據
            weather_dict = {}

            for weatherElement in weatherElements:
                elementName = weatherElement.get('elementName')
                times = weatherElement.get('time')

                for time in times:
                    startTime = time.get('startTime')
                    endTime = time.get('endTime')
                    parameters = time.get('parameter')

                    # 轉換時間格式為timestamp
                    startTime = int(datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                    endTime = int(datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

                    key = (locationName, startTime, endTime)

                    if key not in weather_dict:
                        weather_dict[key] = {
                            "location": locationName,
                            "start_time": startTime,
                            "end_time": endTime
                        }

                    # 添加參數到對應的 key 的字典中
                    if elementName == 'Wx':
                        weather_dict[key]['wx'] = parameters.get('parameterName')
                        weather_dict[key]['weather_code'] = parameters.get('parameterValue')
                    elif elementName == 'PoP':
                        weather_dict[key]['pop_value'] = parameters.get('parameterName')
                        weather_dict[key]['pop_unit'] = parameters.get('parameterUnit')
                    elif elementName == 'MinT':
                        weather_dict[key]['min_temp'] = parameters.get('parameterName')
                    elif elementName == 'MaxT':
                        weather_dict[key]['max_temp'] = parameters.get('parameterName')
                        weather_dict[key]['temp_unit'] = parameters.get('parameterUnit')

            # 將整理好的數據添加到列表中
            for key, value in weather_dict.items():
                weather_data_list.append(value)

        return weather_data_list
    else:
        return None


if __name__ == "__main__":
    weather()