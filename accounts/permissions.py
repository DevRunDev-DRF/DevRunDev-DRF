from rest_framework import permissions


class IsInstructor(permissions.BasePermission):
    """
    강사만 접근 가능한 권한
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_instructor()


class IsManager(permissions.BasePermission):
    """
    관리자만 접근 가능한 권한
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.MANAGER
        )
