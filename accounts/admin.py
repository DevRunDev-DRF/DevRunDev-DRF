from django.contrib import admin

from .models import InstructorApplication, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "is_staff",
    )


@admin.register(InstructorApplication)
class InstructorApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "updated_at")
    list_filter = ("status",)
    actions = ["approve_applications", "reject_applications"]

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
