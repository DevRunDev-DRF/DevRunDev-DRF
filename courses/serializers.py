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


class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["title", "video_url", "order"]


class SectionCreateSerializer(serializers.ModelSerializer):
    lessons = LessonCreateSerializer(many=True, required=False)

    class Meta:
        model = Section
        fields = ["title", "order", "lessons"]


class CourseCreateSerializer(serializers.ModelSerializer):
    sections = SectionCreateSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = ["title", "description", "price", "status", "thumbnail", "sections"]
        read_only_fields = ["status"]  # 상태는 자동으로 'review'로 설정

    def create(self, validated_data):
        sections_data = validated_data.pop("sections", [])

        # 강의 생성
        course = Course.objects.create(**validated_data)

        # 섹션 생성
        for section_data in sections_data:
            lessons_data = section_data.pop("lessons", [])
            section = Section.objects.create(course=course, **section_data)

            # 레슨 생성
            for lesson_data in lessons_data:
                Lesson.objects.create(section=section, **lesson_data)

        return course

    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections", [])

        # 기본 필드 업데이트
        instance = super().update(instance, validated_data)

        # 섹션 업데이트 (기존 섹션 유지 옵션)
        for section_data in sections_data:
            lessons_data = section_data.pop("lessons", [])

            # 섹션 ID가 제공되면 업데이트, 아니면 새로 생성
            section_id = section_data.pop("id", None)
            if section_id:
                section = Section.objects.get(id=section_id, course=instance)
                for key, value in section_data.items():
                    setattr(section, key, value)
                section.save()
            else:
                section = Section.objects.create(course=instance, **section_data)

            # 레슨 업데이트
            for lesson_data in lessons_data:
                lesson_id = lesson_data.pop("id", None)
                if lesson_id:
                    lesson = Lesson.objects.get(id=lesson_id, section=section)
                    for key, value in lesson_data.items():
                        setattr(lesson, key, value)
                    lesson.save()
                else:
                    Lesson.objects.create(section=section, **lesson_data)

        return instance


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
