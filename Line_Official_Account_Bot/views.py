from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mapAPP.views import mapfunctionplus
from Line_Official_Account_Bot.models import (
    WeatherRecord,
    LineUserSessions,
    LineUserOnTimeBikeStatus,
    LineUserLocationsInformation
    )
from Line_Official_Account_Bot.scraper import weather as scweather
import json
import time
import os
import copy
from typing import Optional, Tuple
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    LocationMessageContent
)
# 設定 Line Bot 的基本參數和路徑設置。
base_dir = os.path.dirname(os.path.abspath(__file__))
quick_reply_path = os.path.join(base_dir, 'messages_components', 'quick_reply.json')
flex_message_path = os.path.join(base_dir, 'messages_components', 'Flex_message.json')
# 設定 Line Bot 配置和處理程序
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

# Create your views here.

# line bot
# 禁用 CSRF 驗證，以便 LINE 伺服器可以發送請求到此端點
@csrf_exempt
@require_POST
def callback(request):
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
    body = request.body.decode('utf-8')
    # print(json.loads(body).get('events'))
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
    return HttpResponse(status=200)

@handler.add(PostbackEvent)
def handle_postback(event):
    data = eval(event.postback.data)
    user_id = event.source.user_id
    action = data.get('action')
    task = data.get('task')
    timestamp = event.timestamp
    # 如果存在任務 就儲存到 session
    if task:
        # 獲取 task 儲存到 session，時效為五分鐘
        session = LineUserSessions(user_id=user_id,
                                   expiry_date=timestamp,
                                   task=task
                                  )
        # 儲存時預設 expiry_date = timestamp + 5分鐘
        session.save()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
        line_bot_api.show_loading_animation(show_loading_animation_request)
        if action == "shareLocation":
            with open(quick_reply_path, "r", encoding="utf-8") as quick_reply_component:
                quick_reply = QuickReply.from_dict(json.load(quick_reply_component).get('location'))
            message = TextMessage(text="確認分享您的所在位置", quickReply=quick_reply)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[message]
                )
            )
            show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
        elif action == "selectStation":
            # 提取 line 返回的 user id 在 sessions 中的資料並倒序排列
            session = LineUserSessions.objects.filter(user_id = user_id).order_by('-id')
            last_session = session.first()

             # 如果使用者的時間戳記小於 session 時間，代表 session 有效。
            if last_session.expiry_date >= timestamp:
                # 從資料庫中找到使用者使用車站查詢紀錄的資料
                bike_status_obj = LineUserOnTimeBikeStatus.objects.filter(user_id=user_id).all()
                bikeStatus = []
                for status in bike_status_obj:
                    temp = {}
                    temp.update(
                        {"name": status.name,
                         "available_spaces": status.available_spaces,
                         "parking_spaces": status.parking_spaces,
                         "duration": status.duration,
                         "msg": status.msg,
                         "update_time": status.update_time}
                        )
                    bikeStatus.append(temp)

                user_location_information = LineUserLocationsInformation.objects.filter(user_id=user_id).first()
                station_number = data.get('station')
                gps = (user_location_information.latitude, user_location_information.longitude)
                bubble = make_bike_status_bubble(station_number, bikeStatus, gps)
                # 設定站點切換按鍵 ( Quick Reply )
                quick_reply = make_station_reply(station_number, len(bikeStatus))
                # 發送資訊給使用者
                message = FlexMessage(alt_text="最佳站點推薦", contents=bubble, quickReply=quick_reply)
                line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[message]
                    )
                )
                show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
            else:
                line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="超過查詢時間，請重新查詢")]
                        )
                    )

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    user_id = event.source.user_id
    timestamp = event.timestamp
    address = event.message.address
    latitude = event.message.latitude
    longitude = event.message.longitude

    # 儲存使用者的 location 供後續使用
    user_location_information = LineUserLocationsInformation(
        user_id=user_id,
        timestamp=timestamp,
        address=address,
        latitude=latitude,
        longitude=longitude
    )

    user_location_information.save()

    # 提取 line 返回的 user id 在 sessions 中的資料並倒序排列
    session = LineUserSessions.objects.filter(user_id = user_id).order_by('-id')
    last_session = session.first()

    # 如果使用者的時間戳記小於 session 時間，代表 session 有效。
    if last_session.expiry_date >= timestamp:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)
            line_bot_api.show_loading_animation(show_loading_animation_request)
            # 判斷使用者要查詢天氣預報
            if last_session.task == "weather_query":
                address = event.message.address
                if "台灣" in address:
                    location = address.split("台灣")[1][0:3]
                elif "省" in address:
                    location = address.split("省")[1][0:3]
                else:
                    location = address[0:3]

                if "台" in location:
                    location = location.replace("台", "臺")

                weather_records = WeatherRecord.objects.filter(
                    location=location,
                    start_time__lte=timestamp,
                    end_time__gte=timestamp
                    )
                # 檢查對應資料是否存在，如果對應資料不存在那就不在台灣
                if weather_records.exists():
                    #理論上只會有一筆資料，但留著保平安
                    weather_record = weather_records.first()

                    with open(flex_message_path, "r", encoding="utf-8") as file:
                        bubble_string = json.load(file).get('weather_bubble')
                    bubble = FlexContainer.from_dict(bubble_string)
                    # 圖片
                    if int(weather_record.weather_code) < 10:
                        bubble.hero.contents[0].url = f"https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/png_icon/day/0{weather_record.weather_code}.png"
                    else:
                        bubble.hero.contents[0].url = f"https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/png_icon/day/{weather_record.weather_code}.png"
                    # 天氣
                    bubble.hero.contents[1].text = weather_record.wx
                    # 最低溫度
                    bubble.body.contents[0].contents[0].contents[1].contents[0].contents[0].text = weather_record.min_temp
                    # 最高溫度
                    bubble.body.contents[0].contents[0].contents[1].contents[0].contents[2].text = weather_record.max_temp
                    # 降雨機率
                    bubble.body.contents[0].contents[1].contents[1].contents[0].text = weather_record.pop_value

                    message = FlexMessage(alt_text="weather", contents=bubble)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[message]
                        )
                    )
                else:
                    line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="僅支援台灣地區")]
                    )
                )
            # 判斷使用者要查詢最佳站點
            elif last_session.task == "yb_select_site":
                gps = {'lat': latitude, 'lng': longitude}
                parameter = mapfunctionplus(gps)
                bikeStatus = parameter.get('bikeStatus')

                # 刪除關於此使用者之前儲存的 top 5 站點資料
                LineUserOnTimeBikeStatus.objects.filter(user_id=user_id).delete()
                # 寫入新的 top 5 站點資料
                for information in bikeStatus:
                    bike_station_status = LineUserOnTimeBikeStatus(
                        user_id=user_id,
                        name=information.get('name'),
                        available_spaces=information.get('available_spaces'),
                        parking_spaces=information.get('parking_spaces'),
                        duration=information.get('duration'),
                        msg=information.get('msg'),
                        update_time=information.get('update_time'),
                    )

                    bike_station_status.save()

                # 設定 default 使用者介面-資訊站點資訊 ( Flex Message )
                station_number = 1
                gps = (latitude, longitude)
                bubble = make_bike_status_bubble(station_number, bikeStatus, gps)
                # 設定站點切換按鍵 ( Quick Reply )
                quick_reply = make_station_reply(station_number, len(bikeStatus))
                # 發送資訊給使用者
                message = FlexMessage(alt_text="最佳站點推薦", contents=bubble, quickReply=quick_reply)
                line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[message]
                    )
                )
                show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)

    else:
        line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="超過查詢時間，請重新查詢")]
                )
            )

# weather records
def weather(request):
    METEOROLOGICAL_DATA_OPEN_PLATFORM = settings.METEOROLOGICAL_DATA_OPEN_PLATFORM

    WeatherRecord.objects.all().delete()
    weather_data_list = scweather(METEOROLOGICAL_DATA_OPEN_PLATFORM)

    if weather_data_list is not None:
        for weather_data in weather_data_list:
            weather_record = WeatherRecord(
                location=weather_data.get('locationName'),
                start_time=weather_data.get('start_time'),
                end_time=weather_data.get('end_time'),
                wx=weather_data.get('Wx'),
                weather_code=weather_data.get('weather_code'),
                pop_value=weather_data.get('PoP'),
                pop_unit=weather_data.get('pop_unit'),
                min_temp=weather_data.get('MinT'),
                max_temp=weather_data.get('MaxT'),
                temp_unit=weather_data.get('temp_unit')
            )
            weather_record.save()
            time.sleep(0.1)

        return HttpResponse("Weather data fetched and saved successfully.")
    else:
        return HttpResponse("Failed to fetch data", status=403)

# 建立站點選項的 quick reply
def make_station_reply(station_number: int, bikeStatus_len: int) -> QuickReply:
    station_index = station_number - 1

    with open(quick_reply_path, "r", encoding="utf-8") as quick_reply_component:
            quick_reply_string = json.load(quick_reply_component).get('postBack')
    items = quick_reply_string.get('items')

    select_station_template = items[0]
    # data 是 string 型別，為方便操作轉換為 dict
    select_station_template['action']['data'] = json.loads(select_station_template['action']['data'])

    new_items = []

    for i in range(1, bikeStatus_len+1):
        temp_select_station = copy.deepcopy(select_station_template)
        temp_select_station['action']['label'] = f"站點 {i}"
        temp_select_station['action']['data']['station'] = i
        # QuickReply 的 data 只接受 string，故將之轉換回 string
        temp_select_station['action']['data'] = str(temp_select_station['action']['data'])
        new_items.append(temp_select_station)

    new_items.pop(station_index)
    quick_reply_string['items'] = new_items

    return QuickReply.from_dict(quick_reply_string)

def make_bike_status_bubble(station_number: int, bikeStatus: list[dict], gps: Tuple[float, float]) -> FlexContainer:
    latitude, longitude = gps
    station_index = station_number - 1

    with open(flex_message_path, "r", encoding="utf-8") as file:
        bubble_string = json.load(file).get('ybSelectSite')
    bubble = FlexContainer.from_dict(bubble_string)

    # 設定 default 站點資訊 Flex Message

    # 站點
    bubble.body.contents[0].contents[1].text = bikeStatus[station_index].get('name')
    # 剩餘車輛
    bubble.body.contents[1].contents[1].text = str(bikeStatus[station_index].get('available_spaces'))
    # 全部車輛
    bubble.body.contents[1].contents[3].text = str(bikeStatus[station_index].get('parking_spaces'))
    # 路程時間推算
    bubble.body.contents[2].contents[1].text = str(bikeStatus[station_index].get('duration'))
    # 最佳站點建議
    if bikeStatus[0].get('msg') == "車輛充裕，建議前往":
        bubble.body.contents[3].contents[0].text = bikeStatus[station_index].get('msg')
        bubble.body.contents[3].contents[0].color = "#119e1a"
    elif bikeStatus[0].get('msg') == "車輛緊張，建議更換站點":
        bubble.body.contents[3].contents[0].text = bikeStatus[station_index].get('msg')
        bubble.body.contents[3].contents[0].color = "#f04d4d"
    else:
        bubble.body.contents[3].contents[0].text = bikeStatus[station_index].get('msg')
        bubble.body.contents[3].contents[0].color = "#D3D3D3"
        bubble.body.contents[3].size = "md"
    # 資料更新時間
    bubble.body.contents[4].contents[1].text = str(bikeStatus[station_index].get('update_time'))
    # 打開 yb_select_side
    bubble.footer.action.uri = f"https://yb-select-site-cf3061dbdf38.herokuapp.com/map/?lat={latitude}&lng={longitude}"

    return bubble

def make_weather_record_bubble(weather_record: WeatherRecord) -> FlexContainer:
    with open(flex_message_path, "r", encoding="utf-8") as file:
            bubble_string = json.load(file).get('weather_bubble')
    bubble = FlexContainer.from_dict(bubble_string)
    # 圖片
    if int(weather_record.weather_code) < 10:
        bubble.hero.contents[0].url = f"https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/png_icon/day/0{weather_record.weather_code}.png"
    else:
        bubble.hero.contents[0].url = f"https://www.cwa.gov.tw/V8/assets/img/weather_icons/weathers/png_icon/day/{weather_record.weather_code}.png"
    # 天氣
    bubble.hero.contents[1].text = weather_record.wx
    # 最低溫度
    bubble.body.contents[0].contents[0].contents[1].contents[0].contents[0].text = weather_record.min_temp
    # 最高溫度
    bubble.body.contents[0].contents[0].contents[1].contents[0].contents[2].text = weather_record.max_temp
    # 降雨機率
    bubble.body.contents[0].contents[1].contents[1].contents[0].text = weather_record.pop_value

    return bubble
