# enrollments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EnrollmentViewSet,
    LessonProgressViewSet,
    CertificateViewSet,
    CartItemViewSet,
    cart_view,
    my_courses_view,
)

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"progress", LessonProgressViewSet)
router.register(r"certificates", CertificateViewSet)
router.register(r"cart", CartItemViewSet)

app_name = "enrollments"

urlpatterns = [
    path("", include(router.urls)),
    path("cart/", cart_view, name="cart"),
    path("my-courses/", my_courses_view, name="my_courses"),
]
