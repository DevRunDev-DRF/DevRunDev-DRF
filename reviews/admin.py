from django.contrib import admin
from django.utils.html import format_html

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "user",
        "get_rating_stars",
        "comment_preview",
        "created_at",
        "updated_at",
        "review_actions",
    )
    list_filter = ("rating", "created_at", "course")
    search_fields = ("comment", "user__username", "user__email", "course__title")
    readonly_fields = ("created_at", "updated_at")
    actions = ["delete_selected_reviews"]

    fieldsets = (
        ("리뷰 정보", {"fields": ("course", "user", "rating", "comment")}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def get_rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        colors = {
            1: "#ffcdd2",  # 연한 빨강
            2: "#ffecb3",  # 연한 노랑
            3: "#fff9c4",  # 연한 노랑
            4: "#c8e6c9",  # 연한 초록
            5: "#a5d6a7",  # 초록
        }
        return format_html(
            '<span style="color: {}; font-size: 1.2em;">{}</span>',
            colors.get(obj.rating, "#000000"),
            stars,
        )

    get_rating_stars.short_description = "평점"

    def comment_preview(self, obj):
        if len(obj.comment) > 50:
            return f"{obj.comment[:50]}..."
        return obj.comment

    comment_preview.short_description = "리뷰 내용"

    def review_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">삭제</a>',
            f"/admin/reviews/review/{obj.pk}/delete/",
        )

    review_actions.short_description = "리뷰 관리"

    def delete_selected_reviews(self, request, queryset):
        # 리뷰 삭제 시, 자동으로 관련 강의의 평점을 업데이트하는 로직이 모델에 구현되어 있음
        queryset.delete()
        self.message_user(request, f"{queryset.count()}개의 리뷰가 삭제되었습니다.")

    delete_selected_reviews.short_description = "선택된 리뷰 삭제"
