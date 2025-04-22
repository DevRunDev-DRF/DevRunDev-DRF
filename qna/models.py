from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class Question(models.Model):
    """학생이 작성한 질문 모델"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="작성자",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="questions", verbose_name="강의"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
        verbose_name="레슨",
    )
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    is_resolved = models.BooleanField(default=False, verbose_name="해결됨")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "질문"
        verbose_name_plural = "질문 목록"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Answer(models.Model):
    """질문에 대한 답변 모델"""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="질문"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="작성자",
    )
    content = models.TextField(verbose_name="내용")
    is_accepted = models.BooleanField(default=False, verbose_name="채택됨")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "답변"
        verbose_name_plural = "답변 목록"
        ordering = ["-is_accepted", "-created_at"]

    def __str__(self):
        return f"{self.user.username}의 답변"

    def save(self, *args, **kwargs):
        # 답변이 채택되면 질문을 해결됨으로 표시
        if self.is_accepted:
            self.question.is_resolved = True
            self.question.save()

            # 동일한 질문에 대한 다른 답변들의 채택 상태를 False로 설정
            Answer.objects.filter(question=self.question).exclude(pk=self.pk).update(
                is_accepted=False
            )

        super().save(*args, **kwargs)
