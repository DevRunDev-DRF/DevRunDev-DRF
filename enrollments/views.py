# enrollments/views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Enrollment, LessonProgress, Certificate, CartItem
from .serializers import (
    EnrollmentSerializer,
    EnrollmentDetailSerializer,
    LessonProgressSerializer,
    CertificateSerializer,
    CartItemSerializer,
)
from .permissions import IsEnrollmentOwner, IsCartItemOwner
from accounts.permissions import IsInstructor
from courses.models import Course, Lesson


class EnrollmentViewSet(viewsets.ModelViewSet):
    """수강 신청 관련 API 뷰셋"""

    queryset = Enrollment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "student", "status"]
    ordering_fields = ["enrolled_at", "progress"]
    ordering = ["-enrolled_at"]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return EnrollmentDetailSerializer
        return EnrollmentSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [IsAuthenticated(), IsEnrollmentOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.all()

        if user.is_instructor():
            return queryset.filter(course__instructor=user)

        if not user.is_staff:
            if self.action in ["list", "create"]:
                return queryset.filter(student=user)
            return queryset

        return queryset

    def create(self, request, *args, **kwargs):
        if request.data.get("student") is None:
            request.data.update({"student": request.user.id})
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"])
    def reset_progress(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.student != request.user:
            return Response(
                {"detail": "자신의 수강 신청만 초기화할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        enrollment.reset_progress()
        return Response({"detail": "수강 진행률이 초기화되었습니다."})

    @action(detail=True, methods=["post"])
    def generate_certificate(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.student != request.user:
            return Response(
                {
                    "detail": "자신의 수강 신청에 대해서만 수료증을 발급받을 수 있습니다."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not enrollment.is_course_completed():
            return Response(
                {
                    "detail": "모든 강의와 퀴즈를 완료해야 수료증을 발급받을 수 있습니다."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        certificate = enrollment.generate_certificate()
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """강의 진행 상황 관련 API 뷰셋"""

    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "lesson", "completed"]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsEnrollmentOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = LessonProgress.objects.all()

        if user.is_instructor():
            return queryset.filter(lesson__section__course__instructor=user)

        if not user.is_staff:
            return queryset.filter(student=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_completed(self, request):
        lesson_id = request.data.get("lesson")
        if not lesson_id:
            return Response(
                {"detail": "lesson 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)

        enrollment_exists = Enrollment.objects.filter(
            student=request.user,
            course=lesson.section.course,
            status__in=["in_progress", "completed"],
        ).exists()

        if not enrollment_exists:
            return Response(
                {"detail": "이 강의에 등록되어 있지 않습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson
        )

        progress.mark_completed()

        enrollment = Enrollment.objects.get(
            student=request.user, course=lesson.section.course
        )
        enrollment.last_watched_lesson = lesson
        enrollment.save()

        return Response({"detail": "레슨이 완료 처리되었습니다."})

    @action(detail=False, methods=["post"])
    def update_last_watched(self, request):
        lesson_id = request.data.get("lesson")
        if not lesson_id:
            return Response(
                {"detail": "lesson 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson
        )

        progress.update_last_watched()

        enrollment = Enrollment.objects.get(
            student=request.user, course=lesson.section.course
        )
        enrollment.last_watched_lesson = lesson
        enrollment.save()

        return Response({"detail": "마지막 시청 시간이 업데이트되었습니다."})


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """수료증 관련 API 뷰셋 (읽기 전용)"""

    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Certificate.objects.all()

        if user.is_instructor():
            return queryset.filter(enrollment__course__instructor=user)

        if not user.is_staff:
            return queryset.filter(enrollment__student=user)

        return queryset


class CartItemViewSet(viewsets.ModelViewSet):
    """장바구니 아이템 관련 API 뷰셋"""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCartItemOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "이미 수강 중인 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CartItem.objects.filter(user=request.user, course=course).exists():
            return Response(
                {"detail": "이미 장바구니에 추가된 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data.update({"user": request.user.id})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 장바구니 개수 반환
        cart_count = CartItem.objects.filter(user=request.user).count()
        return Response(str(cart_count), status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        # HTMX 요청인 경우 장바구니 아이템 카운트 갱신
        if request.headers.get("HX-Request"):
            cart_count = CartItem.objects.filter(user=request.user).count()
            headers = {
                "HX-Trigger-After-Swap": '{"updateCartCount": "'
                + str(cart_count)
                + '"}'
            }
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"detail": "장바구니가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollments = []
        for item in cart_items:
            if not Enrollment.objects.filter(
                student=request.user, course=item.course
            ).exists():
                enrollment = Enrollment.objects.create(
                    student=request.user,
                    course=item.course,
                    status="in_progress",
                    progress=0,
                )
                enrollments.append(enrollment)

        cart_items.delete()

        # HTMX 요청일 경우 템플릿 응답
        if "HX-Request" in request.headers:
            return render(
                request,
                "enrollments/checkout_success.html",
                {"enrollments": enrollments},
            )

        return Response(
            {
                "detail": f"{len(enrollments)}개 강의의 수강신청이 완료되었습니다.",
                "enrollments": EnrollmentSerializer(enrollments, many=True).data,
            }
        )


@login_required
def cart_view(request):
    """장바구니 페이지 뷰"""
    cart_items = CartItem.objects.filter(user=request.user).select_related(
        "course", "course__instructor"
    )

    # 장바구니 총액 계산
    total_price = sum(item.course.price for item in cart_items)

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_count": cart_items.count(),
    }
    return render(request, "enrollments/cart.html", context)


@login_required
def my_courses_view(request):
    """내 강의 페이지 뷰"""
    from enrollments.models import Enrollment

    enrollments = Enrollment.objects.filter(
        student=request.user, status__in=["in_progress", "completed"]
    ).select_related("course")

    context = {
        "enrollments": enrollments,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "enrollments/my_courses.html", context)
