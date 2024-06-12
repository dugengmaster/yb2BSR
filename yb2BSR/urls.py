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



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", web_views.home, name="home"),
    path("login", web_views.home, name="home"),
    path('my_login/', views.my_login, name='my_login'),
    path('home/', web_views.home, name='home'),
    path("stations/", web_views.stations, name="stations"),
    path("analysis/", web_views.analysis_view, name="analysis"),
    path(
        "analysis/<str:station_name>/",
        web_views.station_analysis_view,
        name="station_analysis",
    ),
    path('register/', views.registerModal, name='register_page'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path("about_us/", include("aboutUS.urls")),
    path("map/", include("mapAPP.urls")),
    path('line/login/callback/', views.line_login_callback, name='line_login_callback'),
    path('login_failed/', views.login_failed, name='login_failed'),
    path("callback/", linebot_views.callback),
    path('line-login/', views.custom_line_login, name='custom_line_login'),

]
handler404 = web_views.custom_404
