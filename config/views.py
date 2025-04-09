from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as django_login
from courses.models import Course
from enrollments.models import CartItem


def home_view(request):
    # 인기 강의 (평점 순)
    popular_courses = Course.objects.filter(status="approved").order_by("-avg_rating")[
        :3
    ]

    # 최신 강의 (생성일 순)
    new_courses = Course.objects.filter(status="approved").order_by("-created_at")[:3]

    # 장바구니 수 계산
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    context = {
        "popular_courses": popular_courses,
        "new_courses": new_courses,
        "cart_count": cart_count,
    }
    return render(request, "home.html", context)


def login_view(request):
    if request.method == "GET":
        return render(request, "accounts/login.html")

    from accounts.serializers import LoginSerializer

    serializer = LoginSerializer(data=request.POST, context={"request": request})
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        django_login(request, user)
        messages.success(request, "로그인되었습니다.")
        return redirect("home")
    else:
        return render(request, "accounts/login.html", {"errors": serializer.errors})


def register_view(request):
    if request.method == "GET":
        return render(request, "accounts/register.html")

    from accounts.serializers import RegisterSerializer

    serializer = RegisterSerializer(data=request.POST)
    if serializer.is_valid():
        user = serializer.save()
        django_login(request, user)
        messages.success(request, "회원가입이 완료되었습니다.")
        return redirect("home")
    else:
        return render(request, "accounts/register.html", {"errors": serializer.errors})
