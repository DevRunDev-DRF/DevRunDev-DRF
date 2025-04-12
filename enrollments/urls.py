from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EnrollmentViewSet,
    LessonProgressViewSet,
    CertificateViewSet,
    CartItemViewSet,
    cart_view,
    my_courses_view,
    delete_cart_item,
    certificate_view,
)

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"progress", LessonProgressViewSet)
router.register(r"certificates", CertificateViewSet)
router.register(r"cart", CartItemViewSet)

app_name = "enrollments"

urlpatterns = [
    path("", include(router.urls)),
    # 템플릿 뷰 경로 추가/수정
    path("cart-view/", cart_view, name="cart-view"),  # 새 템플릿 뷰 경로
    path("my-courses/", my_courses_view, name="my_courses"),
    path("cart/<int:item_id>/delete/", delete_cart_item, name="delete-cart-item"),
    path("my-certificates/", certificate_view, name="my_certificates"),
    path(
        "certificate/<str:certificate_id>/", certificate_view, name="certificate_detail"
    ),
]
