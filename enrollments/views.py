# enrollments/views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Enrollment, LessonProgress, Certificate, CartItem, Payment
from .serializers import (
    EnrollmentSerializer,
    EnrollmentDetailSerializer,
    LessonProgressSerializer,
    CertificateSerializer,
    CartItemSerializer,
)
from .permissions import IsEnrollmentOwner, IsCartItemOwner
from accounts.permissions import IsInstructor
from courses.models import Course, Lesson

from iamport import Iamport
from django.conf import settings
import uuid
from django.db import transaction


class EnrollmentViewSet(viewsets.ModelViewSet):
    """수강 신청 관련 API 뷰셋"""

    queryset = Enrollment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "student", "status"]
    ordering_fields = ["enrolled_at", "progress"]
    ordering = ["-enrolled_at"]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return EnrollmentDetailSerializer
        return EnrollmentSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [IsAuthenticated(), IsEnrollmentOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.all()

        if user.is_instructor():
            return queryset.filter(course__instructor=user)

        if not user.is_staff:
            if self.action in ["list", "create"]:
                return queryset.filter(student=user)
            return queryset

        return queryset

    def create(self, request, *args, **kwargs):
        if request.data.get("student") is None:
            request.data.update({"student": request.user.id})
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"])
    def reset_progress(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.student != request.user:
            return Response(
                {"detail": "자신의 수강 신청만 초기화할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        enrollment.reset_progress()
        return Response({"detail": "수강 진행률이 초기화되었습니다."})

    @action(detail=True, methods=["post"])
    def generate_certificate(self, request, pk=None):
        enrollment = self.get_object()

        if enrollment.student != request.user:
            return Response(
                {
                    "detail": "자신의 수강 신청에 대해서만 수료증을 발급받을 수 있습니다."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not enrollment.is_course_completed():
            return Response(
                {
                    "detail": "모든 강의와 퀴즈를 완료해야 수료증을 발급받을 수 있습니다."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        certificate = enrollment.generate_certificate()
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """강의 진행 상황 관련 API 뷰셋"""

    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "lesson", "completed"]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsEnrollmentOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = LessonProgress.objects.all()

        if user.is_instructor():
            return queryset.filter(lesson__section__course__instructor=user)

        if not user.is_staff:
            return queryset.filter(student=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_completed(self, request):
        lesson_id = request.data.get("lesson")
        if not lesson_id:
            return Response(
                {"detail": "lesson 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)

        enrollment_exists = Enrollment.objects.filter(
            student=request.user,
            course=lesson.section.course,
            status__in=["in_progress", "completed"],
        ).exists()

        if not enrollment_exists:
            return Response(
                {"detail": "이 강의에 등록되어 있지 않습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson
        )

        progress.mark_completed()

        # 마지막 시청 레슨 업데이트
        enrollment = Enrollment.objects.get(
            student=request.user, course=lesson.section.course
        )
        enrollment.last_watched_lesson = lesson
        enrollment.save()

        # 모든 레슨 완료 후 수료증 자동 발급
        if enrollment.is_course_completed() and not hasattr(enrollment, "certificate"):
            certificate = enrollment.generate_certificate()
            if certificate:
                return Response(
                    {
                        "detail": "레슨이 완료 처리되었으며, 모든 과정을 완료하여 수료증이 발급되었습니다.",
                        "certificate_id": certificate.certificate_id,
                    }
                )

        return Response({"detail": "레슨이 완료 처리되었습니다."})

    @action(detail=False, methods=["post"])
    def update_last_watched(self, request):
        lesson_id = request.data.get("lesson")
        if not lesson_id:
            return Response(
                {"detail": "lesson 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson
        )

        progress.update_last_watched()

        enrollment = Enrollment.objects.get(
            student=request.user, course=lesson.section.course
        )
        enrollment.last_watched_lesson = lesson
        enrollment.save()

        return Response({"detail": "마지막 시청 시간이 업데이트되었습니다."})


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """수료증 관련 API 뷰셋 (읽기 전용)"""

    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Certificate.objects.all()

        if user.is_instructor():
            return queryset.filter(enrollment__course__instructor=user)

        if not user.is_staff:
            return queryset.filter(enrollment__student=user)

        return queryset


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCartItemOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # 요청 헤더 확인
        is_html_request = (
            getattr(request, "accepted_renderer", None)
            and getattr(request.accepted_renderer, "format", None) == "html"
        ) or request.content_type == "application/x-www-form-urlencoded"

        course_id = request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            if is_html_request:
                return redirect("enrollments:cart-view")
            return Response(
                {"detail": "이미 수강 중인 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if CartItem.objects.filter(user=request.user, course=course).exists():
            if is_html_request:
                return redirect("enrollments:cart-view")
            return Response(
                {"detail": "이미 장바구니에 추가된 강의입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 장바구니에 추가
        data = {"course": course_id, "user": request.user.id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # HTML 요청인 경우 장바구니 페이지로 리다이렉트
        if is_html_request:
            return redirect("enrollments:cart-view")

        # API 요청인 경우 장바구니 개수 반환
        cart_count = CartItem.objects.filter(user=request.user).count()
        return Response(str(cart_count), status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        # HTML 요청인지 확인 (Content-Type 또는 HTMX 헤더 확인)
        is_html_request = (
            request.accepted_renderer.format == "html"
            or request.content_type == "application/x-www-form-urlencoded"
            or "HX-Request" in request.headers
        )

        # HTML 요청인 경우 장바구니 페이지로 리다이렉트
        if is_html_request and "HX-Request" not in request.headers:
            messages.success(request, "항목이 장바구니에서 삭제되었습니다.")
            return redirect("enrollments:cart-view")

        # HTMX 요청인 경우 장바구니 아이템 카운트 갱신
        if "HX-Request" in request.headers:
            cart_count = CartItem.objects.filter(user=request.user).count()
            headers = {
                "HX-Trigger-After-Swap": '{"updateCartCount": "'
                + str(cart_count)
                + '"}'
            }
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        # API 요청인 경우 기존 동작 유지
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        # _method 파라미터가 있는지 확인
        if (
            self.request.method == "POST"
            and self.request.POST.get("_method") == "DELETE"
        ):
            self.request.method = "DELETE"

        return super().get_object()

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"detail": "장바구니가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollments = []
        total_price = 0
        # 트랜잭션으로 처리하여 오류 발생 시 롤백
        with transaction.atomic():
            for item in cart_items:
                # 이미 수강 중인지 확인
                if not Enrollment.objects.filter(
                    student=request.user, course=item.course
                ).exists():
                    # 수강료 계산
                    total_price += item.course.price

                    # 수강 신청 생성
                    enrollment = Enrollment.objects.create(
                        student=request.user,
                        course=item.course,
                        status="in_progress",
                        progress=0,
                    )
                    enrollments.append(enrollment)

                    # 강의 첫 레슨 자동으로 가져와서 설정
                    first_lesson = (
                        Lesson.objects.filter(section__course=item.course)
                        .order_by("section__order", "order")
                        .first()
                    )

                    if first_lesson:
                        enrollment.last_watched_lesson = first_lesson
                        enrollment.save()

            # 장바구니 비우기
            cart_items.delete()

        # HTMX 요청일 경우 템플릿 응답
        if "HX-Request" in request.headers:
            return render(
                request,
                "enrollments/checkout_success.html",
                {"enrollments": enrollments, "total_price": total_price},
            )

        return Response(
            {
                "detail": f"{len(enrollments)}개 강의의 수강신청이 완료되었습니다.",
                "enrollments": EnrollmentSerializer(enrollments, many=True).data,
                "total_price": total_price,
            }
        )


def get_iamport_client():
    return Iamport(
        imp_key=settings.IAMPORT_API_KEY, imp_secret=settings.IAMPORT_API_SECRET
    )


class PaymentPrepareView(APIView):
    """결제 준비 API 뷰"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 사용자의 장바구니 아이템 가져오기
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"detail": "장바구니가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 총 결제 금액 계산
        total_amount = sum(item.course.price for item in cart_items)

        # 무료 강의만 있는 경우
        if total_amount == 0:
            # 무료 강의는 바로 수강 신청 처리
            with transaction.atomic():
                for item in cart_items:
                    # 이미 수강 중인지 확인
                    if not Enrollment.objects.filter(
                        student=request.user, course=item.course
                    ).exists():
                        Enrollment.objects.create(
                            student=request.user,
                            course=item.course,
                            status="in_progress",
                            progress=0,
                        )

                # 장바구니 비우기
                cart_items.delete()

            return Response(
                {
                    "success": True,
                    "message": "무료 강의 수강 신청이 완료되었습니다.",
                    "free_course": True,
                }
            )

        # 결제가 필요한 경우
        # 고유한 merchant_uid 생성
        merchant_uid = f"ORDER_{uuid.uuid4().hex[:12].upper()}"

        # 결제 정보 생성
        payment = Payment.objects.create(
            user=request.user,
            merchant_uid=merchant_uid,
            amount=total_amount,
            status="ready",
        )

        # 장바구니 아이템 연결
        payment.cart_items.set(cart_items)

        # 클라이언트에 결제 정보 반환
        return Response(
            {
                "success": True,
                "merchant_uid": merchant_uid,
                "amount": total_amount,
                "name": f"{request.user.username}의 강의 결제",
                "buyer_name": request.user.username,
                "buyer_email": request.user.email,
                "free_course": False,
            }
        )


class PaymentVerifyView(APIView):
    """결제 검증 API 뷰"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")

        if not imp_uid or not merchant_uid:
            return Response(
                {"detail": "imp_uid와 merchant_uid가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 결제 정보 조회
            payment = Payment.objects.get(merchant_uid=merchant_uid, user=request.user)

            print(f"Payment found: {payment.merchant_uid}, amount: {payment.amount}")
            print(
                f"API Keys set: {bool(settings.PORTONE_API_KEY)}, {bool(settings.PORTONE_API_SECRET)}"
            )

            # 아임포트 API 키가 설정되어 있는지 확인
            if (
                not settings.PORTONE_API_KEY
                or not settings.PORTONE_API_SECRET
                or settings.SKIP_PAYMENT_VERIFICATION
            ):
                # API 키가 설정되어 있지 않은 경우 (개발 환경 등), 결제 검증 없이 진행
                with transaction.atomic():
                    payment.imp_uid = imp_uid
                    payment.status = "paid"
                    payment.save()

                    print("Dev mode: Payment marked as paid without verification")

                    # 장바구니 아이템으로 수강 신청 처리
                    cart_items = payment.cart_items.all()
                    for item in cart_items:
                        # 이미 수강 중인지 확인
                        if not Enrollment.objects.filter(
                            student=request.user, course=item.course
                        ).exists():
                            Enrollment.objects.create(
                                student=request.user,
                                course=item.course,
                                status="in_progress",
                                progress=0,
                            )

                    # 장바구니 비우기
                    CartItem.objects.filter(
                        id__in=cart_items.values_list("id", flat=True)
                    ).delete()

                return Response(
                    {"success": True, "message": "결제 및 수강 신청이 완료되었습니다."}
                )
            else:
                # 아임포트 결제 정보 검증
                iamport = Iamport(
                    imp_key=settings.PORTONE_API_KEY,
                    imp_secret=settings.PORTONE_API_SECRET,
                )
                payment_info = iamport.find(imp_uid=imp_uid)

                # 결제금액 검증
                if payment_info["amount"] == payment.amount:
                    # 데이터베이스에 결제 정보 업데이트
                    with transaction.atomic():
                        payment.imp_uid = imp_uid
                        payment.status = "paid"
                        payment.save()

                        # 장바구니 아이템으로 수강 신청 처리
                        cart_items = payment.cart_items.all()
                        for item in cart_items:
                            # 이미 수강 중인지 확인
                            if not Enrollment.objects.filter(
                                student=request.user, course=item.course
                            ).exists():
                                Enrollment.objects.create(
                                    student=request.user,
                                    course=item.course,
                                    status="in_progress",
                                    progress=0,
                                )

                        # 장바구니 비우기
                        CartItem.objects.filter(
                            id__in=cart_items.values_list("id", flat=True)
                        ).delete()

                    return Response(
                        {
                            "success": True,
                            "message": "결제 및 수강 신청이 완료되었습니다.",
                        }
                    )
                else:
                    # 결제금액 불일치
                    return Response(
                        {"success": False, "message": "결제금액이 일치하지 않습니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Payment.DoesNotExist:
            return Response(
                {"detail": "결제 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCancelView(APIView):
    """결제 취소 API 뷰"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get("payment_id")
        reason = request.data.get("reason", "사용자 요청")

        try:
            payment = Payment.objects.get(
                id=payment_id, user=request.user, status="paid"
            )

            # 아임포트에 취소 요청
            iamport = get_iamport_client()
            cancel_result = iamport.cancel(
                imp_uid=payment.imp_uid,
                merchant_uid=payment.merchant_uid,
                amount=payment.amount,
                reason=reason,
            )

            # 취소 성공 시 DB 업데이트
            if cancel_result["status"] == "cancelled":
                payment.status = "cancelled"
                payment.save()

                # 연관된 수강신청 삭제
                courses = payment.cart_items.values_list("course", flat=True)
                Enrollment.objects.filter(
                    student=request.user,
                    course__in=courses,
                    created_at__gte=payment.created_at,
                ).delete()

                return Response({"success": True, "message": "결제가 취소되었습니다."})
            else:
                return Response(
                    {"success": False, "message": "결제 취소에 실패했습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Payment.DoesNotExist:
            return Response(
                {"detail": "결제 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@login_required
def delete_cart_item(request, item_id):
    """장바구니 항목 삭제 뷰"""
    # 현재 사용자의 장바구니 항목만 삭제 가능
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "장바구니에서 항목이 삭제되었습니다.")
    return redirect("enrollments:cart-view")


@login_required
def cart_view(request):
    """장바구니 페이지 뷰"""
    cart_items = CartItem.objects.filter(user=request.user).select_related(
        "course", "course__instructor"
    )

    # 장바구니 총액 계산
    total_price = sum(item.course.price for item in cart_items)

    # 디버깅용 로그 추가
    print(f"PORTONE_SHOP_ID: {settings.PORTONE_SHOP_ID}")
    print(f"PORTONE_PG_PROVIDER: {settings.PORTONE_PG_PROVIDER}")

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_count": cart_items.count(),
        "portone_store_id": settings.PORTONE_SHOP_ID,
        "portone_pg_provider": settings.PORTONE_PG_PROVIDER,
        "debug": settings.DEBUG,
    }
    return render(request, "enrollments/cart.html", context)


@login_required
def my_courses_view(request):
    """내 강의 페이지 뷰"""
    from enrollments.models import Enrollment

    enrollments = Enrollment.objects.filter(
        student=request.user, status__in=["in_progress", "completed"]
    ).select_related("course")

    context = {
        "enrollments": enrollments,
        "cart_count": request.user.cart_items.count(),
    }
    return render(request, "enrollments/my_courses.html", context)


@login_required
def certificate_view(request, certificate_id=None):
    """수료증 조회 페이지"""
    if certificate_id:
        # 특정 수료증 조회
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        # 수료증 소유자 또는 관리자만 접근 가능
        if certificate.enrollment.student != request.user and not request.user.is_staff:
            messages.error(request, "해당 수료증에 접근할 권한이 없습니다.")
            return redirect("enrollments:my_certificates")

        context = {
            "certificate": certificate,
            "enrollment": certificate.enrollment,
            "course": certificate.enrollment.course,
        }
        return render(request, "enrollments/certificate_detail.html", context)
    else:
        # 사용자의 모든 수료증 목록 조회
        certificates = Certificate.objects.filter(
            enrollment__student=request.user
        ).select_related("enrollment__course")

        context = {
            "certificates": certificates,
            "cart_count": CartItem.objects.filter(user=request.user).count(),
        }
        return render(request, "enrollments/my_certificates.html", context)


@login_required
def print_certificate_view(request, certificate_id):
    """인쇄용 수료증 페이지"""
    # 특정 수료증 조회
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

    # 수료증 소유자 또는 관리자만 접근 가능
    if certificate.enrollment.student != request.user and not request.user.is_staff:
        messages.error(request, "해당 수료증에 접근할 권한이 없습니다.")
        return redirect("enrollments:my_certificates")

    context = {
        "certificate": certificate,
        "enrollment": certificate.enrollment,
        "course": certificate.enrollment.course,
    }
    return render(request, "enrollments/certificate_print.html", context)


@login_required
def checkout_free_course(request):
    """무료 강의 체크아웃 뷰"""
    if request.method != "POST":
        return redirect("enrollments:cart-view")

    # 사용자의 장바구니 아이템 가져오기
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "장바구니가 비어있습니다.")
        return redirect("enrollments:cart-view")

    # 총 결제 금액 계산
    total_amount = sum(item.course.price for item in cart_items)

    # 무료 강의만 있는지 확인
    if total_amount > 0:
        messages.error(request, "무료 강의만 이 기능을 사용할 수 있습니다.")
        return redirect("enrollments:cart-view")

    # 무료 강의 수강 신청 처리
    enrollments_created = []

    with transaction.atomic():
        for item in cart_items:
            # 이미 수강 중인지 확인
            if not Enrollment.objects.filter(
                student=request.user, course=item.course
            ).exists():
                enrollment = Enrollment.objects.create(
                    student=request.user,
                    course=item.course,
                    status="in_progress",
                    progress=0,
                )
                enrollments_created.append(enrollment)

        # 장바구니 비우기
        cart_items.delete()

    if enrollments_created:
        messages.success(
            request, f"{len(enrollments_created)}개 강의의 수강 신청이 완료되었습니다."
        )
    else:
        messages.info(request, "이미 수강 중인 강의입니다.")

    return redirect("enrollments:my_courses")
