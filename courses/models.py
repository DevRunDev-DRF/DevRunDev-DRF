import os
import re

from django.conf import settings
from django.db import models
from django.db.models import Avg

from accounts.models import User


class Course(models.Model):
    STATUS_CHOICES = [
        ("review", "심사 중"),
        ("approved", "승인 완료"),
        ("not_approved", "수정 필요"),
    ]

    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="review")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avg_rating = models.FloatField(default=0.0)
    thumbnail = models.ImageField(
        upload_to="courses/", null=True, blank=True, default="default.jpg"
    )

    def update_avg_rating(self):
        """리뷰 점수의 평균을 계산하여 업데이트하는 메서드"""
        from django.db.models import Avg

        # 디버깅을 위한 로그 추가
        print(f"Updating avg_rating for course {self.id}: {self.title}")

        # 모든 리뷰 확인
        reviews = self.reviews.all()
        print(f"Reviews count: {reviews.count()}")
        for review in reviews:
            print(
                f"Review ID: {review.id}, Rating: {review.rating}, User: {review.user.username}"
            )

        # 평균 계산 (반올림 없이)
        avg = self.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        print(f"Calculated average: {avg}")

        # 결과가 None이 아닌 경우에만 업데이트
        if avg is not None:
            self.avg_rating = avg
        else:
            self.avg_rating = 0.0

        # 디버깅을 위한 로그 추가
        print(f"Final avg_rating: {self.avg_rating}")

        # save 메서드가 다시 update_avg_rating을 호출하지 않도록 주의
        super(Course, self).save(update_fields=["avg_rating"])

    def get_thumbnail_url(self):
        """썸네일 파일이 존재하지 않으면 기본 썸네일 반환"""
        if self.thumbnail:
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, str(self.thumbnail))
            if os.path.exists(thumbnail_path):
                return self.thumbnail.url
        return settings.MEDIA_URL + "default.jpg"

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Section.objects.filter(course=self.course).count()
            self.order = last_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


def convert_youtube_url(url):
    """YouTube URL을 embed 형식으로 변환"""
    if not url:
        return url

    # 이미 embed 형식인 경우
    if "youtube.com/embed/" in url:
        return url

    # 유튜브 URL에서 동영상 ID 추출하는 정규식 (shorts 포함)
    youtube_regex = r'(?:youtube\.com\/(?:shorts\/|[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(youtube_regex, url)

    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"

    # 일치하는 패턴이 없으면 원래 URL 반환
    return url


class Lesson(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Lesson.objects.filter(section=self.section).count()
            self.order = last_order + 1

        if self.video_url:
            self.video_url = convert_youtube_url(self.video_url)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
