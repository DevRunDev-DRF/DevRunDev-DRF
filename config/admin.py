from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.filters import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html


class DevRunDevAdminSite(AdminSite):
    """커스텀 관리자 사이트"""

    # 사이트 타이틀 설정
    site_title = _("DevRunDev 관리자")
    site_header = _("DevRunDev 관리자 페이지")
    index_title = _("DevRunDev 관리자 대시보드")

    def each_context(self, request):
        context = super().each_context(request)
        context["available_apps"] = self.get_app_list(request)

        # 대시보드 통계 데이터 추가
        from accounts.models import User, InstructorApplication
        from courses.models import Course
        from enrollments.models import Enrollment, Certificate, Payment
        from reviews.models import Review

        # 사용자 통계
        context["total_users"] = User.objects.count()
        context["students_count"] = User.objects.filter(role=User.Role.STUDENT).count()
        context["instructors_count"] = User.objects.filter(
            role=User.Role.INSTRUCTOR
        ).count()
        context["pending_instructors"] = InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).count()

        # 강의 통계
        context["total_courses"] = Course.objects.count()
        context["approved_courses"] = Course.objects.filter(status="approved").count()
        context["review_courses"] = Course.objects.filter(status="review").count()
        context["rejected_courses"] = Course.objects.filter(
            status="not_approved"
        ).count()

        # 수강 통계
        context["total_enrollments"] = Enrollment.objects.count()
        context["active_enrollments"] = Enrollment.objects.filter(
            status="in_progress"
        ).count()
        context["completed_enrollments"] = Enrollment.objects.filter(
            status="completed"
        ).count()
        context["certificates_count"] = Certificate.objects.count()

        # 리뷰 통계
        context["total_reviews"] = Review.objects.count()
        context["avg_rating"] = Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0

        # 결제 통계
        context["total_payments"] = Payment.objects.count()
        context["total_revenue"] = (
            Payment.objects.filter(status="paid").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        # 최근 활동
        context["recent_users"] = User.objects.order_by("-date_joined")[:5]
        context["recent_courses"] = Course.objects.order_by("-created_at")[:5]
        context["recent_enrollments"] = Enrollment.objects.order_by("-enrolled_at")[:5]
        context["recent_reviews"] = Review.objects.order_by("-created_at")[:5]

        # 시간별 통계
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)

        # 오늘 통계
        context["today_users"] = User.objects.filter(date_joined__date=today).count()
        context["today_enrollments"] = Enrollment.objects.filter(
            enrolled_at__date=today
        ).count()
        context["today_reviews"] = Review.objects.filter(created_at__date=today).count()
        context["today_revenue"] = (
            Payment.objects.filter(created_at__date=today, status="paid").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        # 이번 주 통계
        context["week_users"] = User.objects.filter(
            date_joined__date__gte=last_week
        ).count()
        context["week_enrollments"] = Enrollment.objects.filter(
            enrolled_at__date__gte=last_week
        ).count()
        context["week_revenue"] = (
            Payment.objects.filter(
                created_at__date__gte=last_week, status="paid"
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        # 이번 달 통계
        context["month_users"] = User.objects.filter(
            date_joined__date__gte=last_month
        ).count()
        context["month_enrollments"] = Enrollment.objects.filter(
            enrolled_at__date__gte=last_month
        ).count()
        context["month_revenue"] = (
            Payment.objects.filter(
                created_at__date__gte=last_month, status="paid"
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return context


# 기본 AdminSite 대신 커스텀 AdminSite 사용
admin.site = DevRunDevAdminSite()

# Django 기본 앱 등록
admin.site.register(Site)


# 관리자 페이지 인덱스 커스터마이징
admin.site.index_template = "admin/custom_index.html"


# 사용자 관련 필터
class UserRoleFilter(SimpleListFilter):
    title = _("사용자 역할")
    parameter_name = "role"

    def lookups(self, request, model_admin):
        from accounts.models import User

        return User.Role.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(role=self.value())
        return queryset


# 강의 관련 필터
class CourseEnrollmentCountFilter(SimpleListFilter):
    title = _("수강생 수")
    parameter_name = "enrollment_count"

    def lookups(self, request, model_admin):
        return (
            ("0", _("없음 (0명)")),
            ("1-10", _("적음 (1-10명)")),
            ("11-50", _("보통 (11-50명)")),
            ("51+", _("많음 (51명 이상)")),
        )

    def queryset(self, request, queryset):
        from django.db.models import Count

        queryset = queryset.annotate(enrollment_count=Count("enrollments"))

        if self.value() == "0":
            return queryset.filter(enrollment_count=0)
        elif self.value() == "1-10":
            return queryset.filter(enrollment_count__range=(1, 10))
        elif self.value() == "11-50":
            return queryset.filter(enrollment_count__range=(11, 50))
        elif self.value() == "51+":
            return queryset.filter(enrollment_count__gt=50)
        return queryset


class CourseRatingFilter(SimpleListFilter):
    title = _("평균 평점")
    parameter_name = "avg_rating"

    def lookups(self, request, model_admin):
        return (
            ("0-1", _("매우 낮음 (0-1점)")),
            ("1-2", _("낮음 (1-2점)")),
            ("2-3", _("보통 (2-3점)")),
            ("3-4", _("좋음 (3-4점)")),
            ("4-5", _("매우 좋음 (4-5점)")),
        )

    def queryset(self, request, queryset):
        if self.value() == "0-1":
            return queryset.filter(avg_rating__gte=0, avg_rating__lt=1)
        elif self.value() == "1-2":
            return queryset.filter(avg_rating__gte=1, avg_rating__lt=2)
        elif self.value() == "2-3":
            return queryset.filter(avg_rating__gte=2, avg_rating__lt=3)
        elif self.value() == "3-4":
            return queryset.filter(avg_rating__gte=3, avg_rating__lt=4)
        elif self.value() == "4-5":
            return queryset.filter(avg_rating__gte=4, avg_rating__lte=5)
        return queryset


# 수강 관련 필터
class EnrollmentProgressFilter(SimpleListFilter):
    title = _("진행률")
    parameter_name = "progress"

    def lookups(self, request, model_admin):
        return (
            ("0-25", _("시작 (0-25%)")),
            ("25-50", _("초반 (25-50%)")),
            ("50-75", _("중반 (50-75%)")),
            ("75-99", _("후반 (75-99%)")),
            ("100", _("완료 (100%)")),
        )

    def queryset(self, request, queryset):
        if self.value() == "0-25":
            return queryset.filter(progress__lt=25)
        elif self.value() == "25-50":
            return queryset.filter(progress__gte=25, progress__lt=50)
        elif self.value() == "50-75":
            return queryset.filter(progress__gte=50, progress__lt=75)
        elif self.value() == "75-99":
            return queryset.filter(progress__gte=75, progress__lt=100)
        elif self.value() == "100":
            return queryset.filter(progress=100)
        return queryset
