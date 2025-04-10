from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    QuizViewSet,
    QuestionViewSet,
    QuizAttemptViewSet,
    QuizCreateView,
    QuizUpdateView,
    QuizDeleteView,
    QuizDetailView,
    QuizListView,
    QuizAttemptView,
    QuizResultView,
    QuizSubmitView,
    QuestionCreateView,
    QuestionUpdateView,
    QuestionDeleteView,
)

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"attempts", QuizAttemptViewSet)

app_name = "quizzes"

urlpatterns = [
    # REST API 엔드포인트
    path("api/", include(router.urls)),
    # 웹 페이지 URL
    path("quiz/", QuizListView.as_view(), name="quiz-list"),
    path("quiz/create/", QuizCreateView.as_view(), name="quiz-create"),
    path("quiz/<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/<int:pk>/edit/", QuizUpdateView.as_view(), name="quiz-edit"),
    path("quiz/<int:pk>/delete/", QuizDeleteView.as_view(), name="quiz-delete"),
    path("quiz/<int:pk>/attempt/", QuizAttemptView.as_view(), name="quiz-attempt"),
    path("quiz/<int:pk>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("quiz/<int:pk>/result/", QuizResultView.as_view(), name="quiz-result"),
    path("question/create/", QuestionCreateView.as_view(), name="question-create"),
    path("question/<int:pk>/edit/", QuestionUpdateView.as_view(), name="question-edit"),
    path(
        "question/<int:pk>/delete/",
        QuestionDeleteView.as_view(),
        name="question-delete",
    ),
]
