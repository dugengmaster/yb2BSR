# LINE Bot 圖文選單
本文件描述如何在 Django 專案中設置和管理 LINE Bot 的圖文選單（Rich Menu）。涵蓋了從 webhook 設置到事件處理以及圖文選單的創建和分配的完整流程。

## 整體流程
1. 使用 LINE 的 Rich Menu API 管理圖文選單（創建、更新、刪除、分配）。

    - 創建圖文選單：使用 LINE 的 Rich Menu API 來定義圖文選單的結構和內容，然後將其上傳到 LINE 伺服器。

    - 更新圖文選單：更新圖文選單是指修改已存在的圖文選單內容，包括名稱、操作區域等。

    - 刪除圖文選單：刪除圖文選單是指移除不再需要的圖文選單。

    - 分配圖文選單：將特定的圖文選單設置為默認圖文選單，或者根據使用者 ID 將圖文選單分配給特定使用者。
2. 設置 Webhook Endpoint 來接收來自 LINE 伺服器的事件。
3. 接收並解析來自 LINE 伺服器的事件請求。
4. 根據事件類型進行相應的處理並回應使用者操作。
## 安裝與設定

### 步驟一：安裝 `line-bot-sdk` 套件
1. 使用以下指令安裝 `line-bot-sdk` 套件：
    ```terminal
    pip install line-bot-sdk
    ```

### 步驟二：設定 LINE Bot 秘密金鑰

1. 在 `.env` 檔案中添加新金鑰：
    ```plaintext
    LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET
    LINE_CHANNEL_ACCESS_TOKEN=YOUR_CHANNEL_ACCESS_TOKEN
    ```

2. 在 `settings.py` 檔案中讀取新金鑰：
    ```python
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    ```

## 製作 Rich Menu

使用 [line_richmenu_manager](https://github.com/dugengmaster/line_richmenu_manager)。

1. clone line_richmenu_manager 到本地端。

    ```terminal
    git clone https://github.com/dugengmaster/line_richmenu_manager.git && cd line_richmenu_manager
    ```
2. 在 `rich_menu_configs` 資料夾放入 `yb_select_side_rich_menu_default.json` 與 `yb_select_side_rich_menu_main.json` 等設定文件，在 `images` 資料夾放入 `yb_select_side_rich_menu_default.jpg` 與 `yb_select_side_rich_menu_main.jpg` 等圖片。
3. 使用指令創造圖文選單與設置圖文選單顯示的圖片，example：

    ```terminal
    python line_richmenu_manager.py -C yb_select_side_rich_menu_default.json
    ```
    這會返回一個 rich menu id 記下這個 id 並用此 id 設置圖片，example：

    ```terminal
    python line_richmenu_manager.py -U <rich_menu_id> yb_select_side_rich_menu_default.jpg
    ```
4. 在 line 官方帳號將圖文選單設置為 default 以顯示在使用者端。

    ```terminal
    python line_richmenu_manager.py -sd <rich_menu_id>
    ```

## 設置 Webhook Endpoint 來接收來自 LINE 伺服器的事件。
請將以下 Endpoint URL 替換為伺服器的地址：
  - Heroku: `https://yb-select-site-cf3061dbdf38.herokuapp.com/callback/`
  - 本地端測試 (需使用 ngrok): `你的 ngrok 地址/callback/`

  請執行以下命令，將 <endpoint_url> 替換為你的伺服器的 Endpoint URL：

  ```terminal
  python line_richmenu_manager.py -se <endpoint_url>
  ```

## 接收並解析來自 LINE 伺服器的事件請求

設置一個用於處理 Line Messaging API Webhook 事件的 callback 函數。該函數位於 Django 應用程式中，並使用 `line-bot-sdk` 來處理 Line Server 發送的事件。

  ```python
  from django.conf import settings
  from django.http import HttpResponse, HttpResponseForbidden
  from django.views.decorators.csrf import csrf_exempt
  from django.views.decorators.http import require_POST
  from linebot.v3 import WebhookHandler
  from linebot.v3.exceptions import InvalidSignatureError

  @csrf_exempt
  @require_POST
  def callback(request):
    # 從請求的標頭中獲取 Line 的簽名
    signature = request.META.get('HTTP_X_LINE_SIGNATURE', '')
    # 從請求的主體中獲取事件內容
    body = request.body.decode('utf-8')
    try:
        # 使用 WebhookHandler 處理事件內容和簽名
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 如果簽名無效，返回 HTTP 403 Forbidden 錯誤
        return HttpResponseForbidden()
    # 回應 HTTP 200 OK 表示成功處理請求
    return HttpResponse(status=200)
  ```
## 根據事件類型進行相應的處理並回應使用者操作
在接收到來自 LINE 伺服器的事件請求後，根據不同的事件類型進行相應的處理並回應用戶操作。主要的事件類型包括：
### Postback Event
當使用者在圖文選單或按鈕上進行操作（如點擊按鈕）時，LINE 伺服器會發送 Postback 事件。可以根據接收到的數據進行相應的業務邏輯處理，例如導航到特定頁面、執行特定指令等。

```python
from linebot.v3.webhooks import PostbackEvent

@handler.add(PostbackEvent)
def handle_postback(event):
    # 程式邏輯
```

### Message Event
當使用者發送訊息時，LINE 伺服器會發送 Message 事件。根據訊息的內容進行處理，主要包括以下類型：

#### Location Message Content
當使用者發送地點訊息時，可以根據使用者提供的地點資訊進行相應的處理，如查找附近的服務點、提供路線導航等。

```python
from linebot.v3.webhooks import MessageEvent
from linebot.v3.webhooks import LocationMessageContent

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location_message(event):
    # 程式邏輯
```
### 創建回覆訊息

#### Flex Message and Quick Reply
讀取事先定義好的彈性訊息模板，然後根據需要修改模板的內容，最後將修改後的彈性訊息放入 `FlexMessage` 中以供發送給使用者。
1. **設定 LINE Bot 的基本參數和路徑設置**：
   - `base_dir`：取得目前文件的絕對路徑，作為基礎目錄。
   - `quick_reply_path` 和 `flex_message_path`：分別設定快速回覆訊息和彈性訊息的配置文件路徑。

2. 使用 FLEX MESSAGE SIMULATOR 製作訊息的模板。

3. 將模板儲存在 `./messages_components/Flex_message.json`。

4. 讀取彈性訊息配置文件並創建彈性訊息物件：
    ```python
    import json
    from linebot.v3.messaging import (
        FlexMessage,
        FlexContainer,
    )

    with open(flex_message_path, "r", encoding="utf-8") as file:
        flex_message_config = json.load(file)
        bubble_config = flex_message_config.get('example_bubble')
    bubble = FlexContainer.from_dict(bubble_config)
### 發送訊息給使用者
1. **設定 LINE Bot 配置和處理程序**：
    - `configuration`：使用 `Configuration` 設定訪問令牌 (`access_token`)，這是與 LINE API 通信所需的身份驗證令牌。

2. **發送訊息**：
    - 使用 `ApiClient` 建立 API 客戶端。
    - 通過 `MessagingApi` 來發送回覆訊息。
    - 使用 `reply_message` 方法，將 `ReplyMessageRequest` 封裝的回覆訊息發送給使用者。

```python
import os
from linebot.v3 import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest
  )

# 設定 Line Bot 的基本參數和路徑設置
base_dir = os.path.dirname(os.path.abspath(__file__))
quick_reply_path = os.path.join(base_dir, 'messages_components', 'quick_reply.json')
flex_message_path = os.path.join(base_dir, 'messages_components', 'Flex_message.json')

# 設定 Line Bot 配置和處理程序
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)

# 使用配置的訪問令牌創建 API 客戶端
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)

    # 使用 reply_message 方法發送回覆訊息
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,  # 事件的回覆令牌
            messages=[message]  # 要發送的訊息
        )
    )
```
### Line 讀取動畫
1. 使用配置好的訪問令牌創建 API 客戶端。
2. 初始化 `MessagingApi`，用於與 Line Bot 進行通信。
3. 創建顯示讀取動畫的請求，並在 `event` 中獲得欲返回之使用者的 `user_id`。
4. 創建 `ShowLoadingAnimationRequest` 物件，指定 `chatId=user_id`。
5. 使用 `api_client` 的 `show_loading_animation()` 方法發送顯示讀取動畫的請求。

```python
from linebot.v3.messaging import ShowLoadingAnimationRequest

# 使用配置的訪問令牌創建 API 客戶端
with ApiClient(configuration) as api_client:
    # 初始化 MessagingApi，用於與 Line Bot 進行通信
    line_bot_api = MessagingApi(api_client)

    # 創建顯示讀取動畫的請求，指定使用者的 chatId
    show_loading_animation_request = ShowLoadingAnimationRequest(chatId=user_id)

    # 通過 line_bot_api 發送顯示讀取動畫的請求
    line_bot_api.show_loading_animation(show_loading_animation_request)
```
## Line app 通過Django後端處理的功能
1. Line Sessions 管理
在處理 Line 使用者 sessions 時，我們使用了自定義的 `LineUserSessions` ORM 來管理 sessions 狀態。
儲存 使用者的 user_id，sessions 的有效時間 expiry_date，從使用者端接收到的任務 task。

2. 最佳站點推薦
    - 資料來源
        - `mapfunctionplus`：位於 `mapAPP` 應用程式內，提供最佳站點推薦所需的相關資料和功能。
        - `mapfunctionplus` 會回傳一個 `dict`，我們的 Line app 使用其中 `bikeStatus` 鍵獲取的即時站點狀態資訊。
        - 即時站點狀態資訊包括，站點名稱 `name`、可用車位數量 `available_spaces`、停車位數量 `parking_spaces`、預估路程時間 `duration`、最佳站點建議 `msg`、資料更新時間 `update_time`，這些資料以字典的形式存儲在一個列表中。

    - 相關函式
        - `make_station_reply(station_number: int, bikeStatus_len: int) -> QuickReply`

            功能：返回一個包含站點選項的快速回覆對象，排除了指定站點編號的項目。

            參數：
            - `station_number`: 整數，表示使用者選擇某一個鄰近站點的站點編號。
            - `bikeStatus_len`: 整數，表示鄰近站點的數量。
        - `make_bike_status_bubble(station_number: int, bikeStatus: list[dict], gps: Tuple[float, float]) -> FlexContainer`

            功能：返回一個 Flex Message 容器，用於顯示指定站點的單車狀態資訊。

            參數：
            - `station_number`: 整數，表示使用者選擇某一個鄰近站點的站點編號。
            - `bikeStatus`: 包含站點資訊的列表，每個元素是包含站點相關信息的字典。
            - `gps`: 包含緯度和經度的元組 (float, float)。

3. 天氣查詢
    - 資料來源
        - 天氣資料來自於資料庫中的 WeatherRecord 資料表，該表中包含了特定地點和時間範圍內的天氣記錄。

    - 相關函式
        - `make_weather_record_bubble(weather_record: WeatherRecord) -> FlexContainer`

        功能：把天氣紀錄的狀態資訊封裝成一個 Flex Message 容器。

        參數：
        - `weather_record`: 從資料庫 ORM 取得的 WeatherRecord 資料表物件，內含天氣記錄信息 ( 36小時 )。

## 參考資料
- Line developers 官方文件

  https://developers.line.biz/en/reference/messaging-api/#rich-menu-object

  https://developers.line.biz/en/reference/messaging-api/#rich-menu-response-object

  https://developers.line.biz/flex-simulator/
- Django 官方文件

  https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.body
- line-bot-sdk-python 技術文件

  https://github.com/line/line-bot-sdk-python
