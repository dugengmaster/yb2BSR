from django.shortcuts import render

# Create your views here.
""


# 顯示關於我們頁面
def about_us(request):
    return render(request, "aboutUS/aboutUs.html")
