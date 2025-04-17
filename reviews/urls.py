from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet,
    review_edit_view,
    review_delete_view,
)

router = DefaultRouter()
router.register(r"", ReviewViewSet)

app_name = "reviews"

urlpatterns = [
    path("", include(router.urls)),
    path("<int:review_id>/edit/", review_edit_view, name="review-edit"),
    path("<int:review_id>/delete/", review_delete_view, name="review-delete"),
]
