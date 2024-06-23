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
4. 在 line 官方帳號將圖文選單設置為 default 以顯示在用戶端。

    ```terminal
    python line_richmenu_manager.py -sd <rich_menu_id>
    ```

5. 設置 Webhook Endpoint URL 來接收 Line server Webhook api 發送過來的事件。請將以下 Endpoint URL 替換為你的伺服器的地址：
    - Heroku: `https://yb-select-site-cf3061dbdf38.herokuapp.com/callback/`
    - 本地端測試 (需使用 ngrok): `你的 ngrok 地址/callback/`

    請執行以下命令，將 <endpoint_url> 替換為你的伺服器的 Endpoint URL：

    ```terminal
    python line_richmenu_manager.py -se <endpoint_url>
    ```

## Line Bot Callback 函數
設置一個用於處理 Line Messaging API Webhook 事件的 callback 函數。該函數位於 Django 應用程式中，並使用 `line-bot-sdk` 來處理 Line Server 發送的事件。


## 參考資料
- Line developers 官方文件
https://developers.line.biz/en/reference/messaging-api/#rich-menu-object
https://developers.line.biz/en/reference/messaging-api/#rich-menu-response-object
- Django 官方文件
https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.body




