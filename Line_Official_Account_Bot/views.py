from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Line_Official_Account_Bot.models import WeatherRecord, LineUserSessions
from Line_Official_Account_Bot.scraper import weather as scweather
import json
import time
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
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    LocationMessageContent
)
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

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
    return HttpResponse(status=200)

@handler.add(PostbackEvent)
def handle_postback(event):
    data = json.loads(event.postback.data)
    # 獲取 task 儲存到 session，時效為五分鐘
    user_id = event.source.user_id
    action = data.get('action')
    task = data.get('task')
    timestamp = event.timestamp
    session = LineUserSessions(user_id=user_id,
                               expiry_date=timestamp,
                               task=task
                               )
    # 儲存時預設 expiry_date = timestamp + 5分鐘
    session.save()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if action == "shareLocation":
            with open(r".\Line_Official_Account_Bot\messages_components\quick_reply.json", "r", encoding="utf-8") as file:
                quick_reply = QuickReply.from_dict(json.load(file).get('shareLocation'))
                message = TextMessage(text="確認分享您的所在位置", quickReply=quick_reply)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[message]
                    )
                )

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    user_id = event.source.user_id
    timestamp = event.timestamp
    session = LineUserSessions.objects.filter(user_id = user_id).order_by('-id')
    last_session = session.first() # 抓最新一筆資料

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # 如果使用者的時間戳記小於 session 時間，代表 session 有效。
        if last_session.expiry_date >= timestamp:
            # 判斷使用者要查詢天氣預報
            if last_session.task == "weather_query":
                address = event.message.address
                if "台灣" in address:
                    location = address.split("台灣")[1][0:3]
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

                    with open(r".\Line_Official_Account_Bot\messages_components\Flex_message.json", "r", encoding="utf-8") as file:
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
                print("yb")
        else:
            line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="超過反應時間")]
                    )
                )

# weather records
def weather(request):
    METEOROLOGICAL_DATA_OPEN_PLATFORM = settings.METEOROLOGICAL_DATA_OPEN_PLATFORM

    weather_data_list = scweather(METEOROLOGICAL_DATA_OPEN_PLATFORM)
    # print(weather_data_list)
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
