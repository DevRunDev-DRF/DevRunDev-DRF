from django.urls import path
from . import views

urlpatterns = [
    path("test/courses/", views.test_course_list, name="test-course-list"),
    path("test/courses/<int:pk>/", views.test_course_detail, name="test-course-detail"),
]
