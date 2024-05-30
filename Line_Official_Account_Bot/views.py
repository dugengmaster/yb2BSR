from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hashlib
import hmac
import base64
import json
import requests
import aiohttp
import asyncio

# from linebot.v3 import (
#     WebhookHandler
# )
# from linebot.v3.exceptions import (
#     InvalidSignatureError
# )
# from linebot.v3.messaging import (
#     Configuration,
#     ApiClient,
#     MessagingApi,
#     ReplyMessageRequest,
#     TextMessage
# )
# from linebot.v3.webhooks import (
#     MessageEvent,
#     TextMessageContent
# )

LINE_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET

LINE_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN

# Create your views here.

# 禁用 CSRF 驗證，以便 LINE 伺服器可以發送請求到此端點
# @csrf_exempt
# @require_POST
# def callback(request):
#     # 從 HTTP 標頭中取得 LINE 伺服器發送的簽名
#     signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
#     # 取得請求的數據可能是
#     body = request.body.decode('utf-8')
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         print(signature)
#         print(body)
#         return HttpResponse(status=403)
#     return HttpResponse(status=200)

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

# print(MessagingApi.mro())

def verify_signature(signature, body):
    # 計算簽名
    hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    expected_signature = base64.b64encode(hash).decode('utf-8')

    # 簽名驗證
    return signature == expected_signature

@csrf_exempt
@require_POST
async def callback(request):
    body = request.body.decode('utf-8')
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')

    if not verify_signature(signature, body):
        return HttpResponseForbidden()

    events = json.loads(body).get('events', [])
    tasks = []

    # 處理每個事件
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']
            reply_message = event['message']['text']
            tasks.append(send_reply_message(reply_token, reply_message))

    await asyncio.gather(*tasks)
    return HttpResponse(status=200)

async def send_reply_message(reply_token, message_text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': message_text}],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(data)) as response:
            if response.status != 200:
                print(f"Error: {response.status} {await response.text()}")

