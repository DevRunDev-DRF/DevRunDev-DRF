from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "qna"

# API용 라우터 설정
router = DefaultRouter()
router.register(r"questions", views.QuestionViewSet, basename="question-api")
router.register(r"answers", views.AnswerViewSet, basename="answer-api")

urlpatterns = [
    # API 경로
    path("api/", include(router.urls)),
    # 질문 관련 템플릿 뷰
    path("", views.question_list_view, name="question-list"),
    path(
        "course/<int:course_id>/", views.question_list_view, name="question-list-course"
    ),
    path("<int:pk>/", views.question_detail_view, name="question-detail"),
    path("create/", views.question_create_view, name="question-create"),
    path(
        "create/course/<int:course_id>/",
        views.question_create_view,
        name="question-create-course",
    ),
    path("<int:pk>/edit/", views.question_edit_view, name="question-edit"),
    path("<int:pk>/delete/", views.question_delete_view, name="question-delete"),
    # 답변 관련 템플릿 뷰
    path("answer/<int:pk>/edit/", views.answer_edit_view, name="answer-edit"),
    path("answer/<int:pk>/delete/", views.answer_delete_view, name="answer-delete"),
    path("answer/<int:pk>/accept/", views.answer_accept_view, name="answer-accept"),
    path(
        "answer/<int:pk>/unaccept/", views.answer_unaccept_view, name="answer-unaccept"
    ),
    path(
        "<int:pk>/mark-resolved/",
        views.question_mark_resolved_view,
        name="question-mark-resolved",
    ),
    path(
        "<int:pk>/mark-unresolved/",
        views.question_mark_unresolved_view,
        name="question-mark-unresolved",
    ),
]
