from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import InstructorApplication, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "get_role_display",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("username", "first_name", "last_name")}),
        (
            "권한",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        ("중요 일자", {"fields": ("last_login", "date_joined")}),
        ("권한 그룹", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "role"),
            },
        ),
    )

    def get_role_display(self, obj):
        role_colors = {
            "Student": "blue",
            "Instructor": "green",
            "manager": "red",
        }
        color = role_colors.get(obj.role, "gray")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_role_display()
        )

    get_role_display.short_description = "역할"
    get_role_display.admin_order_field = "role"


@admin.register(InstructorApplication)
class InstructorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_email",
        "status",
        "created_at",
        "updated_at",
        "application_actions",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "qualifications", "experience")
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_applications", "reject_applications"]

    fieldsets = (
        ("신청자 정보", {"fields": ("user",)}),
        ("신청 내용", {"fields": ("qualifications", "experience", "sample_video_url")}),
        ("처리 상태", {"fields": ("status",)}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "이메일"
    user_email.admin_order_field = "user__email"

    def application_actions(self, obj):
        if obj.status == InstructorApplication.Status.PENDING:
            return format_html(
                '<a class="button" href="{}">승인</a>&nbsp;'
                '<a class="button" href="{}">거부</a>',
                f"/admin/accounts/instructorapplication/{obj.pk}/approve/",
                f"/admin/accounts/instructorapplication/{obj.pk}/reject/",
            )
        elif obj.status == InstructorApplication.Status.APPROVED:
            return "승인됨"
        else:
            return "거부됨"

    application_actions.short_description = "신청 처리"

    def approve_applications(self, request, queryset):
        for application in queryset:
            application.approve()
        self.message_user(
            request, f"{queryset.count()}개의 강사 신청이 승인되었습니다."
        )

    approve_applications.short_description = "선택된 강사 신청을 승인"

    def reject_applications(self, request, queryset):
        queryset.update(status=InstructorApplication.Status.REJECTED)
        self.message_user(
            request, f"{queryset.count()}개의 강사 신청이 거부되었습니다."
        )

    reject_applications.short_description = "선택된 강사 신청을 거부"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:application_id>/approve/",
                self.admin_site.admin_view(self.approve_application),
                name="approve-instructor-application",
            ),
            path(
                "<int:application_id>/reject/",
                self.admin_site.admin_view(self.reject_application),
                name="reject-instructor-application",
            ),
        ]
        return custom_urls + urls

    def approve_application(self, request, application_id):
        from django.shortcuts import redirect

        application = InstructorApplication.objects.get(pk=application_id)
        application.approve()
        self.message_user(
            request, f"{application.user.username}의 강사 신청이 승인되었습니다."
        )
        return redirect("admin:accounts_instructorapplication_changelist")

    def reject_application(self, request, application_id):
        from django.shortcuts import redirect

        application = InstructorApplication.objects.get(pk=application_id)
        application.status = InstructorApplication.Status.REJECTED
        application.save()
        self.message_user(
            request, f"{application.user.username}의 강사 신청이 거부되었습니다."
        )
        return redirect("admin:accounts_instructorapplication_changelist")
