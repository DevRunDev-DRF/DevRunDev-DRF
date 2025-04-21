from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, InstructorApplication
from courses.models import Course, Section, Lesson
from enrollments.models import Enrollment, Certificate, Payment, CartItem
from reviews.models import Review


@staff_member_required
def admin_dashboard_data(request):
    """관리자 대시보드용 데이터 API"""

    # 현재 시간 기준으로 기간 설정
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # 대시보드에 표시할 주요 데이터 수집
    data = {
        # 강사 신청 관련
        "pending_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).count(),
        "approved_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.APPROVED
        ).count(),
        "rejected_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.REJECTED
        ).count(),
        # 강의 관련
        "review_course_count": Course.objects.filter(status="review").count(),
        "approved_course_count": Course.objects.filter(status="approved").count(),
        "not_approved_course_count": Course.objects.filter(
            status="not_approved"
        ).count(),
        # 사용자 관련
        "student_count": User.objects.filter(role=User.Role.STUDENT).count(),
        "instructor_count": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "manager_count": User.objects.filter(role=User.Role.MANAGER).count(),
        # 수강 관련
        "enrollment_count": Enrollment.objects.count(),
        "completed_enrollment_count": Enrollment.objects.filter(
            status="completed"
        ).count(),
        "certificate_count": Certificate.objects.count(),
        # 리뷰 관련
        "review_count": Review.objects.count(),
        "avg_rating": Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0,
        # 결제 관련
        "payment_count": Payment.objects.count(),
        "successful_payment_count": Payment.objects.filter(status="paid").count(),
        "total_revenue": Payment.objects.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
        # 기타 요약 정보
        "total_users": User.objects.count(),
        "total_courses": Course.objects.count(),
        "total_sections": Section.objects.count(),
        "total_lessons": Lesson.objects.count(),
        # 기간별 통계
        "today_users": User.objects.filter(date_joined__date=today).count(),
        "today_enrollments": Enrollment.objects.filter(enrolled_at__date=today).count(),
        "today_revenue": Payment.objects.filter(
            created_at__date=today, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "week_users": User.objects.filter(date_joined__date__gte=last_week).count(),
        "week_enrollments": Enrollment.objects.filter(
            enrolled_at__date__gte=last_week
        ).count(),
        "week_revenue": Payment.objects.filter(
            created_at__date__gte=last_week, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "month_users": User.objects.filter(date_joined__date__gte=last_month).count(),
        "month_enrollments": Enrollment.objects.filter(
            enrolled_at__date__gte=last_month
        ).count(),
        "month_revenue": Payment.objects.filter(
            created_at__date__gte=last_month, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
    }

    # 인기 강의 TOP 5
    popular_courses = Course.objects.filter(status="approved").order_by("-avg_rating")[
        :5
    ]
    data["popular_courses"] = [
        {
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor.username,
            "avg_rating": course.avg_rating,
            "enrollment_count": course.enrollments.count(),
            "price": course.price,
        }
        for course in popular_courses
    ]

    # 활발한 강사 TOP 5
    active_instructors = (
        User.objects.filter(role=User.Role.INSTRUCTOR)
        .annotate(
            course_count=Count("course", distinct=True),
            student_count=Count("course__enrollments__student", distinct=True),
            review_count=Count("course__reviews", distinct=True),
        )
        .order_by("-student_count")[:5]
    )

    data["active_instructors"] = [
        {
            "id": instructor.id,
            "username": instructor.username,
            "email": instructor.email,
            "course_count": instructor.course_count,
            "student_count": instructor.student_count,
            "review_count": instructor.review_count,
        }
        for instructor in active_instructors
    ]

    # 월별 통계 (최근 6개월)
    monthly_stats = []
    for i in range(5, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=30 * i)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(
            day=1
        ) - timedelta(days=1)

        month_name = month_start.strftime("%Y년 %m월")

        month_signups = User.objects.filter(
            date_joined__date__range=[month_start, month_end]
        ).count()

        month_enrollments = Enrollment.objects.filter(
            enrolled_at__date__range=[month_start, month_end]
        ).count()

        month_revenue = (
            Payment.objects.filter(
                created_at__date__range=[month_start, month_end], status="paid"
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        monthly_stats.append(
            {
                "month": month_name,
                "signups": month_signups,
                "enrollments": month_enrollments,
                "revenue": month_revenue,
            }
        )

    data["monthly_stats"] = monthly_stats

    # 장바구니 데이터
    cart_stats = {
        "total_cart_items": CartItem.objects.count(),
        "users_with_cart": CartItem.objects.values("user").distinct().count(),
        "avg_cart_value": CartItem.objects.aggregate(avg_value=Avg("course__price"))[
            "avg_value"
        ]
        or 0,
    }
    data["cart_stats"] = cart_stats

    # 강의 카테고리별 분석 (시뮬레이션)
    categories = [
        "프로그래밍",
        "웹개발",
        "모바일",
        "데이터",
        "AI/ML",
        "디자인",
        "비즈니스",
        "마케팅",
    ]
    category_stats = []

    for category in categories:
        # 실제로는 강의 카테고리 필드에 따라 필터링해야 함
        # 여기서는 임의의 데이터로 시뮬레이션
        import random

        course_count = random.randint(5, 30)
        enrollment_count = random.randint(20, 200)
        avg_rating = round(random.uniform(3.0, 5.0), 1)
        revenue = random.randint(100000, 5000000)

        category_stats.append(
            {
                "category": category,
                "course_count": course_count,
                "enrollment_count": enrollment_count,
                "avg_rating": avg_rating,
                "revenue": revenue,
            }
        )

    data["category_stats"] = category_stats

    return JsonResponse(data)


@staff_member_required
def admin_analytics_view(request):
    """관리자 분석 페이지"""
    from django.shortcuts import render

    # 현재 시간 기준으로 기간 설정
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # 기본 통계 데이터
    context = {
        "total_users": User.objects.count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "total_revenue": Payment.objects.filter(status="paid").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
    }

    # 기간별 사용자 통계
    user_stats = {
        "today": User.objects.filter(date_joined__date=today).count(),
        "yesterday": User.objects.filter(date_joined__date=yesterday).count(),
        "this_week": User.objects.filter(date_joined__date__gte=last_week).count(),
        "this_month": User.objects.filter(date_joined__date__gte=last_month).count(),
        "student_ratio": User.objects.filter(role=User.Role.STUDENT).count()
        / max(context["total_users"], 1)
        * 100,
        "instructor_ratio": User.objects.filter(role=User.Role.INSTRUCTOR).count()
        / max(context["total_users"], 1)
        * 100,
    }
    context["user_stats"] = user_stats

    # 기간별 수강 통계
    enrollment_stats = {
        "today": Enrollment.objects.filter(enrolled_at__date=today).count(),
        "yesterday": Enrollment.objects.filter(enrolled_at__date=yesterday).count(),
        "this_week": Enrollment.objects.filter(
            enrolled_at__date__gte=last_week
        ).count(),
        "this_month": Enrollment.objects.filter(
            enrolled_at__date__gte=last_month
        ).count(),
        "completed_ratio": Enrollment.objects.filter(status="completed").count()
        / max(context["total_enrollments"], 1)
        * 100,
    }
    context["enrollment_stats"] = enrollment_stats

    # 수익 통계
    revenue_stats = {
        "today": Payment.objects.filter(
            created_at__date=today, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "yesterday": Payment.objects.filter(
            created_at__date=yesterday, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "this_week": Payment.objects.filter(
            created_at__date__gte=last_week, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
        "this_month": Payment.objects.filter(
            created_at__date__gte=last_month, status="paid"
        ).aggregate(total=Sum("amount"))["total"]
        or 0,
    }
    context["revenue_stats"] = revenue_stats

    # 인기 강의 TOP 10
    popular_courses = (
        Course.objects.filter(status="approved")
        .annotate(enrollment_count=Count("enrollments"))
        .order_by("-enrollment_count")[:10]
    )

    context["popular_courses"] = popular_courses

    # 최근 활동 로그
    recent_activities = []

    # 최근 가입
    for user in User.objects.order_by("-date_joined")[:5]:
        recent_activities.append(
            {
                "type": "signup",
                "user": user,
                "timestamp": user.date_joined,
                "detail": f"{user.username} 사용자가 가입했습니다.",
            }
        )

    # 최근 수강 신청
    for enrollment in Enrollment.objects.order_by("-enrolled_at")[:5]:
        recent_activities.append(
            {
                "type": "enrollment",
                "user": enrollment.student,
                "timestamp": enrollment.enrolled_at,
                "detail": f"{enrollment.student.username}님이 '{enrollment.course.title}' 강의를 수강 신청했습니다.",
            }
        )

    # 최근 리뷰
    for review in Review.objects.order_by("-created_at")[:5]:
        recent_activities.append(
            {
                "type": "review",
                "user": review.user,
                "timestamp": review.created_at,
                "detail": f"{review.user.username}님이 '{review.course.title}' 강의에 {review.rating}점 리뷰를 남겼습니다.",
            }
        )

    # 최근 결제
    for payment in Payment.objects.filter(status="paid").order_by("-created_at")[:5]:
        recent_activities.append(
            {
                "type": "payment",
                "user": payment.user,
                "timestamp": payment.created_at,
                "detail": f"{payment.user.username}님이 {payment.amount}원 결제를 완료했습니다.",
            }
        )

    # 타임스탬프로 정렬
    recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
    context["recent_activities"] = recent_activities[:10]  # 최근 10개만

    return render(request, "admin/analytics.html", context)


@staff_member_required
def admin_user_analytics(request):
    """사용자 분석 페이지"""
    from django.shortcuts import render

    # 사용자 역할별 통계
    role_stats = {
        "students": User.objects.filter(role=User.Role.STUDENT).count(),
        "instructors": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "managers": User.objects.filter(role=User.Role.MANAGER).count(),
    }

    # 전체 사용자 수
    total_users = sum(role_stats.values())

    # 역할별 비율 계산
    role_percentages = {
        "students_percent": (
            role_stats["students"] / total_users * 100 if total_users > 0 else 0
        ),
        "instructors_percent": (
            role_stats["instructors"] / total_users * 100 if total_users > 0 else 0
        ),
        "managers_percent": (
            role_stats["managers"] / total_users * 100 if total_users > 0 else 0
        ),
    }

    # 사용자 등록 추이 (월별)
    from django.db.models.functions import TruncMonth

    monthly_signups = (
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # 활성 사용자 통계
    active_students = (
        User.objects.filter(role=User.Role.STUDENT)
        .annotate(enrollment_count=Count("enrollments"))
        .filter(enrollment_count__gt=0)
        .count()
    )

    # 강사 통계
    instructor_stats = {
        "total": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "with_courses": User.objects.filter(role=User.Role.INSTRUCTOR)
        .annotate(course_count=Count("course"))
        .filter(course_count__gt=0)
        .count(),
        "approval_pending": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).count(),
    }

    # 최근 활동적인 사용자
    active_users = (
        User.objects.annotate(
            last_login_days=timezone.now() - F("last_login"),
            enrollment_count=Count("enrollments", distinct=True),
            review_count=Count("reviews", distinct=True),
        )
        .exclude(last_login=None)
        .order_by("last_login_days")[:10]
    )

    context = {
        "role_stats": role_stats,
        "role_percentages": role_percentages,
        "total_users": total_users,
        "monthly_signups": monthly_signups,
        "active_students": active_students,
        "instructor_stats": instructor_stats,
        "active_users": active_users,
    }

    return render(request, "admin/user_analytics.html", context)
