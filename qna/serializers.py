from rest_framework import serializers
from .models import Question, Answer
from accounts.serializers import UserSerializer


class AnswerSerializer(serializers.ModelSerializer):
    """답변 시리얼라이저"""

    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "question",
            "user",
            "user_details",
            "content",
            "is_accepted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
            "role": obj.user.role,
        }


class QuestionSerializer(serializers.ModelSerializer):
    """질문 시리얼라이저"""

    answers = AnswerSerializer(many=True, read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    answer_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "user",
            "user_details",
            "course",
            "lesson",
            "title",
            "content",
            "is_resolved",
            "created_at",
            "updated_at",
            "answers",
            "answer_count",
        ]
        read_only_fields = ["user", "created_at", "updated_at", "is_resolved"]

    def get_user_details(self, obj):
        return {
            "username": obj.user.username,
            "email": obj.user.email,
            "role": obj.user.role,
        }

    def get_answer_count(self, obj):
        return obj.answers.count()
