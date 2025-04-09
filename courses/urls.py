from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # API 뷰셋
    CourseViewSet,
    SectionViewSet,
    LessonViewSet,
    # 템플릿 뷰
    CourseListView,
    CourseDetailView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    SectionCreateView,
    SectionUpdateView,
    SectionDeleteView,
    LessonCreateView,
    LessonUpdateView,
    LessonDeleteView,
    LessonDetailView,
    InstructorDashboardView,
    SearchCoursesView,
)

# API 라우터 설정
router = DefaultRouter()
router.register(r"api/courses", CourseViewSet)
router.register(r"api/sections", SectionViewSet)
router.register(r"api/lessons", LessonViewSet)

app_name = "courses"

urlpatterns = [
    # API 엔드포인트
    path("", include(router.urls)),
    # 템플릿 기반 URL
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/create/", CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course-edit"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course-delete"),
    path("sections/create/", SectionCreateView.as_view(), name="section-create"),
    path("sections/<int:pk>/edit/", SectionUpdateView.as_view(), name="section-edit"),
    path(
        "sections/<int:pk>/delete/", SectionDeleteView.as_view(), name="section-delete"
    ),
    path("lessons/create/", LessonCreateView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson-edit"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson-delete"),
    path(
        "instructor/dashboard/",
        InstructorDashboardView.as_view(),
        name="instructor-dashboard",
    ),
    path(
        "instructor/reviews/",
        InstructorDashboardView.as_view(),
        name="instructor-reviews",
    ),
    path("search/", SearchCoursesView.as_view(), name="search"),
]
