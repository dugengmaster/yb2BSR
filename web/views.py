from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
import logging
from web.models import UserProfile

# Create your views here.

def custom_authenticate(username, password):
    try:
        user = UserProfile.objects.get(username=username)
        if check_password(password, user.password):
            return user
    except UserProfile.DoesNotExist:
        return None

def my_login(request):
    show_modal_1 = False  # 預設不顯示模態窗口

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 使用自定義身份驗證方法
        user = custom_authenticate(username=username, password=password)
        # print("user:", user)

        if user is not None:
            login(request, user, backend='web.backed.LineUserBackend')  # 將用戶信息存儲在會話中，實現保持登錄狀態
            return redirect("home")  # 登錄成功後重定向到首頁

        # 使用自定義身份驗證方法
        user = custom_authenticate(username=username, password=password)
        # print("user:", user)

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # 將用戶信息存儲在會話中，實現保持登錄狀態
            return redirect("home")  # 登錄成功後重定向到首頁
        else:
            error_message = "帳號或密碼錯誤! 注意大小寫"
            messages.error(request, error_message)  # 使用 messages 庫來添加錯誤訊息
            show_modal_1 = True

    # GET 請求或登入失敗後顯示表單
    return render(request, "home.html", {"error_message":error_message,'show_modal_1': show_modal_1})

def home(request):
    if request.user.is_authenticated:
        line_user_id = request.user.line_user_id
        line_name = request.user.line_name
        email = request.user.email
        email = email.split("@")[0]

        context = {
            "line_user_id":line_user_id,
            "line_name":line_name,
            "email":email,
        }

        # print("line_name",line_name)
        # print("email",email)
        return render(request,'home.html',context)
        # return render(request, 'home.html')
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

import requests
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
import secrets
from django.http import HttpResponse, HttpResponseBadRequest

from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth import get_user_model
from web.backed import LineUserBackend


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
            if 'line_user_id' in request.session:
                del request.session['line_user_id']
            if 'display_name' in request.session:
                del request.session['display_name']
            line_user_id = user_info_data['userId']
            display_name = user_info_data.get('displayName', 'No Name')
            request.session['line_user_id'] = line_user_id
            request.session['display_name'] = display_name
            user_profiles = UserProfile.objects.all().values_list('username', flat=True)
            for username in user_profiles:
                username = username
                # print("user_profiles",username)



            # 嘗試根據 line_user_id 創建或獲取用戶
            try:
                user = UserProfile.objects.get(line_user_id=line_user_id)
                # print(f"找到用戶：{user.line_user_id}")

            except UserProfile.DoesNotExist:
                user = None
            if user is None:
                user = LineUserBackend().authenticate(request, line_user_id=line_user_id)
                if not user:
                    # 如果是新用戶，返回 1.html 並顯示註冊模態
                    user_name = UserProfile.objects.get(username=username)
                    if user_name:
                        user_profile, created = UserProfile.objects.get_or_create(username=user_name)
                        user_profile.line_user_id = line_user_id
                        user_profile.line_name = display_name
                        user_profile.save()
                        user = UserProfile.objects.get(username=username)
                        user.backend = 'web.backed.LineUserBackend'
                        login(request, user)
                        line_user_id = request.user.line_user_id
                        line_name = request.user.line_name
                        email = request.user.email
                        email = email.split("@")[0]

                        context = {
                            "line_user_id":line_user_id,
                            "line_name":line_name,
                            "email":email,
                        }
                        return render(request,'home.html',context)
                    return render(request, 'home.html', {'show_modal': True})



                # 如果line_id為空，顯示綁定LINE按鈕
                return redirect('home', show_bind_button=True)

            # 登錄已存在的用戶
            user.backend = 'web.backed.LineUserBackend'
            login(request, user)
            line_user_id = request.user.line_user_id
            line_name = request.user.line_name
            email = request.user.email
            email = email.split("@")[0]

            context = {
                            "line_user_id":line_user_id,
                            "line_name":line_name,
                            "email":email,
                        }
            return render(request, 'home.html',context)
        else:
            # 如果未能獲取 Access Token，返回錯誤信息
            error_description = response_data.get('error_description', 'Unknown error')
            logger.error(f"Failed to obtain access token. Error: {error_description}")
            return HttpResponseBadRequest(f"Failed to obtain access token. Error: {error_description}")

    except Exception as e:
        logger.error(f"Error in line_login_callback: {e}")
        return HttpResponseBadRequest(f"Error in line_login_callback: {e}")


User = get_user_model()

def registerModal(request):
    if request.method == 'POST':
        # 獲取註冊表單提交的數據
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        telecom = request.POST.get('registerCarrier')
        email = request.POST.get('email')
        line_user_id = request.session.get('line_user_id')
        display_name = request.session.get('display_name')
        request.session['new_username'] = new_username

        # 檢查所有字段是否已填寫
        if not (new_username and new_password and telecom and email):
            return HttpResponseBadRequest('所有字段都是註冊所需的。')

        try:
            # 將註冊用戶的數據保存到數據庫中
            # user = User.objects.create_user(username=new_username, password=new_password, email=email)

            # 將用戶訊息儲存到用戶的 UserProfile 中（如果有其他信息需要儲存）
            UserProfile.objects.create(
                # user=user,
                username=new_username,
                password=make_password(new_password),  # 使用 hashed password
                email=email,
                telecom=telecom,
                line_user_id=line_user_id,
                line_name=display_name,
                registration_date=timezone.now()
            )
            # print("user_profile created successfully")  # 打印成功消息，用於調試

            # 自動登入新註冊的用戶
            user = authenticate(username=new_username, password=new_password)
            # print("user",user)
            if user is not None:
                login(request, user)
                return redirect('/')  # 這裡可以重定向到其他頁面或者顯示成功消息

        except Exception as e:
            # 在捕獲到異常時，返回適當的錯誤消息
            error_message = f'註冊用戶失敗：{str(e)}'
            return HttpResponseBadRequest(error_message)

    return render(request, 'home.html', {'show_modal': True})

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

