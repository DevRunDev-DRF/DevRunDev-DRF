from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Course, Section, Lesson
from .permissions import IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    SectionSerializer,
    LessonSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    강의 관련 API 뷰셋
    """

    queryset = Course.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "instructor"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "price", "avg_rating"]
    ordering = ["-created_at"]
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        queryset = Course.objects.all()

        # 승인된 강의만 조회 (강사가 자신의 강의 조회 시에는 모든 상태 조회 가능)
        if self.request.user.is_authenticated and self.request.user.is_instructor():
            if self.action == "list":
                instructor_id = self.request.query_params.get("instructor")
                if instructor_id and int(instructor_id) == self.request.user.id:
                    return queryset

        # 일반 사용자에게는 승인된 강의만 보여줌
        return queryset.filter(status="approved")

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user, status="review")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """
        강의 수강 신청 API (다른 앱과 상호작용)
        """
        course = self.get_object()

        # 자신의 강의인 경우 수강 신청 불필요
        if request.user == course.instructor:
            return Response(
                {"detail": "본인의 강의는 수강 신청 없이 자동 접근 가능합니다."}
            )

        # enrollments 앱 로직 호출 (추후 구현)
        from enrollments.models import Enrollment

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "이미 수강 중인 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Enrollment.objects.create(
            student=request.user, course=course, status="in_progress", progress=0
        )

        return Response(
            {"detail": f"'{course.title}' 수강 신청이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )


class SectionViewSet(viewsets.ModelViewSet):
    """
    섹션 관련 API 뷰셋
    """

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_queryset(self):
        queryset = Section.objects.all()

        # URL에서 course_id 파라미터를 가져옴
        course_id = self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.order_by("order")

    def perform_create(self, serializer):
        course_id = self.request.data.get("course_id")
        course = Course.objects.get(id=course_id)

        # 강의의 작성자만 섹션 추가 가능
        if course.instructor != self.request.user:
            raise PermissionDenied(
                "You don't have permission to add sections to this course."
            )

        serializer.save(course=course)


class LessonViewSet(viewsets.ModelViewSet):
    """
    레슨 관련 API 뷰셋
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_queryset(self):
        queryset = Lesson.objects.all()

        # URL에서 section_id 파라미터를 가져옴
        section_id = self.request.query_params.get("section_id")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        return queryset.order_by("order")

    def perform_create(self, serializer):
        section_id = self.request.data.get("section_id")
        section = Section.objects.get(id=section_id)

        # 섹션이 속한 강의의 작성자만 레슨 추가 가능
        if section.course.instructor != self.request.user:
            raise PermissionDenied(
                "You don't have permission to add lessons to this section."
            )

        serializer.save(section=section)
