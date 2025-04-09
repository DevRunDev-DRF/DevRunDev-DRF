# enrollments/serializers.py
from rest_framework import serializers
from .models import Enrollment, LessonProgress, Certificate, CartItem
from accounts.serializers import UserSerializer
from courses.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "enrolled_at",
            "last_updated_at",
            "progress",
            "status",
            "last_watched_lesson",
        ]
        read_only_fields = ["enrolled_at", "last_updated_at", "progress"]


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "enrolled_at",
            "last_updated_at",
            "progress",
            "status",
            "last_watched_lesson",
        ]
        read_only_fields = ["enrolled_at", "last_updated_at", "progress"]


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "student",
            "lesson",
            "completed",
            "completed_at",
            "last_watched_at",
        ]
        read_only_fields = ["completed_at"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "enrollment", "issued_at", "certificate_id"]
        read_only_fields = ["issued_at", "certificate_id"]


class CartItemSerializer(serializers.ModelSerializer):
    course_details = CourseListSerializer(source="course", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "user", "course", "course_details", "added_at"]
        read_only_fields = ["added_at"]
