from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Review
from .serializers import ReviewSerializer
from courses.models import Course


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰 API 뷰셋"""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
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
    review = get_object_or_404(Review, id=review_id, user=request.user)

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
    review = get_object_or_404(Review, id=review_id, user=request.user)
    course = review.course

    if request.method == "DELETE":
        review.delete()
        # 리뷰 삭제 후 평균 평점 업데이트
        course.update_avg_rating()
        return HttpResponse(status=200)

    return redirect("courses:course-detail", pk=course.id)
