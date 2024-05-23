from django.shortcuts import render
from django.conf import settings

# Create your views here.


# 顯示有地圖的頁面
def mapAPP(request):
    map_key = {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
    return render(request, "map.html", map_key)


# 查詢特定站點

# 推薦站點

# 站點分析
