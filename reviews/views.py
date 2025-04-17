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
    permission_classes = [IsAuthenticated, IsReviewOwnerOrReadOnly]  # 권한 클래스 추가
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # 리뷰 생성 후 평균 평점 업데이트
        course = serializer.validated_data["course"]
        course.update_avg_rating()

    def perform_update(self, serializer):
        serializer.save()
        # 리뷰 수정 후 평균 평점 업데이트
        course = serializer.instance.course
        course.update_avg_rating()

    def perform_destroy(self, instance):
        course = instance.course
        instance.delete()
        # 리뷰 삭제 후 평균 평점 업데이트
        course.update_avg_rating()


@login_required
def review_edit_view(request, review_id):
    """리뷰 수정 HTMX 뷰"""
    review = get_object_or_404(Review, id=review_id)

    # 권한 확인 - 자신의 리뷰만 수정 가능
    if review.user != request.user:
        if request.headers.get("HX-Request"):
            # HTMX 요청인 경우 403 상태 코드와 에러 메시지 반환
            return HttpResponse("권한이 없습니다.", status=403)
        # 일반 요청인 경우 리디렉션
        messages.error(request, "자신의 리뷰만 수정할 수 있습니다.")
        return redirect("courses:course-detail", pk=review.course.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            review.rating = rating
            review.comment = comment
            review.save()

            # 리뷰 수정 후 평균 평점 업데이트
            review.course.update_avg_rating()

            return render(request, "reviews/review_item.html", {"review": review})

    # GET 요청 또는 유효하지 않은 POST 요청
    return render(request, "reviews/review_edit_form.html", {"review": review})


@login_required
def review_delete_view(request, review_id):
    """리뷰 삭제 HTMX 뷰"""
    review = get_object_or_404(Review, id=review_id)
    course = review.course

    # 권한 확인 - 자신의 리뷰만 삭제 가능
    if review.user != request.user:
        if request.headers.get("HX-Request"):
            # HTMX 요청인 경우 403 상태 코드와 에러 메시지 반환
            return HttpResponse("권한이 없습니다.", status=403)
        # 일반 요청인 경우 리디렉션
        messages.error(request, "자신의 리뷰만 삭제할 수 있습니다.")
        return redirect("courses:course-detail", pk=course.id)

    if request.method == "DELETE":
        review.delete()
        # 리뷰 삭제 후 평균 평점 업데이트
        course.update_avg_rating()
        return HttpResponse(status=200)

    return redirect("courses:course-detail", pk=course.id)
