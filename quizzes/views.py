from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from courses.models import Course
from .models import Quiz, Question, Choice, QuizAttempt, Answer
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuestionSerializer,
    QuestionCreateSerializer,
    ChoiceSerializer,
    QuizAttemptListSerializer,
    QuizAttemptDetailSerializer,
    AnswerSerializer,
    SubmitQuizSerializer,
)
from .permissions import (
    IsInstructorOrReadOnly,
    IsQuizInstructor,
    IsEnrolledOrInstructor,
    IsQuizAttemptOwner,
)
from accounts.permissions import IsInstructor


class QuizViewSet(viewsets.ModelViewSet):
    """
    퀴즈 관련 API 뷰셋
    """

    queryset = Quiz.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "section", "lesson", "instructor"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return QuizListSerializer
        return QuizDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [
                IsAuthenticated,
                IsInstructorOrReadOnly,
                IsQuizInstructor,
            ]
        elif self.action in ["start_attempt", "submit_attempt"]:
            permission_classes = [IsAuthenticated, IsEnrolledOrInstructor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """퀴즈 생성 시 현재 로그인한 사용자를 instructor로 설정"""
        serializer.save(instructor=self.request.user)

    @swagger_auto_schema(
        operation_summary="퀴즈 시작하기",
        operation_description="학생이 퀴즈를 시작하는 API",
        responses={
            201: QuizAttemptDetailSerializer,
            400: "이미 진행 중인 시도가 있거나 완료된 시도가 있는 경우",
            403: "해당 강의에 등록되지 않은 경우",
        },
    )
    @action(detail=True, methods=["post"])
    def start_attempt(self, request, pk=None):
        """학생이 퀴즈 시도를 시작하는 API"""
        quiz = self.get_object()

        # 이미 완료된 시도가 있는지 확인
        completed_attempt = QuizAttempt.objects.filter(
            quiz=quiz, student=request.user, is_completed=True
        ).first()

        if completed_attempt:
            return Response(
                {"detail": "이미 완료된 퀴즈 시도가 존재합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 진행 중인 시도가 있는지 확인
        in_progress_attempt = QuizAttempt.objects.filter(
            quiz=quiz, student=request.user, is_completed=False
        ).first()

        if in_progress_attempt:
            serializer = QuizAttemptDetailSerializer(in_progress_attempt)
            return Response(serializer.data)

        # 새 시도 생성
        attempt = QuizAttempt.objects.create(
            quiz=quiz, student=request.user, total_questions=quiz.questions.count()
        )

        serializer = QuizAttemptDetailSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="퀴즈 제출하기",
        operation_description="학생이 퀴즈 답변을 제출하는 API",
        request_body=SubmitQuizSerializer,
        responses={
            200: QuizAttemptDetailSerializer,
            400: "유효하지 않은 요청 또는 이미 완료된 시도",
            403: "해당 강의에 등록되지 않은 경우",
            404: "퀴즈 또는 시도를 찾을 수 없음",
        },
    )
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def submit_attempt(self, request, pk=None):
        """학생이 퀴즈 답변을 제출하는 API"""
        quiz = self.get_object()

        # 진행 중인 시도 가져오기
        attempt = QuizAttempt.objects.filter(
            quiz=quiz, student=request.user, is_completed=False
        ).first()

        if not attempt:
            return Response(
                {"detail": "진행 중인 퀴즈 시도를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 데이터 유효성 검사
        serializer = SubmitQuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answers_data = serializer.validated_data["answers"]

        # 답변 저장
        for answer_data in answers_data:
            question_id = answer_data["question"]
            choice_id = answer_data["selected_choice"]

            # 해당 문제와 선택지가 존재하는지 확인
            question = get_object_or_404(Question, id=question_id, quiz=quiz)
            choice = get_object_or_404(Choice, id=choice_id, question=question)

            # 이미 답변이 있으면 업데이트, 없으면 생성
            answer, created = Answer.objects.update_or_create(
                attempt=attempt, question=question, defaults={"selected_choice": choice}
            )

        # 퀴즈 시도 완료 처리
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # 점수 계산 메서드 호출
        attempt.calculate_score()

        serializer = QuizAttemptDetailSerializer(attempt)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    문제 관련 API 뷰셋
    """

    queryset = Question.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["quiz"]
    ordering_fields = ["order"]
    ordering = ["order"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return QuestionCreateSerializer
        return QuestionSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes.append(IsQuizInstructor)
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """문제 생성 시 퀴즈 설정"""
        quiz_id = self.request.data.get("quiz")
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # 퀴즈 작성자만 문제 추가 가능
        if quiz.instructor != self.request.user:
            self.permission_denied(
                self.request, message="이 퀴즈에 문제를 추가할 권한이 없습니다."
            )

        serializer.save(quiz=quiz)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    퀴즈 시도 관련 API 뷰셋 (읽기 전용)
    """

    queryset = QuizAttempt.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["quiz", "student", "is_completed"]
    ordering_fields = ["started_at", "completed_at", "score"]
    ordering = ["-started_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return QuizAttemptListSerializer
        return QuizAttemptDetailSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ["retrieve", "list"]:
            permission_classes.append(IsQuizAttemptOwner)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """사용자 역할에 따라 퀴즈 시도 필터링"""
        user = self.request.user
        queryset = QuizAttempt.objects.all()

        # 강사는 자신이 만든 퀴즈의 시도 확인 가능
        if user.is_instructor():
            return queryset.filter(quiz__instructor=user)

        # 학생은 자신의 시도만 확인 가능
        return queryset.filter(student=user)
