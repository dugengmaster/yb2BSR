# 隱藏秘密金鑰

1. 本文件旨在描述如何安全地隱藏和專案中的秘密金鑰。

2. 為什麼需要隱藏秘密金鑰
    1. **安全性**：防止未經授權的訪問和使用。
    2. **可維護性**：集中管理和更新秘密金鑰。

## 在專案中設置環境變數

遵循以下步驟將秘密金鑰存儲在環境變數中，並在應用程式啟動時讀取。

### 步驟一：更新本地儲存庫的 `main` 分支，並合併到你的工作分支。
1. 切換到 `origin/main` 分支：

    ```terminal
    git checkout main
    ```
2. 更新你在本地儲存庫的 `main` 分支：

    ```terminal
    git pull origin main
    ```
3. 切換回你的工作分支：

    ```terminal
    git checkout <你的分支名稱>
    ```
4. 將 `main` 分支合併到你的工作分支：

    ```terminal
    git merge main
    ```
### 步驟二：創建 .env 檔案
1. 在專案的根目錄下創建一個 `.env` 檔案 ( 根目錄指的是 `yb2BSR` 跟 `manage.py` 同一層的那個 )
2. 將 `discord secrect_key` 頻道中的文字全部儲存在 `.env` 檔案中。如：
    
    ```.env
    SECRET_KEY=your_secret_key_here
    DATABASE_PASSWORD=your_database_password_here
    ```
### 步驟三：更新 .gitignore 檔案
- 在專案的根目錄下找到或創建 `.gitignore` 檔案，並添加以下內容以確保 .env 檔案不被提交到版本控制系統：
    
    ```.gitignore
    .env
    ```
### 步驟四：安裝 python-dotenv 套件
- 安裝 `python-dotenv` 這個套件。

    ```terminal
    pip install python-dotenv
    ```
### 步驟五：在應用程式中讀取環境變數
- 在 Django 的 settings.py 檔案中，增加如下內容來讀取環境變數：
    
    ```python
    import os
    from dotenv import load_dotenv

    # Environment variable: ACCESS_TOKEN
    env_path = os.path.join(BASE_DIR, ".env")
    load_dotenv(env_path)

    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    ```

- **不要將金鑰寫在原始碼中，所有需要之金鑰都應該儲存在 `.env` 這個檔案之內統一進行管理**
- **後續要請將新金鑰時，請把她添加到 .env 檔案中，並在 settings.py 中的註解 # Environment variable: ACCESS_TOKEN之後，新增 os.getenv('你想新增的金鑰') 來讀取新金鑰。**

1. 在 `.env` 檔案中添加新金鑰：

    ```.env
    NEW_SECRET_KEY=your_new_secret_key_here
    ```
2. 在 `settings.py` 檔案中讀取新金鑰：

    ```python
    # Environment variable: ACCESS_TOKEN
    env_path = os.path.join(BASE_DIR, ".env")
    load_dotenv(env_path)

    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    NEW_SECRET_KEY = os.getenv('NEW_SECRET_KEY') # <-在這邊加上你新金鑰的讀取方式
    ```