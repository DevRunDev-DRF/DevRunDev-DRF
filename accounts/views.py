from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import logout

from .models import User, InstructorApplication
from .serializers import (
    UserSerializer,
    InstructorApplicationSerializer,
    RegisterSerializer,
    LoginSerializer,
)


class RegisterView(generics.CreateAPIView):
    """회원 가입 API"""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 토큰 생성
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """로그인 API"""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # 토큰 생성 또는 가져오기
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            }
        )


class LogoutView(APIView):
    """로그아웃 API"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 토큰 삭제
        request.user.auth_token.delete()

        # 세션 기반 로그아웃 (선택사항)
        logout(request)

        return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """액션에 따라 권한 다르게 설정"""
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=["put", "patch"], permission_classes=[IsAuthenticated]
    )
    def update_me(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InstructorApplicationViewSet(viewsets.ModelViewSet):
    queryset = InstructorApplication.objects.all()
    serializer_class = InstructorApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 사용자가 이미 강사인 경우
        if self.request.user.is_instructor():
            return Response(
                {"detail": "이미 강사 권한을 가지고 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 대기 중인 신청이 있는 경우
        if InstructorApplication.objects.filter(
            user=self.request.user, status=InstructorApplication.Status.PENDING
        ).exists():
            return Response(
                {"detail": "이미 강사 신청이 진행 중입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=self.request.user)

    def get_queryset(self):
        # 관리자는 모든 신청을 볼 수 있고, 일반 사용자는 자신의 신청만 볼 수 있음
        if self.request.user.role == User.Role.MANAGER:
            return InstructorApplication.objects.all()
        return InstructorApplication.objects.filter(user=self.request.user)
