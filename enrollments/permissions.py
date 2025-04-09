from rest_framework import permissions
from .models import Enrollment


class IsEnrollmentOwner(permissions.BasePermission):
    """
    수강 신청 소유자(학생)만 자신의 수강 정보에 접근 가능
    """

    def has_permission(self, request, view):
        # pk가 있는 경우 (detail=True), 해당 객체를 소유하고 있는지 확인
        if view.kwargs.get("pk") is not None:
            try:
                enrollment = Enrollment.objects.get(pk=view.kwargs["pk"])
                return enrollment.student == request.user
            except Enrollment.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        return obj.student == request.user


class IsCartItemOwner(permissions.BasePermission):
    """
    장바구니 아이템 소유자만 자신의 장바구니에 접근 가능
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
