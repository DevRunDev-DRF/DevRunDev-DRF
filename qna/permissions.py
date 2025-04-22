from rest_framework import permissions


class IsQuestionOwnerOrReadOnly(permissions.BasePermission):
    """
    질문 소유자만 수정/삭제 가능, 다른 사용자는 조회만 가능
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 관리자는 모든 작업 가능
        if request.user.is_staff or request.user.role == request.user.Role.MANAGER:
            return True

        # 강사는 자신의 강의에 대한 질문은 수정 가능
        if request.user.is_instructor() and obj.course.instructor == request.user:
            return True

        # 일반 사용자는 자신의 질문만 수정 가능
        return obj.user == request.user


class IsAnswerOwnerOrReadOnly(permissions.BasePermission):
    """
    답변 소유자만 수정/삭제 가능, 다른 사용자는 조회만 가능
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 관리자는 모든 작업 가능
        if request.user.is_staff or request.user.role == request.user.Role.MANAGER:
            return True

        # 강사는 자신의 강의에 대한 답변은 수정 가능
        if (
            request.user.is_instructor()
            and obj.question.course.instructor == request.user
        ):
            return True

        # 일반 사용자는 자신의 답변만 수정 가능
        return obj.user == request.user


class CanAcceptAnswer(permissions.BasePermission):
    """
    질문 작성자 또는 강의 강사만 답변 채택 가능
    """

    def has_object_permission(self, request, view, obj):
        # 질문 작성자인 경우
        if obj.question.user == request.user:
            return True

        # 강의 강사인 경우
        if (
            request.user.is_instructor()
            and obj.question.course.instructor == request.user
        ):
            return True

        return False
