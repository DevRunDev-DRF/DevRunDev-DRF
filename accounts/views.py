from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import logout

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

    @swagger_auto_schema(
        operation_summary="회원 가입",
        operation_description="새로운 사용자를 생성합니다.",
        responses={
            201: openapi.Response(
                description="회원 가입 성공",
                examples={
                    "application/json": {
                        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                        "user_id": 1,
                        "email": "user@example.com",
                        "username": "username",
                        "role": "Student",
                    }
                },
            ),
            400: "잘못된 요청",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="사용자 이메일과 비밀번호로 로그인합니다.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                        "user_id": 1,
                        "email": "user@example.com",
                        "username": "username",
                        "role": "Student",
                    }
                },
            ),
            400: "인증 실패",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="로그아웃",
        operation_description="현재 인증된 사용자의 토큰을 삭제하여 로그아웃합니다.",
        responses={
            200: openapi.Response(
                description="로그아웃 성공",
                examples={"application/json": {"message": "로그아웃 되었습니다."}},
            ),
            401: "인증되지 않은 요청",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="사용자 목록 조회",
        operation_description="모든 사용자 목록을 조회합니다.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 상세 조회",
        operation_description="특정 사용자의 상세 정보를 조회합니다.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 생성",
        operation_description="새로운 사용자를 생성합니다.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 정보 수정",
        operation_description="사용자 정보를 수정합니다.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 정보 부분 수정",
        operation_description="사용자 정보의 일부를 수정합니다.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="사용자 삭제", operation_description="사용자를 삭제합니다."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="내 정보 조회",
        operation_description="현재 로그인한 사용자의 정보를 조회합니다.",
        responses={200: UserSerializer, 401: "인증되지 않은 요청"},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    # update_me 액션의 경우 methods가 여러 개이므로 각 메소드별로 swagger_auto_schema 지정
    @swagger_auto_schema(
        method="put",
        operation_summary="내 정보 전체 수정",
        operation_description="현재 로그인한 사용자의 정보를 전체 수정합니다.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "잘못된 요청", 401: "인증되지 않은 요청"},
    )
    @swagger_auto_schema(
        method="patch",
        operation_summary="내 정보 부분 수정",
        operation_description="현재 로그인한 사용자의 정보를 부분 수정합니다.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "잘못된 요청", 401: "인증되지 않은 요청"},
    )
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

    @swagger_auto_schema(
        operation_summary="강사 신청 목록 조회",
        operation_description="강사 신청 목록을 조회합니다. 관리자는 모든 신청을 볼 수 있고, 일반 사용자는 자신의 신청만 볼 수 있습니다.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="강사 신청 상세 조회",
        operation_description="특정 강사 신청의 상세 정보를 조회합니다.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="강사 신청 생성",
        operation_description="새로운 강사 신청을 생성합니다.",
        request_body=InstructorApplicationSerializer,
        responses={
            201: InstructorApplicationSerializer,
            400: "이미 강사 권한을 가지고 있거나 대기 중인 신청이 있는 경우",
            401: "인증되지 않은 요청",
        },
    )
    def create(self, request, *args, **kwargs):
        # 기존 로직은 perform_create에 있으므로, 여기서는 super().create를 호출
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="강사 신청 수정",
        operation_description="강사 신청 정보를 수정합니다.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="강사 신청 부분 수정",
        operation_description="강사 신청 정보의 일부를 수정합니다.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="강사 신청 삭제",
        operation_description="강사 신청을 삭제합니다.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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
