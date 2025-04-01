from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 주소는 필수입니다")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault(
            "role", self.model.Role.MANAGER
        )  # Role을 명시적으로 MANAGER로 설정
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "Student", "학생"
        INSTRUCTOR = "Instructor", "강사"
        MANAGER = "manager", "관리자"

    is_verified = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(("email address"), unique=True)
    username = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR


class InstructorApplication(models.Model):
    """강사 신청 모델"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "대기 중"
        APPROVED = "APPROVED", "승인됨"
        REJECTED = "REJECTED", "거부됨"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="instructor_applications"
    )
    qualifications = models.TextField()
    experience = models.TextField()
    sample_video_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def approve(self):
        self.status = self.Status.APPROVED
        self.save()

        self.user.role = User.Role.INSTRUCTOR
        self.user.save()

    def save(self, *args, **kwargs):
        # 상태가 변경되었고, 새로운 상태가 APPROVED인지 확인
        if self.pk:  # 기존 객체 수정 시에만 체크
            try:
                original = InstructorApplication.objects.get(pk=self.pk)
                if (
                    original.status != self.Status.APPROVED
                    and self.status == self.Status.APPROVED
                ):
                    # 사용자 역할 변경
                    self.user.role = User.Role.INSTRUCTOR
                    self.user.save()
            except InstructorApplication.DoesNotExist:
                pass  # 새 객체 생성 시 패스

        # 원래의 save 메서드 호출
        super().save(*args, **kwargs)
