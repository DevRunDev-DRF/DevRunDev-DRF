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

app_name = "quizzes"

# API를 위한 라우터
router = DefaultRouter()
router.register(r"api/quizzes", QuizViewSet, basename="quiz")
router.register(r"api/questions", QuestionViewSet, basename="question")
router.register(r"api/attempts", QuizAttemptViewSet, basename="quizattempt")

urlpatterns = [
    # 템플릿 기반 URL
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
    # API 액션 URL
    path(
        "api/quiz/<int:pk>/start-attempt/",
        QuizViewSet.as_view({"post": "start_attempt"}),
        name="quiz-start-attempt",
    ),
    path(
        "api/quiz/<int:pk>/submit-attempt/",
        QuizViewSet.as_view({"post": "submit_attempt"}),
        name="quiz-submit-attempt",
    ),
    # 라우터 URL 포함
    path("", include(router.urls)),
]
