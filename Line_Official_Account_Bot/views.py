from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Line_Official_Account_Bot.models import WeatherRecord, LineUserSessions
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
    FlexMessage,
    FlexBubble,
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
    # events = json.loads(body).get('events')
    # print(*events)

    # for event in events:
    #     userId = event.get('source')
    #     task = json.loads(event.get('postback').get('data')).get('task')
    #     print(userId)
    #     # request.session['']

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
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

@handler.add(PostbackEvent)
def handle_postback(event):
    data = json.loads(event.postback.data)

    user_id = event.source.user_id
    action = data.get('action')
    task = data.get('task')
    timestamp = event.timestamp
    session = LineUserSessions(user_id=user_id,
                               expiry_date=timestamp,
                               task=task
                               )
    session.save()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if action == "shareLocation":
            handle_share_location(event, line_bot_api)
            # session_task(userId, task)
            # with open(r".\Line_Official_Account_Bot\flex_messages\sharelocation.json", "r", encoding="utf-8") as file:
            #     bubble_string = json.load(file)
            #     message = FlexMessage(alt_text="hello", contents=FlexContainer.from_dict(bubble_string))

            # line_bot_api.reply_message(
            #     ReplyMessageRequest(
            #         reply_token=event.reply_token,
            #         messages=[message]
            #     )
            # )

def handle_share_location(event, line_bot_api) -> None:
    with open(r".\Line_Official_Account_Bot\messages_components\quick_reply.json", "r", encoding="utf-8") as file:
        quick_reply = QuickReply.from_dict(json.load(file).get('shareLocation'))
        message = TextMessage(text="確認分享您的所在位置", quickReply=quick_reply)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[message]
            )
        )

# Django session
# def session_task(userId, task):
#     SessionStore.create()


# weather records
def weather(request):
    METEOROLOGICAL_DATA_OPEN_PLATFORM = settings.METEOROLOGICAL_DATA_OPEN_PLATFORM

    weather_data_list = weather(METEOROLOGICAL_DATA_OPEN_PLATFORM)
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
