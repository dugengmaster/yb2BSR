"""
URL configuration for yb2BSR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from web import views as web_views
from Line_Official_Account_Bot import views as linebot_views
from web import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


from Line_Official_Account_Bot import views as linebot_views
from web import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", web_views.home, name="home"),
    # path("login", web_views.home, name="home"),
    path('my_login/', views.my_login, name='my_login'),
    path('home/', web_views.home, name='home'),
    # path("stations/", web_views.stations, name="stations"),
    path('register/', views.registerModal, name='register_page'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path("map/", include("mapAPP.urls")),
    path("callback/", linebot_views.callback),
    path("scraper/weather/", linebot_views.weather),
    path("about_us/", web_views.about_us, name="about_us"),
    path("member/", web_views.member, name="member"),
    path("bike_trail/", web_views.bike_trail, name="bike_trail"),
    path('line/login/callback/', views.line_login_callback, name='line_login_callback'),
    path('custom_line_login/', views.custom_line_login, name='custom_line_login'),
    path('chart/', views.chart, name='chart'),
    path('food/', views.food, name='food'),
    path('registerModal/', views.registerModal, name='registerModal'),


]
handler404 = web_views.custom_404
# 將自定義 404 視圖與指定路徑關聯
# urlpatterns += [
#     path('404/',web_views.custom_404),
# ]

