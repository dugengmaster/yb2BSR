from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Line_Official_Account_Bot.models import WeatherRecord
from Line_Official_Account_Bot.scraper import weather
import json
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
    QuickReplyItem,
    LocationAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
)
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

# Create your views here.

# line bot
# 禁用 CSRF 驗證，以便 LINE 伺服器可以發送請求到此端點
@csrf_exempt
@require_POST
def callback(request):
    # 從 HTTP 標頭中取得 LINE 伺服器發送的簽名
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
    # 取得請求的數據可能是
    body = request.body.decode('utf-8')
    events = json.loads(body)['events']
    print(events)

    for event in events:
        # 儲存user_id和task到session
        request.session['user_id'] = event.get('source', {}).get('userId')
        # request.session['timestamp'] = event.get('timestamp', {})
        request.session['task'] = json.loads(event.get('postback', {}).get('data', {})).get('task')

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponse(status=403)
    return HttpResponse(status=200)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

# @handler.add(PostbackEvent)
# def handle_postback(event):
    # data = json.loads(event.postback.data)
    # action = data.get('action')
    # task = data.get('task')
    # print(event)

# weather records
def weather(request) -> None:
    METEOROLOGICAL_DATA_OPEN_PLATFORM = settings.METEOROLOGICAL_DATA_OPEN_PLATFORM
    api = f'f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={METEOROLOGICAL_DATA_OPEN_PLATFORM}&format=JSON&elementName=Wx,PoP,MinT,MaxT"'
    weather_data_list = weather(api)

    if weather_data_list is not None:
        for weather_data in weather_data_list:
            WeatherRecord.objects.create(
                location=weather_data['location'],
                start_time=weather_data['start_time'],
                end_time=weather_data['end_time'],
                wx=weather_data.get('wx'),
                weather_code=weather_data.get('weather_code'),
                pop_value=weather_data.get('pop_value'),
                pop_unit=weather_data.get('pop_unit'),
                min_temp=weather_data.get('min_temp'),
                max_temp=weather_data.get('max_temp'),
                temp_unit=weather_data.get('temp_unit')
            )

        return HttpResponse("Weather data fetched and saved successfully.")
    else:
        return HttpResponse("Failed to fetch data", status=403)
