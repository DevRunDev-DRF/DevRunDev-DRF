from django.urls import path
from . import views_admin

urlpatterns = [
    path("dashboard/", views_admin.admin_dashboard, name="admin-dashboard"),
    path("users/", views_admin.admin_users, name="admin-users"),
    path("courses/", views_admin.admin_courses, name="admin-courses"),
    path(
        "instructor-applications/",
        views_admin.admin_instructor_applications,
        name="admin-instructor-applications",
    ),
    path("payments/", views_admin.admin_payments, name="admin-payments"),
]
