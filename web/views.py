from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
import requests
import logging


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

def my_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username:", username)
        print("password:", password)

        # 使用自定義身份驗證方法
        user = custom_authenticate(username=username, password=password)
        print("user:", user)

        if user is not None:
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # 將用戶信息存儲在會話中，實現保持登錄狀態
            return redirect("home")  # 登錄成功後重定向到首頁
        else:
            error_message = "帳號或密碼錯誤! 注意大小寫"
            return render(request, "home.html", {"error_message": error_message})
    else:
        return render(request, "home.html")



# @login_required
def home(request):
    # user_id = request.session.get('user_id')
    # if not user_id:
    #     return redirect('linelogin')

    # user = User.objects.get(id=user_id)
    # return render(request, 'home.html', {'user': user})
    username = request.user.username if request.user.is_authenticated else None
    return render(request, "home.html", {"username": username})





def logout_view(request):
    auth_logout(request)
    return redirect("my_login")


def stations(request):
    map_key = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
    return render(request, "stations.html", map_key)


def analysis_view(request):
    # 示例热门站点数据，可以从数据库或其他数据源获取
    hot_stations = ["台北市", "台中市", "桃園市", "高雄市", "台南市"]
    return render(request, "analysis.html", {"hot_stations": hot_stations})


def station_analysis_view(request, station_name):
    # 根据站点名称获取分析数据
    analysis_data = {
        "station_name": station_name,
        "chart_data": [10, 20, 30, 40, 50],  # 示例数据
    }
    return render(request, "analysis.html", analysis_data)


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

from django.urls import reverse

def custom_line_login(request):
    # LINE 登入頁面 URL
    base_url = "https://access.line.me/oauth2/v2.1/authorize"
    client_id = settings.LINE_CLIENT_ID
    redirect_uri ="http://127.0.0.1:8000/line/login/callback/"

    # 生成隨機的狀態值
    state = secrets.token_urlsafe(16)
    request.session['line_login_state'] = state

    # 設置 OAuth 2.0 請求參數
    response_type = "code"
    scope = "profile%20openid"  # 請求的權限範圍

    # 構建 LINE 登入頁面 URL
    line_login_url = (
        f"{base_url}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}"
    )
    # if 'redirect_uri' in request.session:
    #     del request.session['redirect_uri']
    print(line_login_url)
    print("Generated state:", state)
    # 將用戶導向 LINE 登入頁面
    return redirect(line_login_url)

User = get_user_model()
users = User.objects.all()
print(users)


def line_login_callback(request):
    logger = logging.getLogger(__name__)
    logger.info("line_login_callback view started")
    state = request.GET.get('state')
    code = request.GET.get('code')
    redirect_uri = "http://127.0.0.1:8000/line/login/callback/"

    if state != request.session.get('line_login_state'):
        return HttpResponseBadRequest('Invalid state parameter')
    print("Received state:", state)
    print("Session state:", request.session.get('line_login_state'))
    del request.session['line_login_state']

    token_url = 'https://api.line.me/oauth2/v2.1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': settings.LINE_CLIENT_ID,
        'client_secret': "02f7373d862ef71e3c76888171fc54e7",
    }

    # Request token
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()

    if 'access_token' in response_data:
        access_token = response_data['access_token']
        # print("access_token::",access_token)
        user_info_url = 'https://api.line.me/v2/profile'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info_data = user_info_response.json()

        line_user_id = user_info_data['userId']
        print("line_user_id::",line_user_id)
        display_name = user_info_data.get('displayName', 'No Name')

        try:
            user, created = User.objects.get_or_create(username=line_user_id, defaults={'first_name': display_name})

            if created:
                return redirect(reverse('register_page'))
                user.save()


            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('/')
        except Exception as e:
            print(f"Error saving or logging in user: {e}")
            return HttpResponseBadRequest(f"Error saving or logging in user: {e}")
    else:
        # If failed to obtain access token, return error response
        error_description = response_data.get('error_description', 'Unknown error')
        return HttpResponseBadRequest(f"Failed to obtain access token. Error: {error_description}")


def registerModal(request):
    if request.method == 'POST':
        # 获取注册表单提交的数据
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        # telecom = request.POST.get('telecom')
        email = request.POST.get('email')

        # 保存注册用户的数据到数据库
        user = User.objects.create_user(username=new_username, password=new_password, email=email)
        # UserProfile.objects.create(user=user, telecom=telecom)

        # 将注册用户与 Line 登录用户进行关联
        line_username = request.user.username
        user.line_username = line_username
        user.save()

        if request.POST.get('line_login') == 'true':
            # 自动登录新注册的用户
            user = authenticate(username=new_username, password=new_password)
            if user is not None:
                login(request, user)
        # 重定向到其他页面或者显示成功消息
        return redirect('/')  # 这里可以重定向到其他页面或者显示成功消息

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

def login_failed(request):
    return render(request, 'login_failed.html')



def custom_404(request,exception):

    return render(request, '404.html', status=404)

