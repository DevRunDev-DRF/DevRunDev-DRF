from rest_framework import permissions
from courses.models import Course
from enrollments.models import Enrollment


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    강사만 퀴즈를 생성, 수정, 삭제할 수 있고 다른 사용자는 조회만 가능
    """

    def has_permission(self, request, view):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 쓰기 요청은 강사만 허용
        return request.user.is_authenticated and request.user.is_instructor()


class IsQuizInstructor(permissions.BasePermission):
    """
    해당 퀴즈를 생성한 강사만 퀴즈를 수정, 삭제할 수 있음
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 객체 타입에 따라 instructor 확인 방법 분기
        # Question 객체인 경우
        if hasattr(obj, "quiz"):
            return obj.quiz.instructor == request.user
        # Quiz 객체인 경우
        elif hasattr(obj, "instructor"):
            return obj.instructor == request.user
        # 기타 객체 (Choice 등)
        elif hasattr(obj, "question") and hasattr(obj.question, "quiz"):
            return obj.question.quiz.instructor == request.user

        # 객체 타입을 확인할 수 없는 경우 기본적으로 거부
        return False


class IsEnrolledOrInstructor(permissions.BasePermission):
    """
    해당 강의를 수강 중인 학생이나 강사만 퀴즈에 접근 가능
    """

    def has_permission(self, request, view):
        # 인증된 사용자만 접근 가능
        if not request.user.is_authenticated:
            return False

        # 강사는 항상 접근 가능
        if request.user.is_instructor():
            return True

        # URL 파라미터에서 quiz_id 가져오기
        quiz_id = view.kwargs.get("pk")
        if not quiz_id:
            return False

        # 학생인 경우, 해당 강의에 등록되어 있는지 확인
        from quizzes.models import Quiz

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            return Enrollment.objects.filter(
                student=request.user,
                course=quiz.course,
                status__in=["in_progress", "completed"],
            ).exists()
        except Quiz.DoesNotExist:
            return False


class IsQuizAttemptOwner(permissions.BasePermission):
    """
    퀴즈 시도의 소유자(학생)만 자신의 시도 데이터에 접근 가능
    """

    def has_object_permission(self, request, view, obj):
        # 본인의 퀴즈 시도만 접근 가능
        return obj.student == request.user
