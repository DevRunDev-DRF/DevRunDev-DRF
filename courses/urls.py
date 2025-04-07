from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, SectionViewSet, LessonViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"sections", SectionViewSet)
router.register(r"lessons", LessonViewSet)

app_name = "courses"

urlpatterns = [
    path("", include(router.urls)),
]
