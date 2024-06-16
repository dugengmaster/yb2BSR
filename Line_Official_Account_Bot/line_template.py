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
import json

def quick_reply(line_bot_api, reply_token, action):
    with open(r".\Line_Official_Account_Bot\messages_components\quick_reply.json", "r", encoding="utf-8") as file:
        quick_reply = QuickReply.from_dict(json.load(file).get('shareLocation'))
        message = TextMessage(text="確認分享您的所在位置", quickReply=quick_reply)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[message]
            )
        )