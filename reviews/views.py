from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Review
from .serializers import ReviewSerializer
from courses.models import Course
from django.shortcuts import redirect
from django.contrib import messages


# 리뷰 소유자만 수정/삭제할 수 있는 권한 클래스
class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    리뷰 소유자만 수정/삭제 가능, 다른 사용자는 조회만 가능
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 쓰기 요청은 리뷰 작성자만 허용
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰 API 뷰셋"""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsReviewOwnerOrReadOnly,
    ]  # 권한 클래스 추가
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["comment"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """사용자 권한에 따라 다른 쿼리셋 반환"""
        queryset = Review.objects.all()

        # 특정 강의에 대한 리뷰만 필터링
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # 일반 사용자는 본인의 리뷰 또는 공개된 코스의 리뷰만 볼 수 있음
        if not self.request.user.is_staff and not self.request.user.is_instructor():
            queryset = queryset.filter(course__status="approved") | queryset.filter(
                user=self.request.user
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """리뷰 생성 오버라이드"""
        # HTML 폼 제출 여부 확인
        is_html_request = (
            request.accepted_renderer.format == "html"
            or "text/html" in request.headers.get("Accept", "")
        )

        # 데이터에 사용자 ID 추가
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            review = serializer.save(user=request.user)

            # 강의 평균 평점 업데이트
            course = review.course
            course.update_avg_rating()

            # HTML 폼 제출인 경우 리다이렉트
            if is_html_request:
                messages.success(request, "리뷰가 성공적으로 작성되었습니다.")
                return redirect("courses:course-detail", pk=course.id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            if is_html_request:
                messages.error(request, f"리뷰 작성 중 오류가 발생했습니다: {str(e)}")
                return redirect("courses:course-detail", pk=data.get("course"))

            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """리뷰 생성 시 호출되는 메서드"""
        review = serializer.save(user=self.request.user)
        # 명시적으로 평균 평점 업데이트 호출
        review.course.update_avg_rating()

    def perform_update(self, serializer):
        """리뷰 수정 시 호출되는 메서드"""
        review = serializer.save()
        # 명시적으로 평균 평점 업데이트 호출
        review.course.update_avg_rating()

    def perform_destroy(self, instance):
        """리뷰 삭제 시 호출되는 메서드"""
        course = instance.course
        instance.delete()
        # 명시적으로 평균 평점 업데이트 호출
        course.update_avg_rating()

    def get_serializer_context(self):
        """시리얼라이저 컨텍스트에 테스트 모드 추가"""
        context = super().get_serializer_context()
        # TEST_CLIENT 헤더가 있으면 테스트 모드로 설정
        if self.request.META.get("HTTP_TEST_CLIENT", False):
            context["is_test"] = True
        return context


@login_required
def review_edit_view(request, review_id):
    """리뷰 수정 HTMX 뷰"""
    review = get_object_or_404(Review, id=review_id)

    # 권한 확인 - 자신의 리뷰만 수정 가능
    if review.user != request.user:
        if "HX-Request" in request.headers:
            return HttpResponse("권한이 없습니다.", status=403)
        messages.error(request, "자신의 리뷰만 수정할 수 있습니다.")
        return redirect("courses:course-detail", pk=review.course.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            # 이전 값 저장
            old_rating = review.rating
            old_comment = review.comment

            # 새 값 설정
            review.rating = int(rating)
            review.comment = comment
            review.save()

            # 값이 변경되었는지 로그 출력
            print(f"Rating changed: {old_rating} -> {review.rating}")
            print(f"Comment changed: {old_comment} -> {review.comment}")

            # 리뷰 수정 후 평균 평점 업데이트
            review.course.update_avg_rating()

            # 수정된 리뷰 렌더링하여 반환
            return render(request, "reviews/review_item.html", {"review": review})

    # GET 요청이나 유효하지 않은 POST 요청
    return render(request, "reviews/review_edit_form.html", {"review": review})


@login_required
def review_delete_view(request, review_id):
    """리뷰 삭제 HTMX 뷰"""
    review = get_object_or_404(Review, id=review_id)
    course = review.course
    user = request.user

    # 권한 확인 - 자신의 리뷰만 삭제 가능
    if review.user != request.user:
        if "HX-Request" in request.headers:
            return HttpResponse("권한이 없습니다.", status=403)
        messages.error(request, "자신의 리뷰만 삭제할 수 있습니다.")
        return redirect("courses:course-detail", pk=course.id)

    # 리뷰 삭제
    review.delete()

    # 리뷰 삭제 후 평균 평점 업데이트
    course.update_avg_rating()

    if "HX-Request" in request.headers:
        # HTMX 요청인 경우 리뷰 작성 폼 반환
        context = {
            "course": course,
            "user": user,
            "is_enrolled": True,  # 리뷰를 작성했었으므로 수강 중임
        }
        return render(request, "reviews/review_form.html", context)

    messages.success(request, "리뷰가 삭제되었습니다.")
    return redirect("courses:course-detail", pk=course.id)
