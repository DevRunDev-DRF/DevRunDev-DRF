from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("user", "content", "is_accepted", "created_at")
    readonly_fields = ("created_at",)
    can_delete = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "course",
        "lesson",
        "get_resolved_status",
        "created_at",
        "answer_count",
    )
    list_filter = ("is_resolved", "created_at", "course")
    search_fields = ("title", "content", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [AnswerInline]

    fieldsets = (
        (
            "질문 정보",
            {"fields": ("user", "course", "lesson", "title", "content", "is_resolved")},
        ),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def get_resolved_status(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color: green;">해결됨</span>')
        return format_html('<span style="color: red;">미해결</span>')

    get_resolved_status.short_description = "해결 상태"

    def answer_count(self, obj):
        count = obj.answers.count()
        return format_html(
            '<span style="background-color: #f2f2f2; padding: 2px 6px; border-radius: 10px;">{}</span>',
            count,
        )

    answer_count.short_description = "답변 수"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question_title", "user", "get_accepted_status", "created_at")
    list_filter = ("is_accepted", "created_at", "question__course")
    search_fields = ("content", "user__username", "user__email", "question__title")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("답변 정보", {"fields": ("question", "user", "content", "is_accepted")}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def question_title(self, obj):
        return obj.question.title

    question_title.short_description = "질문 제목"

    def get_accepted_status(self, obj):
        if obj.is_accepted:
            return format_html('<span style="color: green;">채택됨</span>')
        return format_html('<span style="color: gray;">미채택</span>')

    get_accepted_status.short_description = "채택 상태"
