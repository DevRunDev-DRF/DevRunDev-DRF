from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    InstructorApplicationViewSet,
    RegisterView,
    LoginView,
    LogoutView,
    profile_view,
    instructor_application_form,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"instructor-applications", InstructorApplicationViewSet)

app_name = "accounts"

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path(
        "instructor-application-form/",
        instructor_application_form,
        name="instructor_application_form",
    ),
    path(
        "user/me/",
        UserViewSet.as_view({"patch": "update_me", "put": "update_me"}),
        name="user-update_me",
    ),
]
