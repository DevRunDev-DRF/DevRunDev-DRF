from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, InstructorApplication
from courses.models import Course, Section, Lesson
from enrollments.models import Enrollment, Certificate, Payment, CartItem
from reviews.models import Review


def is_manager(user):
    """관리자 또는 매니저 권한 확인"""
    return user.is_staff or user.role == user.Role.MANAGER


@login_required
@user_passes_test(is_manager)
def admin_dashboard(request):
    """관리자 대시보드 메인 페이지"""

    # 현재 시간 기준 설정
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # 주요 통계 데이터 수집
    stats = {
        # 사용자 통계
        "total_users": User.objects.count(),
        "students_count": User.objects.filter(role=User.Role.STUDENT).count(),
        "instructors_count": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "managers_count": User.objects.filter(role=User.Role.MANAGER).count(),
        "today_users": User.objects.filter(date_joined__date=today).count(),
        "week_users": User.objects.filter(date_joined__date__gte=last_week).count(),
        "month_users": User.objects.filter(date_joined__date__gte=last_month).count(),
        # 강의 통계
        "total_courses": Course.objects.count(),
        "approved_courses": Course.objects.filter(status="approved").count(),
        "review_courses": Course.objects.filter(status="review").count(),
        "rejected_courses": Course.objects.filter(status="not_approved").count(),
        # 강사 신청 통계
        "pending_instructors": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).count(),
        "approved_instructors": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.APPROVED
        ).count(),
        "rejected_instructors": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.REJECTED
        ).count(),
        # 수강 통계
        "total_enrollments": Enrollment.objects.count(),
        "active_enrollments": Enrollment.objects.filter(status="in_progress").count(),
        "completed_enrollments": Enrollment.objects.filter(status="completed").count(),
        "certificates_count": Certificate.objects.count(),
        "today_enrollments": Enrollment.objects.filter(enrolled_at__date=today).count(),
        "week_enrollments": Enrollment.objects.filter(
            enrolled_at__date__gte=last_week
        ).count(),
        "month_enrollments": Enrollment.objects.filter(
            enrolled_at__date__gte=last_month
        ).count(),
        # 리뷰 통계
        "total_reviews": Review.objects.count(),
        "avg_rating": Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0,
        # 결제 통계
        "total_payments": Payment.objects.count(),
        "successful_payments": Payment.objects.filter(status="paid").count(),
        "total_revenue": Payment.objects.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
        "today_revenue": Payment.objects.filter(
            created_at__date=today, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "week_revenue": Payment.objects.filter(
            created_at__date__gte=last_week, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "month_revenue": Payment.objects.filter(
            created_at__date__gte=last_month, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
    }

    # 최근 활동 데이터
    recent_data = {
        "recent_users": User.objects.order_by("-date_joined")[:10],
        "recent_courses": Course.objects.order_by("-created_at")[:10],
        "recent_enrollments": Enrollment.objects.order_by("-enrolled_at")[:10],
        "recent_reviews": Review.objects.order_by("-created_at")[:10],
        "recent_instructor_applications": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).order_by("-created_at")[:5],
        "recent_payments": Payment.objects.order_by("-created_at")[:10],
    }

    # 인기 강의 (수강생 많은 순)
    popular_courses = Course.objects.annotate(
        enrollment_count=Count("enrollments")
    ).order_by("-enrollment_count")[:5]

    # 인기 강사 (수강생 많은 순)
    popular_instructors = (
        User.objects.filter(role=User.Role.INSTRUCTOR)
        .annotate(student_count=Count("course__enrollments__student", distinct=True))
        .order_by("-student_count")[:5]
    )

    # 차트 데이터
    chart_data = {
        "popular_courses": popular_courses,
        "popular_instructors": popular_instructors,
    }

    # 월별 사용자 등록 통계 (최근 6개월)
    monthly_stats = []
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=30 * i)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(
            day=1
        ) - timedelta(days=1)

        month_name = month_start.strftime("%Y년 %m월")

        signups = User.objects.filter(
            date_joined__date__range=[month_start, month_end]
        ).count()
        enrollments = Enrollment.objects.filter(
            enrolled_at__date__range=[month_start, month_end]
        ).count()
        revenue = (
            Payment.objects.filter(
                created_at__date__range=[month_start, month_end], status="paid"
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        monthly_stats.append(
            {
                "month": month_name,
                "signups": signups,
                "enrollments": enrollments,
                "revenue": revenue,
            }
        )

    context = {
        "stats": stats,
        "recent_data": recent_data,
        "chart_data": chart_data,
        "monthly_stats": monthly_stats,
    }

    return render(request, "admin/dashboard.html", context)


@login_required
@user_passes_test(is_manager)
def admin_users(request):
    """사용자 관리 페이지"""

    # 사용자 필터링
    role_filter = request.GET.get("role", "")

    # 기본 쿼리셋
    users = User.objects.all().order_by("-date_joined")

    # 역할 필터링
    if role_filter:
        users = users.filter(role=role_filter)

    # 검색 필터링
    search_query = request.GET.get("q", "")
    if search_query:
        users = users.filter(username__icontains=search_query) | users.filter(
            email__icontains=search_query
        )

    context = {
        "users": users,
        "role_filter": role_filter,
        "search_query": search_query,
        "stats": {
            "total_users": User.objects.count(),
            "students_count": User.objects.filter(role=User.Role.STUDENT).count(),
            "instructors_count": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
            "managers_count": User.objects.filter(role=User.Role.MANAGER).count(),
        },
    }

    return render(request, "admin/users.html", context)


@login_required
@user_passes_test(is_manager)
def admin_courses(request):
    """강의 관리 페이지"""

    # 강의 필터링
    status_filter = request.GET.get("status", "")

    # 기본 쿼리셋
    courses = Course.objects.all().order_by("-created_at")

    # 상태 필터링
    if status_filter:
        courses = courses.filter(status=status_filter)

    # 검색 필터링
    search_query = request.GET.get("q", "")
    if search_query:
        courses = courses.filter(title__icontains=search_query) | courses.filter(
            description__icontains=search_query
        )

    context = {
        "courses": courses,
        "status_filter": status_filter,
        "search_query": search_query,
        "stats": {
            "total_courses": Course.objects.count(),
            "approved_courses": Course.objects.filter(status="approved").count(),
            "review_courses": Course.objects.filter(status="review").count(),
            "rejected_courses": Course.objects.filter(status="not_approved").count(),
        },
    }

    return render(request, "admin/courses.html", context)


@login_required
@user_passes_test(is_manager)
def admin_instructor_applications(request):
    """강사 신청 관리 페이지"""

    # 강사 신청 필터링
    status_filter = request.GET.get("status", "")

    # 기본 쿼리셋
    applications = InstructorApplication.objects.all().order_by("-created_at")

    # 상태 필터링
    if status_filter:
        applications = applications.filter(status=status_filter)

    # 검색 필터링
    search_query = request.GET.get("q", "")
    if search_query:
        applications = applications.filter(
            user__username__icontains=search_query
        ) | applications.filter(user__email__icontains=search_query)

    context = {
        "applications": applications,
        "status_filter": status_filter,
        "search_query": search_query,
        "stats": {
            "pending_count": InstructorApplication.objects.filter(
                status=InstructorApplication.Status.PENDING
            ).count(),
            "approved_count": InstructorApplication.objects.filter(
                status=InstructorApplication.Status.APPROVED
            ).count(),
            "rejected_count": InstructorApplication.objects.filter(
                status=InstructorApplication.Status.REJECTED
            ).count(),
        },
    }

    return render(request, "admin/instructor_applications.html", context)


@login_required
@user_passes_test(is_manager)
def admin_payments(request):
    """결제 관리 페이지"""

    # 결제 필터링
    status_filter = request.GET.get("status", "")

    # 기본 쿼리셋
    payments = Payment.objects.all().order_by("-created_at")

    # 상태 필터링
    if status_filter:
        payments = payments.filter(status=status_filter)

    # 검색 필터링
    search_query = request.GET.get("q", "")
    if search_query:
        payments = (
            payments.filter(user__username__icontains=search_query)
            | payments.filter(user__email__icontains=search_query)
            | payments.filter(merchant_uid__icontains=search_query)
        )

    context = {
        "payments": payments,
        "status_filter": status_filter,
        "search_query": search_query,
        "stats": {
            "total_payments": Payment.objects.count(),
            "successful_payments": Payment.objects.filter(status="paid").count(),
            "total_revenue": Payment.objects.filter(status="paid").aggregate(
                total=Sum("amount")
            )["total"]
            or 0,
        },
    }

    return render(request, "admin/payments.html", context)
