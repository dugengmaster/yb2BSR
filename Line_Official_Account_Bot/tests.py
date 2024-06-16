from django.test import TestCase

# Create your tests here.

# import hashlib
# import hmac
# import base64
# import json
# import requests
# import aiohttp
# import asyncio
# from django.conf import settings
# from django.http import HttpResponse, HttpResponseForbidden
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST

# LINE_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET

# LINE_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN

# def verify_signature(signature, body):
#     # 計算簽名
#     hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
#     expected_signature = base64.b64encode(hash).decode('utf-8')

#     # 簽名驗證
#     return signature == expected_signature

# @csrf_exempt
# @require_POST
# async def callback(request):
#     body = request.body.decode('utf-8')
#     signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')

#     if not verify_signature(signature, body):
#         return HttpResponseForbidden()

#     events = json.loads(body).get('events', [])
#     tasks = []

#     # 處理每個事件
#     for event in events:
#         if event['type'] == 'message' and event['message']['type'] == 'text':
#             reply_token = event['replyToken']
#             reply_message = event['message']['text']
#             tasks.append(send_reply_message(reply_token, reply_message))

#     await asyncio.gather(*tasks)
#     return HttpResponse(status=200)

# async def send_reply_message(reply_token, message_text):
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
#     }
#     data = {
#         'replyToken': reply_token,
#         'messages': [{'type': 'text', 'text': message_text}],
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(data)) as response:
#             if response.status != 200:
#                 print(f"Error: {response.status} {await response.text()}")

