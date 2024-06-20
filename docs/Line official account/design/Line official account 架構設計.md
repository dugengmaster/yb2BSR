# Line official account 架構設計

## 註冊系統



## 圖文選單

### 功能
Line official account 未註冊時 圖文選單顯示

| | | |
| :-: | :-: | :-: |
[最佳站點查詢](#最佳站點查詢) | [綁定 YB_site_select 會員](#綁定-yb_site_select-會員)

註冊後改為

| | | |
| :-: | :-: | :-: |
| [最佳站點查詢](#最佳站點查詢) | [天氣查詢](#天氣查詢) | [腳踏車步道導航](#腳踏車步道導航) |
| [公車站點查詢](#公車站點查詢) | [Youbike米其林](#youbike米其林) | [腳踏車道路救援](#腳踏車道路救援) |

### 綁定 YB_site_select 會員

1. 將按鍵設置為 Postback action，使用者按下之後，事件請求轉發給 Django 的 webhook API。
2. 2. **Webhook API接收請求：**
    - Webhook API解析請求並確認其類型。
    - 如果請求為 postback event，檢查 `action` 參數
    - 如果 `action` 為 `link_line_userId`，發送 Flex message bubble 給使用者

    >**Flex message bubble: { header: { pic }, body: { register text }, footer: { 同意, 不同意 }}**
2. 使用者按下 確定 按鍵後發送網址 ( post 請求 抓line massage: { userId, timestamp, postback: { data: { register }}} ) 給使用者回到我們網站的註冊頁進行註冊，按下取消則無功能。
3. 只要 database 內有使用者的 line_userId 那就將正常功能之圖文選單連結到使用者。


[[返回圖文選單]](#圖文選單)

### 最佳站點查詢

1. **用戶操作：**
    - 將按鍵設置為 Postback action，使用者按下之後，事件請求由 LINE 伺服器轉發給我方 Django 的 webhook API

2. **Webhook API接收請求：**
    - Webhook API解析請求並確認其類型。
    - 如果請求為 postback event，檢查 `action` 參數。
    - 如果 `action` 為 `share_location`，執行以下步驟：
        1. 回應一個 Flex Message Bubble，包含說明文字和同意/不同意按鈕。
        2. 將 `userId`、 `task` 儲存在 session 中。

3. **用戶位置分享：**
    - 用戶按下同意按鈕並分享位置信息。
    - LINE 伺服器將位置分享請求轉發給 Django 的 webhook API。

4. **Webhook API處理位置請求：**
    - Webhook API解析位置請求。
    - 確認 session 中的 `user_id` 與位置請求中的 `user_id` 匹配。
    - 如果匹配，檢查 session 中的 `task` 類型。
        - 如果 `task` 為 `yb_select_site`，執行以下步驟：
            - 從位置請求中獲取GPS位置。
            - 使用 GPS 位置獲取對應位置的最佳 YouBike 站點位置。
    - 將 YouBike 站點位置發送給用戶。
    - 清除 session 中的 `[user_id, task]` 資訊。

[[返回圖文選單]](#圖文選單)

### 天氣查詢

1. **用戶操作：**
    - 用戶按下 rich menu 按鈕，觸發 postback 事件。

2. **伺服器處理請求：**
    - LINE 伺服器將 postback 事件請求轉發給 Django 的 webhook API 。

3. **Webhook API接收請求：**
    - Webhook API解析請求並確認其類型。
    - 如果請求為 postback event，檢查 `action` 參數。
    - 如果 `action` 為 `share_location`，執行以下步驟：
        1. 回應一個Flex Message Bubble，包含說明文字和同意/不同意按鈕。
        2. 將 `user_id`、 `task` 儲存在 session 中。

4. **用戶位置分享：**
    - 用戶按下同意按鈕並分享位置信息。
    - LINE伺服器將位置分享請求轉發給 Django 的 webhook API。

5. **Webhook API 處理位置請求：**
    - Webhook API 解析位置請求。
    - 確認 session 中的 `user_id` 與位置請求中的 `user_id` 匹配。
    - 如果匹配，檢查 session 中的 `task` 類型。
        - 如果 `task` 為 `weather_query`，執行以下步驟：
            - 從位置請求中獲取 GPS 位置。
            - 使用 GPS 位置獲取對應位置的天氣信息。
    - 爬蟲抓取氣象局 F-C0032-001 api。
    - 將天氣信息用 Flex message bubble 發送給用戶。

        > Flex message bubble: { header: { pic },
         body: { text: {  }}}

        >pic => https://www.cwa.gov.tw/V8/C/K/Weather_Icon.html
    - 清除 session 中的`[user_id, task]`資訊。

[[返回圖文選單]](#圖文選單)

### 腳踏車步道導航

- 在圖文選單設置 Type 為 url 的按鍵，讓使用者跳轉到我們網站介紹頁

[[返回圖文選單]](#圖文選單)

### 公車站點查詢

- 爬蟲抓取 公車站點 api 整理資料傳給客戶端

[[返回圖文選單]](#圖文選單)

### Youbike米其林

- 在圖文選單設置 Type 為 url 的按鍵，讓使用者跳轉到我們網站介紹頁

[[返回圖文選單]](#圖文選單)

### 腳踏車道路救援

- 在圖文選單設置 Type 為 url 的按鍵，設置

    ```json
    action: {
    "type": "uri",
    "label": "help",
    "uri": "tel:119"
    }
    ```

[[返回圖文選單]](#圖文選單)


## 聊天機器人

- 連接 OPEN AI API

## 訊息推送
- 生日快樂