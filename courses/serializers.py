from rest_framework import serializers
from .models import Course, Section, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "order"]


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "title", "order", "lessons"]


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.ReadOnlyField(source="instructor.username")

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "price",
            "status",
            "instructor",
            "instructor_name",
            "created_at",
            "updated_at",
            "avg_rating",
            "thumbnail",
        ]
        read_only_fields = ["instructor", "avg_rating"]


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor_name = serializers.ReadOnlyField(source="instructor.username")
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "price",
            "status",
            "instructor",
            "instructor_name",
            "created_at",
            "updated_at",
            "avg_rating",
            "thumbnail",
            "sections",
        ]
        read_only_fields = ["instructor", "avg_rating"]
