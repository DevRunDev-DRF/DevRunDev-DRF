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
    PaymentPrepareView,
    PaymentVerifyView,
    PaymentCancelView,
    checkout_free_course,
    print_certificate_view,
    # 결제 취소 관련 새 뷰 함수
    payment_list_view,
    payment_cancel_request,
    payment_cancel_view,
    payment_cancel_complete_view,
)

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"progress", LessonProgressViewSet)
router.register(r"certificates", CertificateViewSet)
router.register(r"cart", CartItemViewSet)

app_name = "enrollments"

urlpatterns = [
    path("", include(router.urls)),
    path("cart-view/", cart_view, name="cart-view"),
    path("my-courses/", my_courses_view, name="my_courses"),
    path("cart/<int:item_id>/delete/", delete_cart_item, name="delete-cart-item"),
    path("my-certificates/", certificate_view, name="my_certificates"),
    path(
        "certificate/<str:certificate_id>/", certificate_view, name="certificate_detail"
    ),
    path("payments/prepare/", PaymentPrepareView.as_view(), name="payment-prepare"),
    path("payments/verify/", PaymentVerifyView.as_view(), name="payment-verify"),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
    path("checkout-free/", checkout_free_course, name="checkout-free"),
    path(
        "certificate/<str:certificate_id>/print/",
        print_certificate_view,
        name="certificate_print",
    ),
    # 결제 취소 관련 새 URL 패턴
    path("my-payments/", payment_list_view, name="payment-list"),
    path(
        "payment/<int:payment_id>/cancel-request/",
        payment_cancel_request,
        name="payment-cancel-request",
    ),
    path("payment/cancel/", payment_cancel_view, name="payment-cancel"),
    path(
        "payment/<int:payment_id>/cancel-complete/",
        payment_cancel_complete_view,
        name="payment-cancel-complete",
    ),
]
