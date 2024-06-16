from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
import requests
import logging
from django.contrib import messages
from django.conf import settings
import requests
import logging
from django.contrib import messages

# Create your views here.
from django.contrib.auth.models import User  # 导入用户模型
from django.contrib.auth.hashers import check_password

def custom_authenticate(username, password):
    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return user
    except User.DoesNotExist:
        return None

from django.contrib.auth.models import User  # 导入用户模型
from django.contrib.auth.hashers import check_password

def custom_authenticate(username, password):
    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return user
    except User.DoesNotExist:
        return None

def my_login(request):
    show_modal_1 = False  # 預設不顯示模態窗口

    show_modal_1 = False  # 預設不顯示模態窗口

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username:", username)
        print("password:", password)

        # 使用自定義身份驗證方法
        user = custom_authenticate(username=username, password=password)
        print("user:", user)

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # 將用戶信息存儲在會話中，實現保持登錄狀態
            return redirect("home")  # 登錄成功後重定向到首頁
        print("username:", username)
        print("password:", password)

        # 使用自定義身份驗證方法
        user = custom_authenticate(username=username, password=password)
        print("user:", user)

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # 將用戶信息存儲在會話中，實現保持登錄狀態
            return redirect("home")  # 登錄成功後重定向到首頁
        else:
            error_message = "帳號或密碼錯誤! 注意大小寫"
            messages.error(request, error_message)  # 使用 messages 庫來添加錯誤訊息
            show_modal_1 = True

    # GET 請求或登入失敗後顯示表單
    return render(request, "home.html", {"error_message":error_message,'show_modal_1': show_modal_1})



# @login_required


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'home.html')


def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect("my_login")

def stations(request):
    map_key = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
    return render(request, "mapAPP.html", map_key)
    map_key = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
    return render(request, "mapAPP.html", map_key)

# def analysis_view(request):
#     # 示例热门站点数据，可以从数据库或其他数据源获取
#     hot_stations = ["台北市", "台中市", "桃園市", "高雄市", "台南市"]
#     return render(request, "analysis.html", {"hot_stations": hot_stations})

# def station_analysis_view(request, station_name):
#     # 根据站点名称获取分析数据
#     analysis_data = {
#         "station_name": station_name,
#         "chart_data": [10, 20, 30, 40, 50],  # 示例数据
#     }
#     return render(request, "analysis.html", analysis_data)

# from django.http import Http404
# def my_view(request):
#     try:
#         # 你的視圖代碼...
#         # 如果無法找到所需內容，則手動引發 404 錯誤
#         # 如果你的視圖無法找到所需內容，你可以引發 Http404 異常
#         raise Http404("Page not found")
#     except Http404:
#         # 如果引發了 Http404 異常，導向到自定義的 404 錯誤頁面
#         return custom_404(request)

import requests
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
import secrets
from django.http import HttpResponse, HttpResponseBadRequest
from web.models import UserProfile
from django.contrib.auth import get_user_model
from django.contrib.auth import login
logger = logging.getLogger(__name__)
def custom_line_login(request):
    if 'code' in request.GET and 'state' in request.GET:
        # 校验 state，确保不被 CSRF 攻击
        state_from_session = request.session.get('line_login_state')
        state_from_request = request.GET.get('state')
        if state_from_session != state_from_request:
            logger.error('Invalid state parameter')
            return HttpResponseBadRequest('Invalid state parameter')

        # 清除会话中的 state 值，防止重复使用
        state_from_session = request.session.pop('line_login_state', None)

        code = request.GET.get('code')

        token_url = "https://api.line.me/oauth2/v2.1/token"
        client_id = settings.LINE_CLIENT_ID
        client_secret = settings.LINE_CLIENT_SECRET
        redirect_uri = "http://127.0.0.1:8000/line/login/callback/"

        response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        })

        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')

            profile_url = "https://api.line.me/v2/profile"
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(profile_url, headers=headers)

            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                line_user_id = profile_data.get('userId')
                display_name = profile_data.get('displayName', 'No Name')

                try:
                    user = authenticate(request, username=line_user_id)
                    if user is None:
                        user = User.objects.create_user(username=line_user_id, password=None)
                        user.first_name = display_name
                        user.save()

                    login(request, user)
                    return redirect('/')  # 登录成功后重定向到首页

                except Exception as e:
                    logger.error(f"Error in authentication or login: {e}")
                    return HttpResponseBadRequest("Failed to authenticate or login")

        else:
            logger.error(f"Failed to obtain access token. Status code: {response.status_code}")
            return HttpResponse("Failed to obtain access token", status=response.status_code)

    else:
        # 生成随机的 state 值并将其存储在会话中
        state = secrets.token_urlsafe(16)
        request.session['line_login_state'] = state
        # print("state",state)
        base_url = "https://access.line.me/oauth2/v2.1/authorize"
        client_id = settings.LINE_CLIENT_ID
        redirect_uri = "http://127.0.0.1:8000/line/login/callback/"
        response_type = "code"
        scope = "profile openid"
        line_login_url = f"{base_url}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}"

        return redirect(line_login_url)

    return HttpResponseBadRequest("Invalid request")

def line_login_callback(request):
    logger = logging.getLogger(__name__)
    logger.info("line_login_callback view started")

    state = request.GET.get('state')
    code = request.GET.get('code')
    redirect_uri = "http://127.0.0.1:8000/line/login/callback/"
    # print("state",state)

    # 檢查 state 參數是否與 Session 中的 line_login_state 匹配
    if state != request.session.get('line_login_state'):
        logger.error('Invalid state parameter')
        return HttpResponseBadRequest('Invalid state parameter')

    try:
        # 刪除 Session 中的 line_login_state，以防止重複使用
        del request.session['line_login_state']
    except KeyError:
        logger.error('line_login_state not found in session')
        return HttpResponseBadRequest('Session state error')

    token_url = 'https://api.line.me/oauth2/v2.1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': settings.LINE_CLIENT_ID,
        'client_secret': "02f7373d862ef71e3c76888171fc54e7",
    }

    try:
        # 請求獲取 Access Token
        response = requests.post(token_url, headers=headers, data=data)
        response_data = response.json()

        if 'access_token' in response_data:
            access_token = response_data['access_token']

            # 使用 Access Token 請求用戶信息
            user_info_url = 'https://api.line.me/v2/profile'
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(user_info_url, headers=headers)
            user_info_data = user_info_response.json()

            line_user_id = user_info_data['userId']
            display_name = user_info_data.get('displayName', 'No Name')

            # 嘗試根據 line_user_id 創建或獲取用戶
            user, created = User.objects.get_or_create(username=line_user_id, defaults={'first_name': display_name})

            if created:
                # 如果是新用戶，返回 1.html 並顯示註冊模態
                return render(request, '1.html', {'show_modal': True})

            # 登錄已存在的用戶
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('/')
        else:
            # 如果未能獲取 Access Token，返回錯誤信息
            error_description = response_data.get('error_description', 'Unknown error')
            logger.error(f"Failed to obtain access token. Error: {error_description}")
            return HttpResponseBadRequest(f"Failed to obtain access token. Error: {error_description}")

    except Exception as e:
        logger.error(f"Error in line_login_callback: {e}")
        return HttpResponseBadRequest(f"Error in line_login_callback: {e}")



def register_user(new_username, new_password, email, telecom, request):
    try:
        # 创建新用户
        user = User.objects.create_user(username=new_username, password=new_password, email=email)

        # 保存电信信息到用户的 UserProfile
        user_profile = UserProfile.objects.create(user=user, telecom=telecom)
        print(user_profile)

        # 确认请求中的用户已经登录
        if request.user.is_authenticated:
            line_username = request.user.username

            # 将注册用户与 Line 登录用户进行关联
            user.line_username = line_username
            user.save()
            return HttpResponse("User registered and linked successfully.")
        else:
            return HttpResponse("Request user is not authenticated.")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def registerModal(request):
    if request.method == 'POST':
        # 獲取註冊表單提交的數據
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        carrier = request.POST.get('registerCarrier')
        email = request.POST.get('email')

        # 檢查所有字段是否已填寫
        if not (new_username and new_password and carrier and email):
            return HttpResponseBadRequest('所有字段都是註冊所需的。')

        try:
            # 將註冊用戶的數據保存到數據庫中
            user = User.objects.create_user(username=new_username, password=new_password, email=email)

            # 將電信信息保存到用戶的 UserProfile 中
            user_profile = UserProfile.objects.create(user=user, carrier=carrier)
            print(user_profile)  # 打印 UserProfile 對象，用於調試

            # 自動登入新註冊的用戶
            user = authenticate(username=new_username, password=new_password)
            if user is not None:
                login(request, user)
                return redirect('/')  # 這裡可以重定向到其他頁面或者顯示成功消息

        except Exception as e:
            return HttpResponseBadRequest(f'註冊用戶失敗：{str(e)}')

    return render(request, 'components/modals/register_modal.html')



def send_line_notification(user_id, message):
    try:
        # 從資料庫中查詢使用者的 access_token
        # 這裡假設你已經定義了一個 UserProfile 模型來存儲用戶的 LINE 使用者 ID 和 access_token
        user_profile = UserProfile.objects.get(user_id=user_id)
        access_token = user_profile.access_token
    except UserProfile.DoesNotExist:
        # 如果未找到使用者，則返回錯誤
        return HttpResponseBadRequest('User not found')

    # 向 LINE 發送通知
    notify_url = settings.LINE_NOTIFY_URL
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'message': message}

    response = requests.post(notify_url, headers=headers, data=data)
    if response.status_code == 200:
        return HttpResponse('Notification sent successfully')
    else:
        return HttpResponseBadRequest('Failed to send notification')

# def login_failed(request):
#     return render(request, 'login_failed.html')




def custom_404(request, exception):

    return render(request, "404.html", status=404)


def io(request):
    return render(request,"home.html")

def about_us(request):
    return render(request, "about_us.html")


def member(request):
    return render(request, "member.html")

def bike_trail(request):
    return render(request, "bike_trail.html")

def chart(request):
    return render(request, "chart.html")

def food(request):
    return render(request, "food.html")

