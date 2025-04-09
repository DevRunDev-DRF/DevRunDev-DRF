from rest_framework import permissions


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    리뷰 소유자만 수정/삭제 가능, 다른 사용자는 조회만 가능
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 요청은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 요청은 해당 리뷰의 작성자만 허용
        return obj.user == request.user
