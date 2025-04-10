from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

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


# REST API ViewSets - 기존 코드를 유지합니다
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


# 템플릿 기반 뷰 (웹 페이지용)
class QuizListView(LoginRequiredMixin, ListView):
    """퀴즈 목록 페이지"""

    model = Quiz
    template_name = "quizzes/quiz_list.html"
    context_object_name = "quizzes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Quiz.objects.all()

        # 강의 필터
        course_id = self.request.GET.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # 강사 필터
        if self.request.user.is_instructor():
            instructor_id = self.request.GET.get("instructor")
            if instructor_id and instructor_id == str(self.request.user.id):
                queryset = queryset.filter(instructor=self.request.user)
        else:
            # 학생인 경우, 자신이 수강 중인 강의의 퀴즈만 표시
            enrolled_courses = Course.objects.filter(
                enrollments__student=self.request.user
            )
            queryset = queryset.filter(course__in=enrolled_courses)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 수강 중인 강의 목록
        context["courses"] = Course.objects.filter(
            enrollments__student=self.request.user
        ).distinct()

        # 사용자가 완료한 퀴즈 ID 목록
        user_completed_quizzes = QuizAttempt.objects.filter(
            student=self.request.user, is_completed=True
        ).values_list("quiz_id", flat=True)

        context["user_completed_quizzes"] = user_completed_quizzes

        return context


class QuizDetailView(LoginRequiredMixin, DetailView):
    """퀴즈 상세 페이지"""

    model = Quiz
    template_name = "quizzes/quiz_detail.html"
    context_object_name = "quiz"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 현재 사용자가 이 퀴즈의 시도 정보
        if not self.request.user.is_instructor():
            context["user_attempt"] = (
                QuizAttempt.objects.filter(quiz=self.object, student=self.request.user)
                .order_by("-started_at")
                .first()
            )

        return context


class QuizCreateView(LoginRequiredMixin, CreateView):
    """퀴즈 생성 페이지"""

    model = Quiz
    template_name = "quizzes/quiz_form.html"
    fields = ["title", "description", "course", "section", "lesson"]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor():
            messages.error(request, "강사만 퀴즈를 생성할 수 있습니다.")
            return redirect("courses:course-list")
        return super().dispatch(request, *args, **kwargs)


class QuizAttemptView(LoginRequiredMixin, View):
    """퀴즈 시도 페이지"""

    template_name = "quizzes/quiz_attempt.html"

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        try:
            quiz = Quiz.objects.get(id=quiz_id)

            # 수강 중인지 확인 (강사는 예외)
            if not request.user.is_instructor():
                is_enrolled = quiz.course.enrollments.filter(
                    student=request.user
                ).exists()
                if not is_enrolled:
                    messages.error(
                        request, "이 강의를 수강 중인 학생만 퀴즈를 시도할 수 있습니다."
                    )
                    return redirect("quizzes:quiz-detail", pk=quiz_id)

            # 퀴즈 시도 가져오기 또는 생성
            attempt, created = QuizAttempt.objects.get_or_create(
                quiz=quiz,
                student=request.user,
                is_completed=False,
                defaults={"total_questions": quiz.questions.count()},
            )

            # 이미 완료된 시도가 있는지 확인
            completed_attempt = QuizAttempt.objects.filter(
                quiz=quiz, student=request.user, is_completed=True
            ).first()

            if completed_attempt and not request.user.is_instructor():
                messages.info(
                    request, "이미 이 퀴즈를 완료했습니다. 결과를 확인합니다."
                )
                return redirect("quizzes:quiz-result", pk=quiz_id)

            # 문제 목록 가져오기
            questions = quiz.questions.all().order_by("order")

            # 이미 답변한 문제 가져오기
            user_answers = {}
            for answer in Answer.objects.filter(attempt=attempt):
                user_answers[answer.question.id] = answer.selected_choice.id

            return render(
                request,
                self.template_name,
                {
                    "quiz": quiz,
                    "questions": questions,
                    "user_answers": user_answers,
                    "attempt": attempt,
                },
            )

        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")

    def post(self, request, *args, **kwargs):
        # 제출 페이지로 리다이렉트 (제출은 QuizSubmitView에서 처리)
        return redirect("quizzes:quiz-submit", pk=kwargs.get("pk"))


class QuizSubmitView(LoginRequiredMixin, View):
    """퀴즈 제출 처리"""

    template_name = "quizzes/quiz_submit.html"

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        try:
            quiz = Quiz.objects.get(id=quiz_id)

            # 수강 중인지 확인 (강사는 예외)
            if not request.user.is_instructor():
                is_enrolled = quiz.course.enrollments.filter(
                    student=request.user
                ).exists()
                if not is_enrolled:
                    messages.error(
                        request, "이 강의를 수강 중인 학생만 퀴즈를 제출할 수 있습니다."
                    )
                    return redirect("quizzes:quiz-detail", pk=quiz_id)

            # 진행 중인 시도가 있는지 확인
            attempt = QuizAttempt.objects.filter(
                quiz=quiz, student=request.user, is_completed=False
            ).first()

            if not attempt:
                messages.error(request, "진행 중인 퀴즈 시도가 없습니다.")
                return redirect("quizzes:quiz-attempt", pk=quiz_id)

            # 문제 목록 가져오기
            questions = quiz.questions.all().order_by("order")

            # 답변 목록 가져오기
            answers = {}
            answered_count = 0
            unanswered_questions = []

            for question in questions:
                answer = Answer.objects.filter(
                    attempt=attempt, question=question
                ).first()
                if answer:
                    answers[question.id] = answer.selected_choice.id
                    answered_count += 1
                else:
                    unanswered_questions.append(question)

            return render(
                request,
                self.template_name,
                {
                    "quiz": quiz,
                    "questions_count": questions.count(),
                    "answered_count": answered_count,
                    "unanswered_questions": unanswered_questions,
                    "answers": answers,
                },
            )

        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")

    def post(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        try:
            quiz = Quiz.objects.get(id=quiz_id)

            # 수강 중인지 확인 (강사는 예외)
            if not request.user.is_instructor():
                is_enrolled = quiz.course.enrollments.filter(
                    student=request.user
                ).exists()
                if not is_enrolled:
                    messages.error(
                        request, "이 강의를 수강 중인 학생만 퀴즈를 제출할 수 있습니다."
                    )
                    return redirect("quizzes:quiz-detail", pk=quiz_id)

            # 진행 중인 시도 가져오기
            attempt = QuizAttempt.objects.filter(
                quiz=quiz, student=request.user, is_completed=False
            ).first()

            if not attempt:
                messages.error(request, "진행 중인 퀴즈 시도가 없습니다.")
                return redirect("quizzes:quiz-attempt", pk=quiz_id)

            # 트랜잭션으로 답변 저장 및 점수 계산
            with transaction.atomic():
                # 답변 처리
                for key, value in request.POST.items():
                    if key.startswith("answer_"):
                        question_id = key.replace("answer_", "")
                        choice_id = value

                        try:
                            question = Question.objects.get(id=question_id, quiz=quiz)
                            choice = Choice.objects.get(id=choice_id, question=question)

                            # 이미 답변이 있으면 업데이트, 없으면 생성
                            answer, created = Answer.objects.update_or_create(
                                attempt=attempt,
                                question=question,
                                defaults={"selected_choice": choice},
                            )
                        except (Question.DoesNotExist, Choice.DoesNotExist):
                            continue

                # 퀴즈 시도 완료 처리
                attempt.is_completed = True
                attempt.completed_at = timezone.now()
                attempt.save()

                # 점수 계산
                attempt.calculate_score()

            # 결과 페이지로 리다이렉트
            messages.success(request, "퀴즈가 성공적으로 제출되었습니다.")
            return redirect("quizzes:quiz-result", pk=quiz_id)

        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")


class QuizResultView(LoginRequiredMixin, View):
    """퀴즈 결과 페이지"""

    template_name = "quizzes/quiz_result.html"

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs.get("pk")
        try:
            quiz = Quiz.objects.get(id=quiz_id)

            # 강사이거나 수강 중인지 확인
            if not request.user.is_instructor():
                is_enrolled = quiz.course.enrollments.filter(
                    student=request.user
                ).exists()
                if not is_enrolled:
                    messages.error(
                        request,
                        "이 강의를 수강 중인 학생만 퀴즈 결과를 볼 수 있습니다.",
                    )
                    return redirect("quizzes:quiz-detail", pk=quiz_id)

            # 완료된 시도 가져오기
            attempt = (
                QuizAttempt.objects.filter(
                    quiz=quiz, student=request.user, is_completed=True
                )
                .order_by("-completed_at")
                .first()
            )

            if not attempt:
                messages.error(request, "완료된 퀴즈 시도가 없습니다.")
                return redirect("quizzes:quiz-attempt", pk=quiz_id)

            # 답변 가져오기 (question_id -> Answer)
            answers = Answer.objects.filter(attempt=attempt).select_related(
                "question", "selected_choice"
            )

            return render(
                request,
                self.template_name,
                {"quiz": quiz, "attempt": attempt, "answers": answers},
            )

        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 강사가 만든 강의 목록
        context["courses"] = Course.objects.filter(instructor=self.request.user)

        # URL에서 course_id가 제공되었는지 확인
        course_id = self.request.GET.get("course_id")
        if course_id:
            context["course_id"] = course_id
            try:
                course = Course.objects.get(id=course_id, instructor=self.request.user)
                context["sections"] = course.sections.all()
            except Course.DoesNotExist:
                pass

        return context

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quizzes:quiz-detail", kwargs={"pk": self.object.pk})


class QuizUpdateView(LoginRequiredMixin, UpdateView):
    """퀴즈 수정 페이지"""

    model = Quiz
    template_name = "quizzes/quiz_form.html"
    fields = ["title", "description", "course", "section", "lesson"]

    def dispatch(self, request, *args, **kwargs):
        quiz = self.get_object()
        if not request.user.is_instructor() or quiz.instructor != request.user:
            messages.error(request, "자신이 만든 퀴즈만 수정할 수 있습니다.")
            return redirect("quizzes:quiz-detail", pk=quiz.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 강사가 만든 강의 목록
        context["courses"] = Course.objects.filter(instructor=self.request.user)

        # 현재 선택된 course의 sections
        if self.object.course:
            context["sections"] = self.object.course.sections.all()

            # 현재 선택된 section의 lessons
            if self.object.section:
                context["lessons"] = self.object.section.lessons.all()

        return context

    def get_success_url(self):
        return reverse("quizzes:quiz-detail", kwargs={"pk": self.object.pk})


class QuizDeleteView(LoginRequiredMixin, DeleteView):
    """퀴즈 삭제 페이지"""

    model = Quiz
    template_name = "quizzes/quiz_confirm_delete.html"
    success_url = reverse_lazy("quizzes:quiz-list")

    def dispatch(self, request, *args, **kwargs):
        quiz = self.get_object()
        if not request.user.is_instructor() or quiz.instructor != request.user:
            messages.error(request, "자신이 만든 퀴즈만 삭제할 수 있습니다.")
            return redirect("quizzes:quiz-detail", pk=quiz.pk)
        return super().dispatch(request, *args, **kwargs)


class QuestionCreateView(LoginRequiredMixin, View):
    """문제 생성 페이지"""

    template_name = "quizzes/question_form.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_instructor():
            messages.error(request, "강사만 문제를 생성할 수 있습니다.")
            return redirect("quizzes:quiz-list")

        # URL에서 quiz_id 가져오기
        quiz_id = request.GET.get("quiz")
        if not quiz_id:
            messages.error(request, "퀴즈 ID가 필요합니다.")
            return redirect("quizzes:quiz-list")

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.instructor != request.user:
                messages.error(
                    request, "자신이 만든 퀴즈에만 문제를 추가할 수 있습니다."
                )
                return redirect("quizzes:quiz-detail", pk=quiz_id)
        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")

        return render(request, self.template_name, {"quiz_id": quiz_id})

    def post(self, request, *args, **kwargs):
        if not request.user.is_instructor():
            messages.error(request, "강사만 문제를 생성할 수 있습니다.")
            return redirect("quizzes:quiz-list")

        quiz_id = request.POST.get("quiz")
        if not quiz_id:
            messages.error(request, "퀴즈 ID가 필요합니다.")
            return redirect("quizzes:quiz-list")

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if quiz.instructor != request.user:
                messages.error(
                    request, "자신이 만든 퀴즈에만 문제를 추가할 수 있습니다."
                )
                return redirect("quizzes:quiz-detail", pk=quiz_id)
        except Quiz.DoesNotExist:
            messages.error(request, "존재하지 않는 퀴즈입니다.")
            return redirect("quizzes:quiz-list")

        # 문제 텍스트 및 순서
        text = request.POST.get("text")
        order = request.POST.get("order") or None

        # 유효성 검사
        if not text:
            messages.error(request, "문제 내용은 필수입니다.")
            return render(
                request,
                self.template_name,
                {"quiz_id": quiz_id, "form_errors": ["문제 내용은 필수입니다."]},
            )

        # 문제 생성
        with transaction.atomic():
            question = Question.objects.create(quiz=quiz, text=text, order=order)

            # 선택지 처리
            choice_count = 0
            has_correct_answer = False

            for key, value in request.POST.items():
                if key.startswith("choice_text_"):
                    choice_num = key.replace("choice_text_", "")
                    choice_text = value

                    # 빈 선택지는 무시
                    if not choice_text:
                        continue

                    is_correct = request.POST.get(f"is_correct_{choice_num}") == "on"
                    if is_correct:
                        has_correct_answer = True

                    Choice.objects.create(
                        question=question, text=choice_text, is_correct=is_correct
                    )

                    choice_count += 1

            # 최소 2개의 선택지와 1개 이상의 정답이 있는지 확인
            if choice_count < 2:
                question.delete()
                messages.error(request, "최소 2개의 선택지가 필요합니다.")
                return render(
                    request,
                    self.template_name,
                    {
                        "quiz_id": quiz_id,
                        "form_errors": ["최소 2개의 선택지가 필요합니다."],
                    },
                )

            if not has_correct_answer:
                question.delete()
                messages.error(request, "최소 1개의 정답이 필요합니다.")
                return render(
                    request,
                    self.template_name,
                    {
                        "quiz_id": quiz_id,
                        "form_errors": ["최소 1개의 정답이 필요합니다."],
                    },
                )

        messages.success(request, "문제가 성공적으로 추가되었습니다.")
        return redirect("quizzes:quiz-detail", pk=quiz_id)


class QuestionUpdateView(LoginRequiredMixin, View):
    """문제 수정 페이지"""

    template_name = "quizzes/question_form.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_instructor():
            messages.error(request, "강사만 문제를 수정할 수 있습니다.")
            return redirect("quizzes:quiz-list")

        question_id = kwargs.get("pk")
        try:
            question = Question.objects.get(id=question_id)
            if question.quiz.instructor != request.user:
                messages.error(request, "자신이 만든 퀴즈의 문제만 수정할 수 있습니다.")
                return redirect("quizzes:quiz-detail", pk=question.quiz.id)
        except Question.DoesNotExist:
            messages.error(request, "존재하지 않는 문제입니다.")
            return redirect("quizzes:quiz-list")

        return render(request, self.template_name, {"question": question})

    def post(self, request, *args, **kwargs):
        if not request.user.is_instructor():
            messages.error(request, "강사만 문제를 수정할 수 있습니다.")
            return redirect("quizzes:quiz-list")

        question_id = kwargs.get("pk")
        try:
            question = Question.objects.get(id=question_id)
            if question.quiz.instructor != request.user:
                messages.error(request, "자신이 만든 퀴즈의 문제만 수정할 수 있습니다.")
                return redirect("quizzes:quiz-detail", pk=question.quiz.id)
        except Question.DoesNotExist:
            messages.error(request, "존재하지 않는 문제입니다.")
            return redirect("quizzes:quiz-list")

        # 문제 텍스트 및 순서
        text = request.POST.get("text")
        order = request.POST.get("order") or None

        # 유효성 검사
        if not text:
            messages.error(request, "문제 내용은 필수입니다.")
            return render(
                request,
                self.template_name,
                {"question": question, "form_errors": ["문제 내용은 필수입니다."]},
            )

        # 문제 수정
        with transaction.atomic():
            question.text = text
            if order:
                question.order = order
            question.save()

            # 기존 선택지 삭제
            question.choices.all().delete()

            # 선택지 처리
            choice_count = 0
            has_correct_answer = False

            for key, value in request.POST.items():
                if key.startswith("choice_text_"):
                    choice_num = key.replace("choice_text_", "")
                    choice_text = value

                    # 빈 선택지는 무시
                    if not choice_text:
                        continue

                    is_correct = request.POST.get(f"is_correct_{choice_num}") == "on"
                    if is_correct:
                        has_correct_answer = True

                    Choice.objects.create(
                        question=question, text=choice_text, is_correct=is_correct
                    )

                    choice_count += 1

            # 최소 2개의 선택지와 1개 이상의 정답이 있는지 확인
            if choice_count < 2:
                messages.error(request, "최소 2개의 선택지가 필요합니다.")
                # 롤백은 되지만, 재생성을 위해 기존 선택지를 다시 불러옴
                for choice in question.choices.all():
                    Choice.objects.create(
                        question=question,
                        text=choice.text,
                        is_correct=choice.is_correct,
                    )
                return render(
                    request,
                    self.template_name,
                    {
                        "question": question,
                        "form_errors": ["최소 2개의 선택지가 필요합니다."],
                    },
                )

            if not has_correct_answer:
                messages.error(request, "최소 1개의 정답이 필요합니다.")
                # 롤백은 되지만, 재생성을 위해 기존 선택지를 다시 불러옴
                for choice in question.choices.all():
                    Choice.objects.create(
                        question=question,
                        text=choice.text,
                        is_correct=choice.is_correct,
                    )
                return render(
                    request,
                    self.template_name,
                    {
                        "question": question,
                        "form_errors": ["최소 1개의 정답이 필요합니다."],
                    },
                )

        messages.success(request, "문제가 성공적으로 수정되었습니다.")
        return redirect("quizzes:quiz-detail", pk=question.quiz.id)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    """문제 삭제 페이지"""

    model = Question
    template_name = "quizzes/question_confirm_delete.html"

    def get_success_url(self):
        return reverse("quizzes:quiz-detail", kwargs={"pk": self.object.quiz.pk})

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        if not request.user.is_instructor() or question.quiz.instructor != request.user:
            messages.error(request, "자신이 만든 퀴즈의 문제만 삭제할 수 있습니다.")
            return redirect("quizzes:quiz-detail", pk=question.quiz.pk)
        return super().dispatch(request, *args, **kwargs)
