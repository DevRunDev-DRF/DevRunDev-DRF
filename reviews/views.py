from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from courses.models import Course
from enrollments.models import Enrollment
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewOwnerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    리뷰 관련 API 뷰셋
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "user", "rating"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_permissions(self):
        """액션에 따라 권한 다르게 설정"""
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated, IsReviewOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """리뷰 생성 시 현재 로그인한 사용자를 user로 설정"""
        course_id = self.request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        # 해당 강의를 수강 중인지 확인
        enrollment_exists = Enrollment.objects.filter(
            student=self.request.user,
            course=course,
            status__in=["in_progress", "completed"],
        ).exists()

        if not enrollment_exists:
            return Response(
                {"detail": "수강 중인 강의에 대해서만 리뷰를 작성할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 이미 리뷰를 작성했는지 확인
        if Review.objects.filter(user=self.request.user, course=course).exists():
            return Response(
                {"detail": "이미 이 강의에 대한 리뷰를 작성했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=self.request.user)

    def get_queryset(self):
        """사용자 역할에 따라 쿼리셋 필터링"""
        queryset = Review.objects.all()

        # URL에서 course_id 파라미터를 가져옴
        course_id = self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset
