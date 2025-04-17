from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from courses.models import Course


class Review(models.Model):
    """강의 리뷰 모델"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="작성자",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="reviews", verbose_name="강의"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="평점"
    )
    comment = models.TextField(verbose_name="리뷰 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰 목록"
        ordering = ["-created_at"]
        # 한 사용자가 하나의 강의에 대해 한 개의 리뷰만 작성 가능
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username}의 '{self.course.title}' 리뷰 ({self.rating}점)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 리뷰 저장 시 강의의 평균 평점 업데이트
        # 여기서는 호출만 하고 실제 구현은 Course 모델에서 처리
        # 이렇게 하면 circular import 문제 방지
        self.course.update_avg_rating()
