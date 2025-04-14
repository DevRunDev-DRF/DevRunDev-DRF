import decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course, Lesson
from quizzes.models import Quiz, QuizAttempt


class Enrollment(models.Model):
    """✅ 수강 신청 모델 (학생이 강의를 신청하고 진행 상태를 관리)"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )  # ✅ 소수점 2자리까지 저장

    STATUS_CHOICES = [
        ("in_progress", "수강 중"),
        ("completed", "완료"),
        ("dropped", "수강 취소"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="in_progress"
    )

    last_watched_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_watched",
    )

    class Meta:
        unique_together = ("student", "course")

    def update_progress(self):
        """✅ 전체 강의 진행률 업데이트 (완료된 레슨 기준, 최적화 적용)"""
        completed_lessons = LessonProgress.objects.filter(
            student=self.student, lesson__section__course=self.course, completed=True
        ).count()  # ✅ 올바르게 LessonProgress에서 가져오기

        total_lessons = Lesson.objects.filter(section__course=self.course).count()

        if total_lessons > 0:
            new_progress = (completed_lessons / total_lessons) * 100
            self.progress = decimal.Decimal(new_progress).quantize(
                decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP
            )
        else:
            self.progress = decimal.Decimal("0.00")

        if self.progress == 100:
            self.status = "completed"
        self.save()

    def reset_progress(self):
        """✅ 강의 재수강 (모든 진행률 초기화, 최적화 적용)"""
        self.progress = decimal.Decimal("0.00")
        self.status = "in_progress"
        self.last_watched_lesson = None

        # ✅ 완료된 레슨만 업데이트하여 불필요한 DB 연산 방지
        LessonProgress.objects.filter(
            student=self.student, lesson__section__course=self.course, completed=True
        ).update(completed=False, completed_at=None)

        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"

    def is_course_completed(self):
        """강의 수료 조건 충족 여부 확인"""
        # 모든 레슨이 완료되었는지 확인
        course_lessons = Lesson.objects.filter(section__course=self.course)
        total_lessons = course_lessons.count()

        if total_lessons == 0:
            return False

        completed_lessons = LessonProgress.objects.filter(
            student=self.student, lesson__section__course=self.course, completed=True
        ).count()

        # 모든 퀴즈가 완료되었는지 확인
        course_quizzes = Quiz.objects.filter(course=self.course)
        total_quizzes = course_quizzes.count()

        # 퀴즈가 없는 경우 레슨 완료만으로 수료 가능
        if total_quizzes == 0:
            return completed_lessons == total_lessons

        completed_quizzes = (
            QuizAttempt.objects.filter(
                quiz__course=self.course, student=self.student, is_completed=True
            )
            .values("quiz")
            .distinct()
            .count()
        )

        # 모든 레슨과 퀴즈가 완료되었는지 확인
        return (completed_lessons == total_lessons) and (
            completed_quizzes == total_quizzes
        )

    def generate_certificate(self):
        """수료증 생성"""
        # 이미 수료증이 있는지 확인
        from enrollments.models import Certificate

        try:
            return self.certificate
        except Certificate.DoesNotExist:
            # 수료 조건 확인
            if not self.is_course_completed():
                return None

            # 수료증 생성
            from .models import Certificate

            certificate = Certificate.objects.create(enrollment=self)

            # 상태 업데이트
            self.status = "completed"
            self.save()

            return certificate


class LessonProgress(models.Model):
    """✅ 레슨 학습 진행 모델 (학생이 특정 레슨을 완료했는지 기록)"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="progress"
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_watched_at = models.DateTimeField(
        null=True, blank=True
    )  # ✅ auto_now=True 제거

    class Meta:
        unique_together = ("student", "lesson")

    def mark_completed(self):
        """✅ 레슨 완료 처리"""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()

            # ✅ 강의 진행률 업데이트
            enrollment = Enrollment.objects.filter(
                student=self.student, course=self.lesson.section.course
            ).first()
            if enrollment:
                enrollment.update_progress()

    def update_last_watched(self):
        """✅ 마지막 시청한 시간 갱신 (불필요한 업데이트 방지)"""
        self.last_watched_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({'완료' if self.completed else '진행 중'})"


class Certificate(models.Model):
    """수료증 모델"""

    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="certificate"
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return (
            f"{self.enrollment.student.email} - {self.enrollment.course.title} 수료증"
        )

    def save(self, *args, **kwargs):
        # 처음 생성될 때 고유한 수료증 ID 생성
        if not self.certificate_id:
            import uuid

            # 'CERT-' 접두사와 UUID를 사용하여 고유한 ID 생성
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class CartItem(models.Model):
    """✅ 장바구니에 담긴 강의 정보 저장"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="cart_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)  # ✅ 장바구니에 담은 시간

    class Meta:
        unique_together = ("user", "course")  # ✅ 중복 추가 방지

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Payment(models.Model):
    """결제 정보 모델"""

    STATUS_CHOICES = [
        ("ready", "결제 대기"),
        ("paid", "결제 완료"),
        ("cancelled", "결제 취소"),
        ("failed", "결제 실패"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    merchant_uid = models.CharField(
        max_length=100, unique=True, verbose_name="주문번호"
    )
    amount = models.PositiveIntegerField(default=0, verbose_name="결제 금액")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ready", verbose_name="결제 상태"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    imp_uid = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="아임포트 거래 고유번호"
    )

    # 결제와 장바구니 아이템 연결
    cart_items = models.ManyToManyField(
        "CartItem", related_name="payments", verbose_name="장바구니 항목"
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount}원 ({self.get_status_display()})"
