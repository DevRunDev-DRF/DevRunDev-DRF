from rest_framework import viewsets, permissions, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import logout, login as django_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string

from enrollments.models import Enrollment

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
        # HTML 요청인 경우
        if request.accepted_renderer.format == "html":
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

                # 토큰 생성
                Token.objects.get_or_create(user=user)

                # Django 로그인
                django_login(request, user)

                messages.success(request, "회원가입이 완료되었습니다.")
                return redirect("home")
            except Exception as e:
                # 에러 메시지를 템플릿에 전달
                return render(
                    request, "accounts/register.html", {"errors": serializer.errors}
                )

        # API 요청인 경우 (기존 로직 유지)
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

    def get(self, request):
        """회원가입 폼 렌더링"""
        return render(request, "accounts/register.html")


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
        # content type을 확인하는 더 명확한 방법
        is_html_request = (
            request.accepted_renderer.format == "html"
            or request.content_type == "application/x-www-form-urlencoded"
        )

        # HTML 요청인 경우
        if is_html_request:
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data["user"]

                # Django 로그인
                django_login(request, user)

                # 토큰 생성 (선택적)
                Token.objects.get_or_create(user=user)

                messages.success(request, "로그인되었습니다.")
                return redirect("home")
            except Exception as e:
                # 에러 메시지를 템플릿에 전달
                return render(
                    request, "accounts/login.html", {"errors": serializer.errors}
                )

        # API 요청인 경우 (기존 로직 유지)
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

    def get(self, request):
        """로그인 폼 렌더링"""
        return render(request, "accounts/login.html")


@login_required
def profile_view(request):
    """사용자 프로필 뷰"""
    # 강사 신청 상태 확인
    instructor_application = None
    try:
        instructor_application = InstructorApplication.objects.filter(
            user=request.user
        ).latest("created_at")
    except InstructorApplication.DoesNotExist:
        pass

    # 수강 중인 강의 가져오기
    enrollments = Enrollment.objects.filter(
        student=request.user, status__in=["in_progress", "completed"]
    )

    context = {
        "instructor_application": instructor_application,
        "enrollments": enrollments,
    }
    return render(request, "accounts/profile.html", context)


def instructor_application_form(request):
    """강사 신청 양식 렌더링"""
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return render(request, "accounts/instructor_application_form.html")
    else:
        return render(request, "accounts/instructor_application_form_page.html")


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
        # 토큰 삭제 (토큰이 있는 경우에만)
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()

        # 세션 기반 로그아웃
        logout(request)

        # API 요청인 경우 JSON 응답 반환
        if request.accepted_renderer.format == "json":
            return Response(
                {"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK
            )

        # 웹 페이지 요청인 경우 홈페이지로 리다이렉트
        messages.success(request, "로그아웃 되었습니다.")
        return redirect("home")

    # GET 메서드 추가 (웹 브라우저에서 링크 클릭으로 로그아웃할 수 있도록)
    def get(self, request):
        # 토큰 삭제 (토큰이 있는 경우에만)
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()

        # 세션 기반 로그아웃
        logout(request)

        # 성공 메시지 추가하고 홈페이지로 리다이렉트
        messages.success(request, "로그아웃 되었습니다.")
        return redirect("home")


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
        user = request.user

        # 비밀번호만 변경하는 경우 (프로필 페이지의 비밀번호 변경 폼)
        if "password" in request.data and len(request.data) == 1:
            password = request.data.get("password")
            if password:
                user.set_password(password)
                user.save()

                # 사용자 로그아웃 처리
                logout(request)

                # HTML 응답인 경우 - 모달 팝업으로 알림 후 로그인 페이지로 리다이렉트
                if request.accepted_renderer.format == "html":
                    response_html = """
                    <div id="password-change-result">
                        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50" id="password-change-modal">
                            <div class="bg-white rounded-lg p-6 max-w-sm mx-auto">
                                <div class="flex items-center text-green-600 mb-4">
                                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                    <h3 class="text-lg font-bold">비밀번호 변경 완료</h3>
                                </div>
                                <p class="mb-6">비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 다시 로그인해주세요.</p>
                                <div class="text-right">
                                    <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" 
                                            onclick="window.location.href='/accounts/login/'">
                                        로그인 페이지로 이동
                                    </button>
                                </div>
                            </div>
                        </div>
                        <script>
                            // 3초 후 자동으로 로그인 페이지로 리다이렉트
                            setTimeout(function() {
                                window.location.href = "/accounts/login/";
                            }, 3000);
                            
                            // ESC 키 또는 모달 외부 클릭 시 바로 로그인 페이지로 이동
                            document.addEventListener('keydown', function(e) {
                                if (e.key === 'Escape') {
                                    window.location.href = "/accounts/login/";
                                }
                            });
                            
                            document.getElementById('password-change-modal').addEventListener('click', function(e) {
                                if (e.target === this) {
                                    window.location.href = "/accounts/login/";
                                }
                            });
                        </script>
                    </div>
                    """
                    return HttpResponse(response_html)

                # API 응답인 경우
                return Response(
                    {
                        "message": "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 다시 로그인해주세요.",
                        "redirect_to": "/accounts/login/",
                    }
                )

        # 일반 프로필 정보 업데이트
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 비밀번호가 포함된 경우 (일반 프로필 업데이트)
        if "password" in request.data and request.data["password"]:
            password = request.data.pop("password")
            user = serializer.save()
            user.set_password(password)
            user.save()

            # 비밀번호 변경 시 로그아웃 처리
            logout(request)

            # API 응답 시
            if request.accepted_renderer.format != "html":
                return Response(
                    {
                        "message": "정보가 업데이트되고 비밀번호가 변경되었습니다. 새 비밀번호로 다시 로그인해주세요.",
                        "redirect_to": "/accounts/login/",
                    }
                )

            # HTML 응답 시 - 메시지 추가하고 로그인 페이지로 리다이렉트
            messages.success(
                request,
                "정보가 업데이트되고 비밀번호가 변경되었습니다. 새 비밀번호로 다시 로그인해주세요.",
            )
            return redirect("accounts:login")
        else:
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
        # HTML 요청인 경우 다르게 처리
        if request.accepted_renderer.format == "html":
            queryset = self.filter_queryset(self.get_queryset())
            return render(
                request,
                "accounts/instructor_applications_list.html",
                {"applications": queryset},
            )
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
        # HTMX 요청 확인 (HTMX는 특별한 헤더를 보냄)
        is_htmx = request.headers.get("HX-Request") == "true"

        # API 요청이 아닌 경우 - HTMX 또는 HTML 폼 제출
        if (
            is_htmx
            or request.content_type.startswith("multipart/form-data")
            or request.content_type.startswith("application/x-www-form-urlencoded")
        ):
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                # 성공 메시지를 담은 HTML 응답 반환
                return HttpResponse(
                    render_to_string("accounts/instructor_application_success.html"),
                    content_type="text/html",
                )
            except serializers.ValidationError as e:
                # 오류 메시지 추출
                if hasattr(e, "detail"):
                    if isinstance(e.detail, dict) and "detail" in e.detail:
                        error_message = str(e.detail["detail"])
                    else:
                        error_message = str(e.detail)
                else:
                    error_message = "신청 처리 중 오류가 발생했습니다."

                # 오류 메시지를 담은 HTML 응답 반환
                return HttpResponse(
                    render_to_string(
                        "accounts/instructor_application_error.html",
                        {"error_message": error_message},
                    ),
                    content_type="text/html",
                )

        # 일반 API 요청 처리
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
            raise serializers.ValidationError(
                {"detail": "이미 강사 권한을 가지고 있습니다."}
            )

        # 대기 중인 신청이 있는 경우
        if InstructorApplication.objects.filter(
            user=self.request.user, status=InstructorApplication.Status.PENDING
        ).exists():
            raise serializers.ValidationError(
                {"detail": "이미 강사 신청이 진행 중입니다."}
            )

        serializer.save(user=self.request.user)

    def get_queryset(self):
        # 관리자는 모든 신청을 볼 수 있고, 일반 사용자는 자신의 신청만 볼 수 있음
        if self.request.user.role == User.Role.MANAGER:
            return InstructorApplication.objects.all()
        return InstructorApplication.objects.filter(user=self.request.user)
