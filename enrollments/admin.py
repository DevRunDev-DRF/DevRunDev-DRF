from django.contrib import admin
from django.utils.html import format_html

from .models import Enrollment, LessonProgress, Certificate, CartItem, Payment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "course",
        "get_progress_bar",
        "status",
        "has_certificate",
        "enrolled_at",
    )
    list_filter = ("status", "enrolled_at")
    search_fields = ("student__username", "student__email", "course__title")
    readonly_fields = ("enrolled_at", "last_updated_at")
    # LessonProgressInline 제거 - 직접적인 관계가 없음
    actions = ["reset_progress_action", "issue_certificate_action"]

    fieldsets = (
        ("수강 정보", {"fields": ("student", "course", "status")}),
        ("진행 상황", {"fields": ("progress", "last_watched_lesson")}),
        ("일자 정보", {"fields": ("enrolled_at", "last_updated_at")}),
    )

    def get_progress_bar(self, obj):
        progress = float(obj.progress)
        color = "green"
        if progress < 30:
            color = "red"
        elif progress < 70:
            color = "orange"

        return format_html(
            '<div style="width:100px; height:10px; background-color:#f2f2f2; border-radius:5px;">'
            '<div style="width:{}px; height:10px; background-color:{}; border-radius:5px;"></div>'
            "</div> {:.1f}%",
            progress,
            color,
            progress,
        )

    get_progress_bar.short_description = "진행률"
    get_progress_bar.admin_order_field = "progress"

    def has_certificate(self, obj):
        try:
            certificate = obj.certificate
            return format_html(
                '<span style="color:green;">발급됨 ({})</span>',
                certificate.certificate_id,
            )
        except Certificate.DoesNotExist:
            if obj.is_course_completed():
                return format_html(
                    '<span style="color:orange;">발급 가능</span> '
                    '<a href="/admin/enrollments/enrollment/{}/issue_certificate/">발급</a>',
                    obj.id,
                )
            return format_html('<span style="color:red;">미발급</span>')

    has_certificate.short_description = "수료증"

    def reset_progress_action(self, request, queryset):
        for enrollment in queryset:
            enrollment.reset_progress()
        self.message_user(
            request, f"{queryset.count()}개의 수강 진행률이 초기화되었습니다."
        )

    reset_progress_action.short_description = "선택된 수강 진행률 초기화"

    def issue_certificate_action(self, request, queryset):
        count = 0
        for enrollment in queryset:
            if enrollment.is_course_completed():
                enrollment.generate_certificate()
                count += 1

        if count:
            self.message_user(request, f"{count}개의 수료증이 발급되었습니다.")
        else:
            self.message_user(
                request, f"수강 완료된 강의가 없어 수료증을 발급할 수 없습니다."
            )

    issue_certificate_action.short_description = "선택된 수강에 수료증 발급"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:enrollment_id>/issue_certificate/",
                self.admin_site.admin_view(self.issue_certificate),
                name="issue-certificate",
            ),
        ]
        return custom_urls + urls

    def issue_certificate(self, request, enrollment_id):
        from django.shortcuts import redirect

        enrollment = Enrollment.objects.get(pk=enrollment_id)
        certificate = enrollment.generate_certificate()
        if certificate:
            self.message_user(
                request,
                f"{enrollment.student.username}님의 '{enrollment.course.title}' 수료증이 발급되었습니다.",
            )
        else:
            self.message_user(
                request, f"수강 완료되지 않아 수료증을 발급할 수 없습니다."
            )
        return redirect("admin:enrollments_enrollment_changelist")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "lesson",
        "get_course",
        "completed",
        "completed_at",
        "last_watched_at",
    )
    list_filter = ("completed", "completed_at", "last_watched_at")
    search_fields = ("student__username", "student__email", "lesson__title")
    readonly_fields = ("completed_at", "last_watched_at")
    actions = ["mark_completed_action", "mark_incomplete_action"]

    def get_course(self, obj):
        return obj.lesson.section.course

    get_course.short_description = "강의"
    get_course.admin_order_field = "lesson__section__course"

    def mark_completed_action(self, request, queryset):
        for progress in queryset:
            progress.mark_completed()
        self.message_user(
            request, f"{queryset.count()}개의 레슨 진행 상태가 완료로 변경되었습니다."
        )

    mark_completed_action.short_description = "선택된 레슨을 완료로 표시"

    def mark_incomplete_action(self, request, queryset):
        queryset.update(completed=False, completed_at=None)
        self.message_user(
            request, f"{queryset.count()}개의 레슨 진행 상태가 미완료로 변경되었습니다."
        )

    mark_incomplete_action.short_description = "선택된 레슨을 미완료로 표시"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enrollment",
        "get_student",
        "get_course",
        "certificate_id",
        "issued_at",
    )
    list_filter = ("issued_at",)
    search_fields = (
        "enrollment__student__username",
        "enrollment__student__email",
        "enrollment__course__title",
        "certificate_id",
    )
    readonly_fields = ("certificate_id", "issued_at")

    def get_student(self, obj):
        return obj.enrollment.student

    get_student.short_description = "학생"
    get_student.admin_order_field = "enrollment__student"

    def get_course(self, obj):
        return obj.enrollment.course

    get_course.short_description = "강의"
    get_course.admin_order_field = "enrollment__course"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__username", "user__email", "course__title")
    readonly_fields = ("added_at",)

    actions = ["checkout_cart_items"]

    def checkout_cart_items(self, request, queryset):
        from django.db import transaction

        with transaction.atomic():
            enrolled_count = 0
            for cart_item in queryset:
                # 이미 수강 중인지 확인
                enrollment_exists = Enrollment.objects.filter(
                    student=cart_item.user, course=cart_item.course
                ).exists()

                if not enrollment_exists:
                    Enrollment.objects.create(
                        student=cart_item.user,
                        course=cart_item.course,
                        status="in_progress",
                        progress=0,
                    )
                    enrolled_count += 1

            # 카트 아이템 삭제
            queryset.delete()

        self.message_user(request, f"{enrolled_count}개의 강의가 수강 신청되었습니다.")

    checkout_cart_items.short_description = "선택된 항목으로 수강 신청하기"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "merchant_uid",
        "amount",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "merchant_uid", "imp_uid")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "결제 정보",
            {"fields": ("user", "merchant_uid", "imp_uid", "amount", "status")},
        ),
        ("장바구니 항목", {"fields": ("cart_items",)}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )
