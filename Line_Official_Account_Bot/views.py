from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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

# 禁用 CSRF 驗證，以便 LINE 伺服器可以發送請求到此端點
@csrf_exempt
@require_POST
def callback(request):
    # 從 HTTP 標頭中取得 LINE 伺服器發送的簽名
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
    # 取得請求的數據可能是
    body = request.body.decode('utf-8')
    events = json.loads(body)['events']
    for event in events:
        task = event.get('postback', {}).get('data')
        timestamp = event.get('timestamp')
    # userId = events.source.userId
    # print(type(events))
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponse(status=403)
    return HttpResponse(status=200)

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text=event.message.text)]
#             )
#         )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = json.loads(event.postback.data)
    action = data.get('action')
    task = data.get('task')

    if action == 'shareLocation':
        user_id = event.source.user_id

        # 儲存user_id, timestamp和task到session
        request.session['user_id'] = user_id
        request.session['timestamp'] = event.timestamp
        request.session['task'] = task

        if task == 'yb_select_site':
            reply_message = {
                "type": "flex",
                "altText": "Location Sharing",
                "contents": {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Please share your location",
                                "wrap": True
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "Share Location",
                                    "uri": "line://nv/location"
                                }
                            }
                        ]
                    }
                }
            }
            line_bot_api.reply_message(event.reply_token, reply_message)
