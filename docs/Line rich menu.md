# LINE Bot 圖文選單
本文件描述如何在 Django 專案中設置和管理 LINE Bot 的圖文選單（Rich Menu）。涵蓋了從 webhook 設置到事件處理以及圖文選單的創建和分配的完整流程。

## 整體流程
1. 使用 LINE 的 Rich Menu API 管理圖文選單（創建、更新、刪除、分配）。

    - 創建圖文選單：使用 LINE 的 Rich Menu API 來定義圖文選單的結構和內容，然後將其上傳到 LINE 伺服器。

    - 更新圖文選單：更新圖文選單是指修改已存在的圖文選單內容，包括名稱、操作區域等。

    - 刪除圖文選單：刪除圖文選單是指移除不再需要的圖文選單。

    - 分配圖文選單：將特定的圖文選單設置為默認圖文選單，或者根據用戶 ID 將圖文選單分配給特定用戶。
2. 設置 Webhook Endpoint 來接收來自 LINE 伺服器的事件。
3. 接收並解析來自 LINE 伺服器的事件請求。
4. 根據事件類型進行相應的處理並回應用戶操作。
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

## 常見的 Action 類型

1. **Postback Action**：
    - 用戶點擊後不會打開瀏覽器或發送消息，而是發送隱藏的 postback 數據給你的機器人。
    - 適合用於需要後端處理的操作，例如表單提交等。

    ```json
    {
      "type": "postback",
      "label": "Buy",
      "data": "action=buy&itemid=123"
    }
    ```

2. **Message Action**：
    - 用戶點擊後會發送一條預定義的消息。
    - 適合用於快速回復或觸發預定義消息。

    ```json
    {
      "type": "message",
      "label": "Say Hello",
      "text": "Hello, World!"
    }
    ```

3. **URI Action**：
    - 用戶點擊後會打開指定的 URL。
    - 適合用於導流到網站或其他網頁。

    ```json
    {
      "type": "uri",
      "label": "Visit Website",
      "uri": "https://example.com"
    }
    ```

4. **Datetime Picker Action**：
    - 用戶點擊後會彈出日期時間選擇器，選擇的日期時間會以 postback 數據形式發送。
    - 適合用於預約或時間選擇。

    ```json
    {
      "type": "datetimepicker",
      "label": "Select date",
      "data": "storeId=12345",
      "mode": "datetime"
    }
    ```

5. **Camera Action**：
    - 用戶點擊後會打開 LINE 的相機，拍攝的照片會發送給你的機器人。

    ```json
    {
      "type": "camera",
      "label": "Open Camera"
    }
    ```

6. **Camera Roll Action**：
    - 用戶點擊後會打開 LINE 的相簿，選擇的照片會發送給你的機器人。

    ```json
    {
      "type": "cameraRoll",
      "label": "Open Camera Roll"
    }
    ```

7. **Location Action**：
    - 用戶點擊後會打開地點選擇器，選擇的地點會發送給你的機器人。

    ```json
    {
      "type": "location",
      "label": "Send Location"
    }
    ```
## 設置 Webhook Endpoint

### 步驟三：建立處理 Webhook 的視圖

1. 在 `line_bot` 應用的 `views.py` 文件中添加一個視圖來處理 webhook 事件：


## 參考資料
- Line developers 官方文件
https://developers.line.biz/en/reference/messaging-api/#rich-menu-object
https://developers.line.biz/en/reference/messaging-api/#rich-menu-response-object
- Django 官方文件
https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.body

# 我要寫一個 顯示實時天氣 的功能

## 用Django跟linebot.v3來寫 如果需要增加 import 的套件 你自己處理

### process：

1. **用戶操作：**
    - 用戶按下rich menu按鈕，觸發postback事件。

2. **伺服器處理請求：**
    - LINE伺服器將postback事件請求轉發給Django的webhook API。

3. **Webhook API接收請求：**
    - Webhook API解析請求並確認其類型。
    - 如果請求為postback事件，檢查`action`參數。
    - 如果`action`為`sharelocation`，以asyncio執行以下步驟：
        1. 回應一個Flex Message Bubble，包含說明文字和同意/不同意按鈕。
        2. 將`user_id`、`timestamp`、`task`儲存在session中。

4. **用戶位置分享：**
    - 用戶按下同意按鈕並分享位置信息。
    - LINE伺服器將位置分享請求轉發給Django的webhook API。

5. **Webhook API處理位置請求：**
    - Webhook API解析位置請求。
    - 確認session中的`user_id`與位置請求中的`user_id`匹配。
    - 如果匹配，檢查session中的`task`類型。
        - 如果`task`為`weather_query`，執行以下步驟：
            - 從位置請求中獲取GPS位置。
            - 使用GPS位置獲取對應位置的天氣信息。
        - 如果`task`為`yb_select_site`，執行以下步驟：
            - 從位置請求中獲取GPS位置。
            - 使用GPS位置獲取對應位置的最佳YouBike站點位置。
    - 將天氣信息或YouBike站點位置發送給用戶。
    - 清除session中的`[timestamp, user_id, task]`資訊。

    但我要你一步一步來幫我完成 先從第一步開始