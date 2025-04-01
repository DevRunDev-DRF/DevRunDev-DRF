from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    InstructorApplicationViewSet,
    RegisterView,
    LoginView,
    LogoutView,
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
]
