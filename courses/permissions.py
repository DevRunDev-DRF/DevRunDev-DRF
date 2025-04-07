from rest_framework import permissions


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    강의 관련 작업은 강사만 수정 가능, 다른 사용자는 조회만 가능
    """

    def has_permission(self, request, view):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 쓰기 요청은 강사만 허용
        return request.user.is_authenticated and request.user.is_instructor()


class IsOwnerInstructorOrReadOnly(permissions.BasePermission):
    """
    강의의 생성자(강사)만 수정 가능, 다른 사용자는 조회만 가능
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        # 쓰기 요청은 해당 강의의 강사만 허용
        return obj.instructor == request.user
