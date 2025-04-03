# quizzes/models.py
from django.db import models

from accounts.models import User
from courses.models import Course, Lesson, Section


class Quiz(models.Model):
    """퀴즈 모델"""

    title = models.CharField(max_length=200, verbose_name="퀴즈 제목")
    description = models.TextField(blank=True, verbose_name="퀴즈 설명")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="quizzes", verbose_name="강의"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="quizzes",
        null=True,
        blank=True,
        verbose_name="섹션",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quizzes",
        null=True,
        blank=True,
        verbose_name="강의 영상",
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_quizzes",
        verbose_name="출제자",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    class Meta:
        verbose_name = "퀴즈"
        verbose_name_plural = "퀴즈 목록"
        ordering = ["-created_at"]


class Question(models.Model):
    """문제 모델"""

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="퀴즈"
    )
    text = models.TextField(verbose_name="문제 내용")
    order = models.PositiveIntegerField(default=0, verbose_name="문제 순서")

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Question.objects.filter(quiz=self.quiz).count()
            self.order = last_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"문제 {self.order}: {self.text[:50]}..."

    class Meta:
        ordering = ["order"]
        verbose_name = "문제"
        verbose_name_plural = "문제 목록"


class Choice(models.Model):
    """선택지 모델"""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices", verbose_name="문제"
    )
    text = models.CharField(max_length=200, verbose_name="선택지 내용")
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")

    def __str__(self):
        return f"{self.text} - {'정답' if self.is_correct else '오답'}"

    class Meta:
        verbose_name = "선택지"
        verbose_name_plural = "선택지 목록"


class QuizAttempt(models.Model):
    """퀴즈 시도 모델"""

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name="퀴즈"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        verbose_name="학생",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="시작 시간")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="완료 시간")
    score = models.PositiveIntegerField(default=0, verbose_name="점수")
    total_questions = models.PositiveIntegerField(
        default=0, verbose_name="전체 문제 수"
    )
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="정답 수")
    is_completed = models.BooleanField(default=False, verbose_name="완료 여부")

    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} ({self.score}점)"

    def calculate_score(self):
        """점수 계산"""
        if self.total_questions > 0:
            self.score = int((self.correct_answers / self.total_questions) * 100)
        else:
            self.score = 0
        self.save()

    class Meta:
        verbose_name = "퀴즈 시도"
        verbose_name_plural = "퀴즈 시도 목록"
        ordering = ["-started_at"]


class Answer(models.Model):
    """학생 답변 모델"""

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="퀴즈 시도",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="문제"
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name="selections",
        verbose_name="선택한 답",
    )
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")

    def __str__(self):
        return f"{self.attempt.student.email}의 {self.question}에 대한 답변"

    def save(self, *args, **kwargs):
        """저장 시 정답 여부 자동 확인"""
        self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)

        # 답변이 저장될 때마다 퀴즈 시도의 정답 수 업데이트
        attempt = self.attempt
        attempt.correct_answers = attempt.answers.filter(is_correct=True).count()
        attempt.total_questions = attempt.quiz.questions.count()
        attempt.calculate_score()

    class Meta:
        unique_together = (
            "attempt",
            "question",
        )  # 하나의 시도에서 하나의 문제에 대한 하나의 답변만 허용
        verbose_name = "답변"
        verbose_name_plural = "답변 목록"
