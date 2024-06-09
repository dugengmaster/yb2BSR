from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import os


# Create your views here.
def my_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 檢查帳號和密碼是否符合預期值
        if username == "Ben" and password == "870126":
            user = authenticate(request, username=username, password=password)
            print(
                f"Input username: {username}, Input password: {password}, Authenticated user: {user}"
            )
            if user is not None:
                auth_login(request, user)
                return redirect("home")
            else:
                error_message = "認證失敗"
                return render(request, "login.html", {"error_message": error_message})
        else:
            error_message = "帳號或密碼錯誤! 注意大小寫"
            return render(request, "login.html", {"error_message": error_message})
    else:
        return render(request, "login.html")


# @login_required
def home(request):
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


def custom_404(request, exception):

    return render(request, "404.html", status=404)


def io(request):
    return render(request,"1.html")

def about_us(request):
    return render(request, "team.html")


def member(request):
    return render(request, "member.html")

def bike(request):
    return render(request, "bike.html")
