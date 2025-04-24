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
    path(
        "instructor-applications/<int:application_id>/approve/",
        views_admin.approve_instructor_application,
        name="admin-instructor-approve",
    ),
    path(
        "instructor-applications/<int:application_id>/reject/",
        views_admin.reject_instructor_application,
        name="admin-instructor-reject",
    ),
    path("payments/", views_admin.admin_payments, name="admin-payments"),
]
