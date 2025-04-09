from django.shortcuts import render
from courses.models import Course


def home_view(request):
    # 인기 강의 (평점 순)
    popular_courses = Course.objects.filter(status="approved").order_by("-avg_rating")[
        :3
    ]

    # 최신 강의 (생성일 순)
    new_courses = Course.objects.filter(status="approved").order_by("-created_at")[:3]

    context = {
        "popular_courses": popular_courses,
        "new_courses": new_courses,
    }
    return render(request, "home.html", context)
