from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from .views import home_view
from .admin_views import admin_dashboard_data
from . import urls_admin

# Courses app의 API 뷰셋 가져오기
from courses.views import CourseViewSet, SectionViewSet, LessonViewSet
from quizzes.views import QuizViewSet

# API 라우터 설정
router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"sections", SectionViewSet)
router.register(r"lessons", LessonViewSet)

# Swagger 문서 스키마 뷰 설정
schema_view = get_schema_view(
    openapi.Info(
        title="DevRunDev API",
        default_version="v1",
        description="DevRunDev 플랫폼을 위한 API 문서",
        terms_of_service="https://www.devrundev.com/terms/",
        contact=openapi.Contact(email="contact@devrundev.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    # API 엔드포인트 (전역 레벨에서 정의)
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    # 앱별 URL
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("courses/", include("courses.urls")),
    path("quizzes/", include("quizzes.urls")),
    path("enrollments/", include("enrollments.urls")),
    path("reviews/", include("reviews.urls")),
    path("qna/", include("qna.urls")),
    path("admin-dashboard/", include(urls_admin.urlpatterns)),
    path("admin/dashboard-data/", admin_dashboard_data, name="admin-dashboard-data"),
    # Swagger 문서 URL
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "api/quiz/<int:pk>/start-attempt/",
        QuizViewSet.as_view({"post": "start_attempt"}),
        name="quiz-start-attempt",
    ),
    path(
        "api/quiz/<int:pk>/submit-attempt/",
        QuizViewSet.as_view({"post": "submit_attempt"}),
        name="quiz-submit-attempt",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
