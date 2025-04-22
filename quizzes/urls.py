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

# API를 위한 라우터는 제거 (메인 urls.py에서 이미 처리)
# router = DefaultRouter()
# router.register(r"api/quizzes", QuizViewSet, basename="quiz")
# router.register(r"api/questions", QuestionViewSet, basename="question")
# router.register(r"api/attempts", QuizAttemptViewSet, basename="quizattempt")

urlpatterns = [
    # 템플릿 기반 URL
    path("", QuizListView.as_view(), name="quiz-list"),
    path("create/", QuizCreateView.as_view(), name="quiz-create"),
    path("<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:pk>/edit/", QuizUpdateView.as_view(), name="quiz-edit"),
    path("<int:pk>/delete/", QuizDeleteView.as_view(), name="quiz-delete"),
    path("<int:pk>/attempt/", QuizAttemptView.as_view(), name="quiz-attempt"),
    path("<int:pk>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("<int:pk>/result/", QuizResultView.as_view(), name="quiz-result"),
    path("question/create/", QuestionCreateView.as_view(), name="question-create"),
    path("question/<int:pk>/edit/", QuestionUpdateView.as_view(), name="question-edit"),
    path(
        "question/<int:pk>/delete/",
        QuestionDeleteView.as_view(),
        name="question-delete",
    ),
    # API URL 패턴은 모두 제거 (메인 urls.py에서 이미 처리)
    # 다음 행들을 제거 또는 주석 처리
    # path("api/", include(router.urls)),
    # path(
    #    "api/quiz/<int:pk>/start-attempt/",
    #    QuizViewSet.as_view({"post": "start_attempt"}),
    #    name="quiz-start-attempt",
    # ),
    # path(
    #    "api/quiz/<int:pk>/submit-attempt/",
    #    QuizViewSet.as_view({"post": "submit_attempt"}),
    #    name="quiz-submit-attempt",
    # ),
]
