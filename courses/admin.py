from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Course, Section, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "video_url", "order")


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ("title", "order")
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "instructor",
        "price",
        "get_status_display",
        "avg_rating",
        "get_thumbnail_preview",
        "created_at",
        "course_actions",
    )
    list_filter = ("status", "created_at", "avg_rating")
    search_fields = (
        "title",
        "description",
        "instructor__username",
        "instructor__email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "avg_rating",
        "get_thumbnail_preview",
    )
    inlines = [SectionInline]
    actions = ["approve_courses", "reject_courses", "mark_for_review"]

    fieldsets = (
        ("기본 정보", {"fields": ("title", "description", "instructor", "price")}),
        ("상태 정보", {"fields": ("status", "avg_rating")}),
        ("이미지", {"fields": ("thumbnail", "get_thumbnail_preview")}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def get_status_display(self, obj):
        status_colors = {
            "review": "orange",
            "approved": "green",
            "not_approved": "red",
        }
        color = status_colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_status_display()
        )

    get_status_display.short_description = "상태"
    get_status_display.admin_order_field = "status"

    def get_thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="auto" style="object-fit: cover; border-radius: 5px;" />',
                obj.thumbnail.url,
            )
        return "이미지 없음"

    get_thumbnail_preview.short_description = "썸네일 미리보기"

    def course_actions(self, obj):
        if obj.status == "review":
            return format_html(
                '<a class="button" href="{}">승인</a>&nbsp;'
                '<a class="button" href="{}">거부</a>',
                f"/admin/courses/course/{obj.pk}/approve/",
                f"/admin/courses/course/{obj.pk}/reject/",
            )
        elif obj.status == "approved":
            return format_html(
                '<a class="button" href="{}">심사중으로 변경</a>',
                f"/admin/courses/course/{obj.pk}/review/",
            )
        else:  # not_approved
            return format_html(
                '<a class="button" href="{}">심사중으로 변경</a>',
                f"/admin/courses/course/{obj.pk}/review/",
            )

    course_actions.short_description = "강의 처리"

    def approve_courses(self, request, queryset):
        queryset.update(status="approved")
        self.message_user(request, f"{queryset.count()}개의 강의가 승인되었습니다.")

    approve_courses.short_description = "선택된 강의 승인"

    def reject_courses(self, request, queryset):
        queryset.update(status="not_approved")
        self.message_user(request, f"{queryset.count()}개의 강의가 거부되었습니다.")

    reject_courses.short_description = "선택된 강의 거부"

    def mark_for_review(self, request, queryset):
        queryset.update(status="review")
        self.message_user(
            request, f"{queryset.count()}개의 강의가 검토 대기중으로 변경되었습니다."
        )

    mark_for_review.short_description = "선택된 강의를 검토 대기중으로 변경"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:course_id>/approve/",
                self.admin_site.admin_view(self.approve_course),
                name="approve-course",
            ),
            path(
                "<int:course_id>/reject/",
                self.admin_site.admin_view(self.reject_course),
                name="reject-course",
            ),
            path(
                "<int:course_id>/review/",
                self.admin_site.admin_view(self.review_course),
                name="review-course",
            ),
        ]
        return custom_urls + urls

    def approve_course(self, request, course_id):
        from django.shortcuts import redirect

        course = Course.objects.get(pk=course_id)
        course.status = "approved"
        course.save()
        self.message_user(request, f"{course.title} 강의가 승인되었습니다.")
        return redirect("admin:courses_course_changelist")

    def reject_course(self, request, course_id):
        from django.shortcuts import redirect

        course = Course.objects.get(pk=course_id)
        course.status = "not_approved"
        course.save()
        self.message_user(request, f"{course.title} 강의가 거부되었습니다.")
        return redirect("admin:courses_course_changelist")

    def review_course(self, request, course_id):
        from django.shortcuts import redirect

        course = Course.objects.get(pk=course_id)
        course.status = "review"
        course.save()
        self.message_user(
            request, f"{course.title} 강의가 검토 대기중으로 변경되었습니다."
        )
        return redirect("admin:courses_course_changelist")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order", "get_lessons_count")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    inlines = [LessonInline]

    def get_lessons_count(self, obj):
        count = obj.lessons.count()
        return format_html(
            '<span style="background-color: #f2f2f2; padding: 2px 6px; border-radius: 10px;">{}</span>',
            count,
        )

    get_lessons_count.short_description = "레슨 수"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "section",
        "get_course",
        "order",
        "get_video_preview",
    )
    list_filter = ("section__course",)
    search_fields = ("title", "section__title", "section__course__title")

    def get_course(self, obj):
        return obj.section.course

    get_course.short_description = "강의"
    get_course.admin_order_field = "section__course"

    def get_video_preview(self, obj):
        if obj.video_url and "youtube.com/embed/" in obj.video_url:
            video_id = obj.video_url.split("/")[-1].split("?")[0]
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
            return format_html(
                '<img src="{}" width="120" height="auto" style="border-radius: 5px;" />',
                thumbnail_url,
            )
        return "비디오 없음"

    get_video_preview.short_description = "비디오 미리보기"
