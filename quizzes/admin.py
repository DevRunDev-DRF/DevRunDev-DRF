from django.contrib import admin
from django.utils.html import format_html

from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    fields = ("text", "is_correct")


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ("text", "order")
    show_change_link = True


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("question", "selected_choice", "is_correct")
    readonly_fields = ("is_correct",)
    can_delete = False


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "section",
        "lesson",
        "instructor",
        "get_questions_count",
        "get_attempts_count",
        "created_at",
    )
    list_filter = ("course", "created_at")
    search_fields = ("title", "description", "course__title", "instructor__username")
    inlines = [QuestionInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("기본 정보", {"fields": ("title", "description", "instructor")}),
        ("강의 연결", {"fields": ("course", "section", "lesson")}),
        ("일자 정보", {"fields": ("created_at", "updated_at")}),
    )

    def get_questions_count(self, obj):
        count = obj.questions.count()
        return format_html(
            '<span style="background-color: #e6f7ff; padding: 2px 6px; border-radius: 10px;">{}</span>',
            count,
        )

    get_questions_count.short_description = "문제 수"

    def get_attempts_count(self, obj):
        count = obj.attempts.count()
        return format_html(
            '<span style="background-color: #f6ffed; padding: 2px 6px; border-radius: 10px;">{}</span>',
            count,
        )

    get_attempts_count.short_description = "시도 수"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text_preview",
        "quiz",
        "order",
        "get_choices_count",
        "get_correct_answer",
    )
    list_filter = ("quiz__course",)
    search_fields = ("text", "quiz__title")
    inlines = [ChoiceInline]

    def text_preview(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text

    text_preview.short_description = "문제"

    def get_choices_count(self, obj):
        count = obj.choices.count()
        return count

    get_choices_count.short_description = "선택지 수"

    def get_correct_answer(self, obj):
        correct_choices = obj.choices.filter(is_correct=True)
        if correct_choices.exists():
            return format_html(
                '<span style="color: green;">{}</span>', correct_choices.first().text
            )
        return format_html('<span style="color: red;">정답 없음</span>')

    get_correct_answer.short_description = "정답"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "student",
        "get_score_display",
        "correct_answers",
        "total_questions",
        "is_completed",
        "started_at",
        "completed_at",
    )
    list_filter = ("is_completed", "started_at", "quiz__course")
    search_fields = ("student__username", "student__email", "quiz__title")
    readonly_fields = (
        "started_at",
        "completed_at",
        "score",
        "correct_answers",
        "total_questions",
    )
    inlines = [AnswerInline]

    fieldsets = (
        ("시도 정보", {"fields": ("quiz", "student", "is_completed")}),
        ("점수 정보", {"fields": ("score", "correct_answers", "total_questions")}),
        ("일자 정보", {"fields": ("started_at", "completed_at")}),
    )

    def get_score_display(self, obj):
        score = obj.score
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "orange"
        else:
            color = "red"

        return format_html(
            '<div style="width:100px; height:10px; background-color:#f2f2f2; border-radius:5px;">'
            '<div style="width:{}px; height:10px; background-color:{}; border-radius:5px;"></div>'
            "</div> {}점",
            score,
            color,
            score,
        )

    get_score_display.short_description = "점수"
    get_score_display.admin_order_field = "score"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt", "question", "selected_choice", "is_correct")
    list_filter = ("is_correct", "attempt__quiz")
    search_fields = (
        "attempt__student__username",
        "attempt__student__email",
        "question__text",
    )
    readonly_fields = ("is_correct",)
