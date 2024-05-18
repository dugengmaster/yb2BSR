from django.shortcuts import render

# Create your views here.


# 顯示首頁
def index(request):
    return render(request, "user/index.html")


# 顯示會員資料
def user(request):
    return render(request, "user/user.html")


# 註冊

# 登入

# 修改會員資料

# 登出
