from django.shortcuts import render
from courses.models import Course
from enrollments.views import get_cart_count


def home_view(request):
    # 인기 강의 (평점 순)
    popular_courses = Course.objects.filter(status="approved").order_by("-avg_rating")[
        :3
    ]

    # 최신 강의 (생성일 순)
    new_courses = Course.objects.filter(status="approved").order_by("-created_at")[:3]

    # 장바구니 수 계산
    cart_count = get_cart_count(request.user)

    context = {
        "popular_courses": popular_courses,
        "new_courses": new_courses,
        "cart_count": cart_count,
    }
    return render(request, "home.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from accounts.serializers import LoginSerializer, RegisterSerializer


def login_view(request):
    if request.method == "GET":
        return render(request, "accounts/login.html")

    serializer = LoginSerializer(data=request.POST, context={"request": request})
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        login(request, user)
        messages.success(request, "로그인되었습니다.")
        return redirect("home")
    else:
        return render(request, "accounts/login.html", {"errors": serializer.errors})


def register_view(request):
    if request.method == "GET":
        return render(request, "accounts/register.html")

    serializer = RegisterSerializer(data=request.POST)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        messages.success(request, "회원가입이 완료되었습니다.")
        return redirect("home")
    else:
        return render(request, "accounts/register.html", {"errors": serializer.errors})
