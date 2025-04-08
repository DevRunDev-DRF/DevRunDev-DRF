from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import QuizViewSet, QuestionViewSet, QuizAttemptViewSet

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet)
router.register(r"questions", QuestionViewSet)
router.register(r"attempts", QuizAttemptViewSet)

app_name = "quizzes"

urlpatterns = [
    path("", include(router.urls)),
]
