from django.urls import path

from .views import (
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
    CourseCreateWithContentView,
)

app_name = "courses"

urlpatterns = [
    # 템플릿 기반 URL (웹 페이지용)
    path("", CourseListView.as_view(), name="course-list"),
    path("create/", CourseCreateView.as_view(), name="course-create"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("<int:pk>/edit/", CourseUpdateView.as_view(), name="course-edit"),
    path("<int:pk>/delete/", CourseDeleteView.as_view(), name="course-delete"),
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
    path(
        "create-with-content/",
        CourseCreateWithContentView.as_view(),
        name="course-create-with-content",
    ),
]
