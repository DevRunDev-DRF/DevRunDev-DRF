from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from enrollments.models import Enrollment
from courses.models import Course, Lesson
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from .permissions import (
    IsQuestionOwnerOrReadOnly,
    IsAnswerOwnerOrReadOnly,
    CanAcceptAnswer,
)


class QuestionViewSet(viewsets.ModelViewSet):
    """질문 API 뷰셋"""

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsQuestionOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "lesson", "user", "is_resolved"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """사용자 권한에 따라 다른 쿼리셋 반환"""
        queryset = Question.objects.all()

        # 특정 강의에 대한 질문만 필터링
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # 특정 레슨에 대한 질문만 필터링
        lesson_id = self.request.query_params.get("lesson")
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        # 강사인 경우 본인 강의에 대한 질문만 조회
        if self.request.user.is_instructor():
            user_courses = Course.objects.filter(instructor=self.request.user)
            queryset = queryset.filter(course__in=user_courses)

        # 학생인 경우 본인이 수강 중인 강의의 질문만 조회
        elif not self.request.user.is_staff and not self.request.user.is_instructor():
            enrolled_courses = Course.objects.filter(
                enrollments__student=self.request.user
            )
            queryset = queryset.filter(course__in=enrolled_courses) | queryset.filter(
                user=self.request.user
            )

        return queryset

    def perform_create(self, serializer):
        """질문 생성 시 현재 사용자를 작성자로 설정"""
        # 수강 중인 강의인지 확인 (강사 제외)
        if not self.request.user.is_instructor() and not self.request.user.is_staff:
            course_id = self.request.data.get("course")
            is_enrolled = Enrollment.objects.filter(
                student=self.request.user, course_id=course_id
            ).exists()

            if not is_enrolled:
                raise permissions.PermissionDenied(
                    "수강 중인 강의에만 질문을 작성할 수 있습니다."
                )

        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_resolved(self, request, pk=None):
        """질문을 해결됨으로 표시"""
        question = self.get_object()

        # 질문 작성자 또는 강의 강사만 가능
        if question.user != request.user and (
            not request.user.is_instructor()
            or question.course.instructor != request.user
        ):
            return Response(
                {"detail": "이 작업을 수행할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        question.is_resolved = True
        question.save()

        return Response({"status": "질문이 해결됨으로 표시되었습니다."})

    @action(detail=True, methods=["post"])
    def mark_as_unresolved(self, request, pk=None):
        """질문을 미해결로 표시"""
        question = self.get_object()

        # 질문 작성자 또는 강의 강사만 가능
        if question.user != request.user and (
            not request.user.is_instructor()
            or question.course.instructor != request.user
        ):
            return Response(
                {"detail": "이 작업을 수행할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        question.is_resolved = False
        question.save()

        # 채택된 답변이 있으면 채택 취소
        Answer.objects.filter(question=question, is_accepted=True).update(
            is_accepted=False
        )

        return Response({"status": "질문이 미해결로 표시되었습니다."})


class AnswerViewSet(viewsets.ModelViewSet):
    """답변 API 뷰셋"""

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated, IsAnswerOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["question", "user", "is_accepted"]
    ordering_fields = ["created_at", "is_accepted"]
    ordering = ["-is_accepted", "-created_at"]

    def get_queryset(self):
        """사용자 권한에 따라 다른 쿼리셋 반환"""
        queryset = Answer.objects.all()

        # 특정 질문에 대한 답변만 필터링
        question_id = self.request.query_params.get("question")
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        return queryset

    def perform_create(self, serializer):
        """답변 생성 시 현재 사용자를 작성자로 설정"""
        # 수강 중인 강의인지 확인 (강사 제외)
        if not self.request.user.is_instructor() and not self.request.user.is_staff:
            question_id = self.request.data.get("question")
            question = get_object_or_404(Question, id=question_id)

            is_enrolled = Enrollment.objects.filter(
                student=self.request.user, course=question.course
            ).exists()

            if not is_enrolled:
                raise permissions.PermissionDenied(
                    "수강 중인 강의의 질문에만 답변을 작성할 수 있습니다."
                )

        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, CanAcceptAnswer],
    )
    def accept(self, request, pk=None):
        """답변을 채택"""
        answer = self.get_object()

        with transaction.atomic():
            # 모든 답변의 채택 상태를 False로 설정
            Answer.objects.filter(question=answer.question).update(is_accepted=False)

            # 현재 답변을 채택됨으로 설정
            answer.is_accepted = True
            answer.save()

            # 질문을 해결됨으로 표시
            answer.question.is_resolved = True
            answer.question.save()

        return Response({"status": "답변이 채택되었습니다."})

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, CanAcceptAnswer],
    )
    def unaccept(self, request, pk=None):
        """답변 채택 취소"""
        answer = self.get_object()

        if not answer.is_accepted:
            return Response(
                {"detail": "이미 채택되지 않은 답변입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 채택 상태를 취소
            answer.is_accepted = False
            answer.save()

            # 질문의 해결 상태도 같이 변경
            answer.question.is_resolved = False
            answer.question.save()

        return Response({"status": "답변 채택이 취소되었습니다."})


# 템플릿 기반 뷰 추가
@login_required
def question_list_view(request, course_id=None):
    """질문 목록 페이지"""
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        # 수강중인지 확인 (강사 제외)
        if not request.user.is_instructor() and not request.user.is_staff:
            is_enrolled = Enrollment.objects.filter(
                student=request.user, course=course
            ).exists()

            if not is_enrolled:
                messages.error(
                    request, "해당 강의를 수강 중인 학생만 접근할 수 있습니다."
                )
                return redirect("courses:course-detail", pk=course_id)

        questions = Question.objects.filter(course=course).order_by("-created_at")
        context = {
            "course": course,
            "questions": questions,
            "cart_count": (
                request.user.cart_items.count() if request.user.is_authenticated else 0
            ),
        }
        return render(request, "qna/question_list.html", context)
    else:
        # 전체 질문 목록
        if request.user.is_instructor():
            # 강사인 경우 자신의 강의 질문만 표시
            questions = Question.objects.filter(
                course__instructor=request.user
            ).order_by("-created_at")
        elif request.user.is_staff:
            # 관리자는 모든 질문 볼 수 있음
            questions = Question.objects.all().order_by("-created_at")
        else:
            # 학생인 경우 수강 중인 강의 질문과 자신이 작성한 질문만 표시
            enrolled_courses = Course.objects.filter(enrollments__student=request.user)
            questions = (
                Question.objects.filter(
                    models.Q(course__in=enrolled_courses) | models.Q(user=request.user)
                )
                .distinct()
                .order_by("-created_at")
            )

        context = {
            "questions": questions,
            "cart_count": (
                request.user.cart_items.count() if request.user.is_authenticated else 0
            ),
        }
        return render(request, "qna/question_list.html", context)


@login_required
def question_detail_view(request, pk):
    """질문 상세 페이지"""
    question = get_object_or_404(Question, id=pk)

    # 수강중인지 확인 (강사, 작성자 제외)
    if (
        not request.user.is_instructor()
        and not request.user.is_staff
        and question.user != request.user
    ):
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=question.course
        ).exists()

        if not is_enrolled:
            messages.error(request, "해당 강의를 수강 중인 학생만 접근할 수 있습니다.")
            return redirect("courses:course-detail", pk=question.course.id)

    # 답변 작성 처리
    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            Answer.objects.create(question=question, user=request.user, content=content)
            messages.success(request, "답변이 작성되었습니다.")
            return redirect("qna:question-detail", pk=question.id)
        else:
            messages.error(request, "답변 내용을 입력해주세요.")

    # 답변 목록
    answers = Answer.objects.filter(question=question).order_by(
        "-is_accepted", "-created_at"
    )

    context = {
        "question": question,
        "answers": answers,
        "can_accept": question.user == request.user
        or (
            request.user.is_instructor() and question.course.instructor == request.user
        ),
        "cart_count": (
            request.user.cart_items.count() if request.user.is_authenticated else 0
        ),
    }
    return render(request, "qna/question_detail.html", context)


@login_required
def question_create_view(request, course_id=None):
    """질문 작성 페이지"""
    if course_id:
        course = get_object_or_404(Course, id=course_id)

        # 수강중인지 확인 (강사 제외)
        if not request.user.is_instructor() and not request.user.is_staff:
            is_enrolled = Enrollment.objects.filter(
                student=request.user, course=course
            ).exists()

            if not is_enrolled:
                messages.error(
                    request, "해당 강의를 수강 중인 학생만 질문을 작성할 수 있습니다."
                )
                return redirect("courses:course-detail", pk=course_id)
    else:
        course = None

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        course_id = request.POST.get("course")
        lesson_id = request.POST.get("lesson")

        if not title or not content or not course_id:
            messages.error(request, "제목, 내용, 강의는 필수 입력 항목입니다.")
            return render(
                request,
                "qna/question_form.html",
                {
                    "course": course,
                    "cart_count": (
                        request.user.cart_items.count()
                        if request.user.is_authenticated
                        else 0
                    ),
                },
            )

        try:
            course = Course.objects.get(id=course_id)

            # 수강중인지 확인 (강사 제외)
            if not request.user.is_instructor() and not request.user.is_staff:
                is_enrolled = Enrollment.objects.filter(
                    student=request.user, course=course
                ).exists()

                if not is_enrolled:
                    messages.error(
                        request,
                        "해당 강의를 수강 중인 학생만 질문을 작성할 수 있습니다.",
                    )
                    return redirect("courses:course-detail", pk=course_id)

            # 질문 생성
            question = Question(
                user=request.user, course=course, title=title, content=content
            )

            # 레슨이 선택되었으면 연결
            if lesson_id:
                try:
                    lesson = Lesson.objects.get(id=lesson_id, section__course=course)
                    question.lesson = lesson
                except Lesson.DoesNotExist:
                    pass

            question.save()

            messages.success(request, "질문이 성공적으로 작성되었습니다.")
            return redirect("qna:question-detail", pk=question.id)

        except Course.DoesNotExist:
            messages.error(request, "선택한 강의가 존재하지 않습니다.")

    # GET 요청: 폼 렌더링
    lessons = []
    if course:
        lessons = Lesson.objects.filter(section__course=course).order_by(
            "section__order", "order"
        )

    # 수강 중인 강의 목록 (강사가 아닌 경우)
    available_courses = []
    if request.user.is_instructor():
        available_courses = Course.objects.filter(instructor=request.user)
    elif request.user.is_staff:
        available_courses = Course.objects.all()
    else:
        available_courses = Course.objects.filter(enrollments__student=request.user)

    context = {
        "course": course,
        "lessons": lessons,
        "available_courses": available_courses,
        "cart_count": (
            request.user.cart_items.count() if request.user.is_authenticated else 0
        ),
    }
    return render(request, "qna/question_form.html", context)


@login_required
def question_edit_view(request, pk):
    """질문 수정 페이지"""
    question = get_object_or_404(Question, id=pk)

    # 권한 확인 - 본인 질문만 수정 가능
    if question.user != request.user:
        messages.error(request, "본인이 작성한 질문만 수정할 수 있습니다.")
        return redirect("qna:question-detail", pk=question.id)

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        lesson_id = request.POST.get("lesson")

        if not title or not content:
            messages.error(request, "제목과 내용은 필수 입력 항목입니다.")
            return render(
                request,
                "qna/question_form.html",
                {
                    "question": question,
                    "course": question.course,
                    "cart_count": request.user.cart_items.count(),
                },
            )

        # 질문 수정
        question.title = title
        question.content = content

        # 레슨이 선택되었으면 연결
        if lesson_id:
            try:
                lesson = Lesson.objects.get(
                    id=lesson_id, section__course=question.course
                )
                question.lesson = lesson
            except Lesson.DoesNotExist:
                question.lesson = None
        else:
            question.lesson = None

        question.save()

        messages.success(request, "질문이 성공적으로 수정되었습니다.")
        return redirect("qna:question-detail", pk=question.id)

    # GET 요청: 폼 렌더링
    lessons = Lesson.objects.filter(section__course=question.course).order_by(
        "section__order", "order"
    )

    context = {
        "question": question,
        "course": question.course,
        "lessons": lessons,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "qna/question_form.html", context)


@login_required
def question_delete_view(request, pk):
    """질문 삭제"""
    question = get_object_or_404(Question, id=pk)
    course_id = question.course.id

    # 권한 확인 - 본인 질문 또는 강사(본인 강의의 경우)만 삭제 가능
    if (
        question.user != request.user
        and not (
            request.user.is_instructor() and question.course.instructor == request.user
        )
        and not request.user.is_staff
    ):
        messages.error(request, "이 질문을 삭제할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=question.id)

    if request.method == "POST":
        question.delete()
        messages.success(request, "질문이 삭제되었습니다.")
        return redirect("qna:question-list-course", course_id=course_id)

    # GET 요청: 삭제 확인 페이지
    context = {
        "question": question,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "qna/question_confirm_delete.html", context)


@login_required
def answer_edit_view(request, pk):
    """답변 수정 페이지"""
    answer = get_object_or_404(Answer, id=pk)

    # 권한 확인 - 본인 답변만 수정 가능
    if answer.user != request.user:
        messages.error(request, "본인이 작성한 답변만 수정할 수 있습니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    if request.method == "POST":
        content = request.POST.get("content")

        if not content:
            messages.error(request, "내용은 필수 입력 항목입니다.")
            context = {
                "answer": answer,
                "cart_count": request.user.cart_items.count(),
            }
            return render(request, "qna/answer_form.html", context)


# qna/views.py (계속)
@login_required
def answer_edit_view(request, pk):
    """답변 수정 페이지"""
    answer = get_object_or_404(Answer, id=pk)

    # 권한 확인 - 본인 답변만 수정 가능
    if answer.user != request.user:
        messages.error(request, "본인이 작성한 답변만 수정할 수 있습니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    if request.method == "POST":
        content = request.POST.get("content")

        if not content:
            messages.error(request, "내용은 필수 입력 항목입니다.")
            context = {
                "answer": answer,
                "cart_count": request.user.cart_items.count(),
            }
            return render(request, "qna/answer_form.html", context)

        # 답변 수정
        answer.content = content
        answer.save()

        messages.success(request, "답변이 성공적으로 수정되었습니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    # GET 요청: 폼 렌더링
    context = {
        "answer": answer,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "qna/answer_form.html", context)


@login_required
def answer_delete_view(request, pk):
    """답변 삭제"""
    answer = get_object_or_404(Answer, id=pk)
    question_id = answer.question.id

    # 권한 확인 - 본인 답변 또는 강사(본인 강의의 경우)만 삭제 가능
    if (
        answer.user != request.user
        and not (
            request.user.is_instructor()
            and answer.question.course.instructor == request.user
        )
        and not request.user.is_staff
    ):
        messages.error(request, "이 답변을 삭제할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=question_id)

    if request.method == "POST":
        # 채택된 답변인 경우, 질문의 해결 상태도 업데이트
        if answer.is_accepted:
            answer.question.is_resolved = False
            answer.question.save()

        answer.delete()
        messages.success(request, "답변이 삭제되었습니다.")
        return redirect("qna:question-detail", pk=question_id)

    # GET 요청: 삭제 확인 페이지
    context = {
        "answer": answer,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "qna/answer_confirm_delete.html", context)


@login_required
def answer_accept_view(request, pk):
    """답변 채택"""
    answer = get_object_or_404(Answer, id=pk)

    # 권한 확인 - 질문 작성자 또는 강의 강사만 채택 가능
    if answer.question.user != request.user and not (
        request.user.is_instructor()
        and answer.question.course.instructor == request.user
    ):
        messages.error(request, "답변을 채택할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    with transaction.atomic():
        # 모든 답변의 채택 상태를 False로 설정
        Answer.objects.filter(question=answer.question).update(is_accepted=False)

        # 현재 답변을 채택됨으로 설정
        answer.is_accepted = True
        answer.save()

        # 질문을 해결됨으로 표시
        answer.question.is_resolved = True
        answer.question.save()

    messages.success(request, "답변이 채택되었습니다.")
    return redirect("qna:question-detail", pk=answer.question.id)


@login_required
def answer_unaccept_view(request, pk):
    """답변 채택 취소"""
    answer = get_object_or_404(Answer, id=pk)

    # 권한 확인 - 질문 작성자 또는 강의 강사만 채택 취소 가능
    if answer.question.user != request.user and not (
        request.user.is_instructor()
        and answer.question.course.instructor == request.user
    ):
        messages.error(request, "답변 채택을 취소할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    if not answer.is_accepted:
        messages.error(request, "이미 채택되지 않은 답변입니다.")
        return redirect("qna:question-detail", pk=answer.question.id)

    with transaction.atomic():
        # 채택 상태를 취소
        answer.is_accepted = False
        answer.save()

        # 질문의 해결 상태도 같이 변경
        answer.question.is_resolved = False
        answer.question.save()

    messages.success(request, "답변 채택이 취소되었습니다.")
    return redirect("qna:question-detail", pk=answer.question.id)


@login_required
def question_mark_resolved_view(request, pk):
    """질문을 해결됨으로 표시"""
    question = get_object_or_404(Question, id=pk)

    # 권한 확인 - 질문 작성자 또는 강의 강사만 가능
    if question.user != request.user and not (
        request.user.is_instructor() and question.course.instructor == request.user
    ):
        messages.error(request, "이 작업을 수행할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=question.id)

    question.is_resolved = True
    question.save()

    messages.success(request, "질문이 해결됨으로 표시되었습니다.")
    return redirect("qna:question-detail", pk=question.id)


@login_required
def question_mark_unresolved_view(request, pk):
    """질문을 미해결로 표시"""
    question = get_object_or_404(Question, id=pk)

    # 권한 확인 - 질문 작성자 또는 강의 강사만 가능
    if question.user != request.user and not (
        request.user.is_instructor() and question.course.instructor == request.user
    ):
        messages.error(request, "이 작업을 수행할 권한이 없습니다.")
        return redirect("qna:question-detail", pk=question.id)

    question.is_resolved = False
    question.save()

    # 채택된 답변이 있으면 채택 취소
    Answer.objects.filter(question=question, is_accepted=True).update(is_accepted=False)

    messages.success(request, "질문이 미해결로 표시되었습니다.")
    return redirect("qna:question-detail", pk=question.id)
