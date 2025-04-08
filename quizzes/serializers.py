from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """선택지 시리얼라이저"""

    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        extra_kwargs = {
            "is_correct": {
                "write_only": True
            }  # 정답 여부는 응답에서 제외 (학생들이 볼 때는 정답을 알 수 없게)
        }


class QuestionSerializer(serializers.ModelSerializer):
    """문제 시리얼라이저"""

    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "order", "choices"]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """문제 생성 시리얼라이저 (선택지 포함)"""

    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "order", "choices"]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices")
        question = Question.objects.create(**validated_data)

        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)

        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop("choices", None)
        instance = super().update(instance, validated_data)

        if choices_data:
            # 기존 선택지 삭제 (덮어쓰기)
            instance.choices.all().delete()

            # 새 선택지 생성
            for choice_data in choices_data:
                Choice.objects.create(question=instance, **choice_data)

        return instance


class QuizListSerializer(serializers.ModelSerializer):
    """퀴즈 목록 시리얼라이저"""

    instructor_name = serializers.ReadOnlyField(source="instructor.username")
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "course",
            "section",
            "lesson",
            "instructor",
            "instructor_name",
            "created_at",
            "question_count",
        ]
        read_only_fields = ["instructor", "created_at"]

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    """퀴즈 상세 시리얼라이저"""

    instructor_name = serializers.ReadOnlyField(source="instructor.username")
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "course",
            "section",
            "lesson",
            "instructor",
            "instructor_name",
            "created_at",
            "updated_at",
            "questions",
        ]
        read_only_fields = ["instructor", "created_at", "updated_at"]


class AnswerSerializer(serializers.ModelSerializer):
    """답변 시리얼라이저"""

    class Meta:
        model = Answer
        fields = ["id", "question", "selected_choice", "is_correct"]
        read_only_fields = ["is_correct"]  # is_correct는 자동 계산됨


class QuizAttemptListSerializer(serializers.ModelSerializer):
    """퀴즈 시도 목록 시리얼라이저"""

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "student",
            "started_at",
            "completed_at",
            "score",
            "total_questions",
            "correct_answers",
            "is_completed",
        ]
        read_only_fields = [
            "started_at",
            "completed_at",
            "score",
            "total_questions",
            "correct_answers",
            "is_completed",
        ]


class QuizAttemptDetailSerializer(serializers.ModelSerializer):
    """퀴즈 시도 상세 시리얼라이저"""

    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "student",
            "started_at",
            "completed_at",
            "score",
            "total_questions",
            "correct_answers",
            "is_completed",
            "answers",
        ]
        read_only_fields = [
            "started_at",
            "completed_at",
            "score",
            "total_questions",
            "correct_answers",
            "is_completed",
        ]


class SubmitQuizSerializer(serializers.Serializer):
    """퀴즈 제출 시리얼라이저"""

    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(), allow_empty=False),
        allow_empty=False,
    )

    def validate_answers(self, value):
        """답변 형식 검증"""
        for answer in value:
            if not all(k in answer for k in ["question", "selected_choice"]):
                raise serializers.ValidationError(
                    "각 답변은 question과 selected_choice를 포함해야 합니다."
                )
        return value
