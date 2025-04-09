from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet)

app_name = "reviews"

urlpatterns = [
    path("", include(router.urls)),
]
