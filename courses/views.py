from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.generic.edit import FormView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from enrollments.models import Enrollment, CartItem, LessonProgress
from quizzes.models import Quiz
from reviews.models import Review
from .models import Course, Section, Lesson
from .permissions import IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    SectionSerializer,
    LessonSerializer,
)
from .forms import CourseForm, SectionForm, LessonForm


# REST API 뷰셋 (기존 코드 유지)
class CourseViewSet(viewsets.ModelViewSet):
    """
    강의 관련 API 뷰셋
    """

    queryset = Course.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "instructor"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "price", "avg_rating"]
    ordering = ["-created_at"]
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        queryset = Course.objects.all()

        # 승인된 강의만 조회 (강사가 자신의 강의 조회 시에는 모든 상태 조회 가능)
        if self.request.user.is_authenticated and self.request.user.is_instructor():
            if self.action == "list":
                instructor_id = self.request.query_params.get("instructor")
                if instructor_id and int(instructor_id) == self.request.user.id:
                    return queryset

        # 일반 사용자에게는 승인된 강의만 보여줌
        return queryset.filter(status="approved")

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user, status="review")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """
        강의 수강 신청 API (다른 앱과 상호작용)
        """
        course = self.get_object()

        # 자신의 강의인 경우 수강 신청 불필요
        if request.user == course.instructor:
            return Response(
                {"detail": "본인의 강의는 수강 신청 없이 자동 접근 가능합니다."}
            )

        # enrollments 앱 로직 호출 (추후 구현)
        from enrollments.models import Enrollment

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "이미 수강 중인 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Enrollment.objects.create(
            student=request.user, course=course, status="in_progress", progress=0
        )

        return Response(
            {"detail": f"'{course.title}' 수강 신청이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )


class SectionViewSet(viewsets.ModelViewSet):
    """
    섹션 관련 API 뷰셋
    """

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_queryset(self):
        queryset = Section.objects.all()

        # URL에서 course_id 파라미터를 가져옴
        course_id = self.request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.order_by("order")

    def perform_create(self, serializer):
        course_id = self.request.data.get("course_id")
        course = Course.objects.get(id=course_id)

        # 강의의 작성자만 섹션 추가 가능
        if course.instructor != self.request.user:
            raise PermissionDenied(
                "You don't have permission to add sections to this course."
            )

        serializer.save(course=course)


class LessonViewSet(viewsets.ModelViewSet):
    """
    레슨 관련 API 뷰셋
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrReadOnly, IsOwnerInstructorOrReadOnly]

    def get_queryset(self):
        queryset = Lesson.objects.all()

        # URL에서 section_id 파라미터를 가져옴
        section_id = self.request.query_params.get("section_id")
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        return queryset.order_by("order")

    def perform_create(self, serializer):
        section_id = self.request.data.get("section_id")
        section = Section.objects.get(id=section_id)

        # 섹션이 속한 강의의 작성자만 레슨 추가 가능
        if section.course.instructor != self.request.user:
            raise PermissionDenied(
                "You don't have permission to add lessons to this section."
            )

        serializer.save(section=section)


# 템플릿 기반 뷰 (새로 추가)
class CourseListView(ListView):
    """강의 목록 페이지"""

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(status="approved")

        # 검색어
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # 정렬
        ordering = self.request.GET.get("ordering", "-created_at")
        if ordering:
            queryset = queryset.order_by(ordering)

        # 강사 필터 (강사인 경우만)
        if self.request.user.is_authenticated and self.request.user.is_instructor():
            instructor_id = self.request.GET.get("instructor")
            if instructor_id:
                queryset = Course.objects.filter(instructor_id=instructor_id)

            # 상태 필터 (강사인 경우만)
            status_filter = self.request.GET.get("status")
            if status_filter and status_filter != "all":
                queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 로그인 사용자가 수강 중인 강의 목록
        if self.request.user.is_authenticated:
            enrolled_courses = Course.objects.filter(
                enrollments__student=self.request.user
            )
            context["enrolled_courses"] = enrolled_courses

            # 장바구니 수 가져오기
            context["cart_count"] = CartItem.objects.filter(
                user=self.request.user
            ).count()

        return context


class CourseDetailView(DetailView):
    """강의 상세 페이지"""

    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user

        # 수강 여부 확인
        if user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(
                student=user, course=course
            ).exists()

            # 장바구니에 담겨있는지 확인
            context["in_cart"] = CartItem.objects.filter(
                user=user, course=course
            ).exists()

            # 이미 리뷰를 작성했는지 확인
            context["user_review"] = Review.objects.filter(
                user=user, course=course
            ).first()

            # 장바구니 수 가져오기
            context["cart_count"] = CartItem.objects.filter(user=user).count()

        # 퀴즈 목록 (수강생 및 강사용)
        if user.is_authenticated and (
            context.get("is_enrolled") or user == course.instructor
        ):
            context["quizzes"] = Quiz.objects.filter(course=course)

        return context


@method_decorator(login_required, name="dispatch")
class CourseCreateView(CreateView):
    """강의 생성 페이지"""

    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def dispatch(self, request, *args, **kwargs):
        # 강사 권한 확인
        if not request.user.is_instructor():
            messages.error(request, "강사만 강의를 생성할 수 있습니다.")
            return redirect("courses:course-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        form.instance.status = "review"
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request, "강의가 생성되었습니다. 관리자 승인 후 공개됩니다."
        )
        return reverse("courses:course-detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class CourseUpdateView(UpdateView):
    """강의 수정 페이지"""

    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def get_queryset(self):
        # 본인의 강의만 수정 가능
        return Course.objects.filter(instructor=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "강의가 수정되었습니다.")
        return reverse("courses:course-detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class CourseDeleteView(DeleteView):
    """강의 삭제"""

    model = Course

    def get_queryset(self):
        # 본인의 강의만 삭제 가능
        return Course.objects.filter(instructor=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "강의가 삭제되었습니다.")
        return reverse("courses:course-list")

    # GET 요청으로 접근하면 상세 페이지로 리다이렉트
    def get(self, request, *args, **kwargs):
        return redirect("courses:course-detail", pk=kwargs.get("pk"))


@method_decorator(login_required, name="dispatch")
class SectionCreateView(CreateView):
    """섹션 생성 페이지"""

    model = Section
    form_class = SectionForm
    template_name = "courses/section_form.html"

    def dispatch(self, request, *args, **kwargs):
        # 강사 권한 확인
        if not request.user.is_instructor():
            messages.error(request, "강사만 섹션을 생성할 수 있습니다.")
            return redirect("courses:course-list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.request.GET.get("course_id")
        if course_id:
            context["course"] = get_object_or_404(
                Course, id=course_id, instructor=self.request.user
            )
        return context

    def form_valid(self, form):
        course_id = self.request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id, instructor=self.request.user)
        form.instance.course = course
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "섹션이 생성되었습니다.")
        return reverse("courses:section-edit", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class SectionUpdateView(UpdateView):
    """섹션 수정 페이지"""

    model = Section
    form_class = SectionForm
    template_name = "courses/section_form.html"
    context_object_name = "section"

    def get_queryset(self):
        # 본인 강의의 섹션만 수정 가능
        return Section.objects.filter(course__instructor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.object.course
        return context

    def get_success_url(self):
        messages.success(self.request, "섹션이 수정되었습니다.")
        return reverse("courses:section-edit", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class SectionDeleteView(DeleteView):
    """섹션 삭제"""

    model = Section

    def get_queryset(self):
        # 본인 강의의 섹션만 삭제 가능
        return Section.objects.filter(course__instructor=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "섹션이 삭제되었습니다.")
        return reverse("courses:course-detail", kwargs={"pk": self.object.course.pk})


@method_decorator(login_required, name="dispatch")
class LessonCreateView(CreateView):
    """레슨 생성 페이지"""

    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def dispatch(self, request, *args, **kwargs):
        # 강사 권한 확인
        if not request.user.is_instructor():
            messages.error(request, "강사만 레슨을 생성할 수 있습니다.")
            return redirect("courses:course-list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id = self.request.GET.get("section_id")
        if section_id:
            context["section"] = get_object_or_404(
                Section, id=section_id, course__instructor=self.request.user
            )
        return context

    def form_valid(self, form):
        section_id = self.request.POST.get("section_id")
        section = get_object_or_404(
            Section, id=section_id, course__instructor=self.request.user
        )
        form.instance.section = section
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "레슨이 생성되었습니다.")
        return reverse("courses:section-edit", kwargs={"pk": self.object.section.pk})


@method_decorator(login_required, name="dispatch")
class LessonUpdateView(UpdateView):
    """레슨 수정 페이지"""

    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"
    context_object_name = "lesson"

    def get_queryset(self):
        # 본인 강의의 레슨만 수정 가능
        return Lesson.objects.filter(section__course__instructor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = self.object.section
        return context

    def get_success_url(self):
        messages.success(self.request, "레슨이 수정되었습니다.")
        return reverse("courses:lesson-edit", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
class LessonDeleteView(DeleteView):
    """레슨 삭제"""

    model = Lesson

    def get_queryset(self):
        # 본인 강의의 레슨만 삭제 가능
        return Lesson.objects.filter(section__course__instructor=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "레슨이 삭제되었습니다.")
        return reverse("courses:section-edit", kwargs={"pk": self.object.section.pk})


class LessonDetailView(DetailView):
    """레슨 상세 페이지"""

    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_queryset(self):
        # 승인된 강의의 레슨만 조회 가능 (강사 제외)
        queryset = Lesson.objects.all()
        if self.request.user.is_authenticated and self.request.user.is_instructor():
            # 강사의 경우 자신의 강의 레슨 모두 조회 가능
            return queryset.filter(
                Q(section__course__instructor=self.request.user)
                | Q(section__course__status="approved")
            )
        return queryset.filter(section__course__status="approved")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        user = self.request.user

        # 수강 여부 확인
        if user.is_authenticated:
            context["is_enrolled"] = Enrollment.objects.filter(
                student=user, course=lesson.section.course
            ).exists()

            # 강사 여부 확인
            context["is_instructor"] = user == lesson.section.course.instructor

            # 수강생 또는 강사가 아닌 경우 접근 제한
            if not (context["is_enrolled"] or context["is_instructor"]):
                return redirect("courses:course-detail", pk=lesson.section.course.id)

            # 레슨 진행 상태 확인
            if context["is_enrolled"]:
                context["lesson_progress"], created = (
                    LessonProgress.objects.get_or_create(student=user, lesson=lesson)
                )

                # 모든 레슨 진행 상태를 맵으로 가져오기
                lesson_progress_list = LessonProgress.objects.filter(
                    student=user,
                    lesson__section__course=lesson.section.course,
                    completed=True,
                ).values_list("lesson_id", flat=True)

                context["lesson_progress_map"] = {
                    lesson_id: True for lesson_id in lesson_progress_list
                }

                # 진행 정보 업데이트 (마지막 시청 레슨)
                enrollment = Enrollment.objects.get(
                    student=user, course=lesson.section.course
                )
                enrollment.last_watched_lesson = lesson
                enrollment.save()

            # 연관된 퀴즈 가져오기
            context["quizzes"] = Quiz.objects.filter(
                Q(lesson=lesson) | Q(section=lesson.section)
            )

            # 이전 및 다음 레슨 찾기
            course_lessons = Lesson.objects.filter(
                section__course=lesson.section.course
            ).order_by("section__order", "order")

            lesson_index = list(course_lessons).index(lesson)

            if lesson_index > 0:
                context["prev_lesson"] = course_lessons[lesson_index - 1]

            if lesson_index < len(course_lessons) - 1:
                context["next_lesson"] = course_lessons[lesson_index + 1]

        return context


@method_decorator(login_required, name="dispatch")
class InstructorDashboardView(ListView):
    """강사 대시보드"""

    model = Course
    template_name = "courses/instructor_dashboard.html"
    context_object_name = "courses"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # 강사 권한 확인
        if not request.user.is_instructor():
            messages.error(request, "강사만 접근할 수 있습니다.")
            return redirect("courses:course-list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # 본인의 강의만 조회
        queryset = Course.objects.filter(instructor=self.request.user)

        # 상태별 필터링
        status = self.request.GET.get("status")
        if status and status != "all":
            queryset = queryset.filter(status=status)

        # 정렬
        queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 통계 정보
        instructor_courses = Course.objects.filter(instructor=self.request.user)

        context["courses_count"] = instructor_courses.count()
        context["approved_count"] = instructor_courses.filter(status="approved").count()
        context["review_count"] = instructor_courses.filter(status="review").count()
        context["not_approved_count"] = instructor_courses.filter(
            status="not_approved"
        ).count()

        # 총 학생 수 (중복 제거)
        context["total_students"] = (
            Enrollment.objects.filter(course__instructor=self.request.user)
            .values("student")
            .distinct()
            .count()
        )

        # 평균 평점
        context["avg_rating"] = (
            instructor_courses.aggregate(avg=models.Avg("avg_rating"))["avg"] or 0
        )

        # 총 리뷰 수
        context["total_reviews"] = Review.objects.filter(
            course__instructor=self.request.user
        ).count()

        # 최근 리뷰 5개
        context["recent_reviews"] = Review.objects.filter(
            course__instructor=self.request.user
        ).order_by("-created_at")[:5]

        # 장바구니 수
        context["cart_count"] = CartItem.objects.filter(user=self.request.user).count()

        return context


class SearchCoursesView(ListView):
    """강의 검색 결과 페이지"""

    model = Course
    template_name = "courses/search_results.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(status="approved")

        # 검색어
        self.query = self.request.GET.get("search", "")
        if self.query:
            queryset = queryset.filter(
                Q(title__icontains=self.query) | Q(description__icontains=self.query)
            )

        # 정렬
        ordering = self.request.GET.get("ordering", "-created_at")
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query

        # 로그인 사용자가 수강 중인 강의 목록
        if self.request.user.is_authenticated:
            enrolled_courses = Course.objects.filter(
                enrollments__student=self.request.user
            )
            context["enrolled_courses"] = enrolled_courses

            # 장바구니 수 가져오기
            context["cart_count"] = CartItem.objects.filter(
                user=self.request.user
            ).count()

        return context
