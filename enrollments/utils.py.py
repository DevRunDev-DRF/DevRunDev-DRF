from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_payment_cancel_email(user, payment, cancelled_courses):
    """
    결제 취소 완료 후 사용자에게 이메일 알림을 보냅니다.

    Args:
        user: 사용자 객체
        payment: 취소된 결제 객체
        cancelled_courses: 취소된 강의 목록
    """
    subject = f"[DevRunDev] 결제 취소가 완료되었습니다"

    html_message = render_to_string(
        "emails/payment_cancel_email.html",
        {
            "user": user,
            "payment": payment,
            "cancelled_courses": cancelled_courses,
        },
    )

    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_payment_cancel_admin_notification(payment, cancelled_courses, reason=None):
    """
    결제 취소가 발생했을 때 관리자에게 알림을 보냅니다.

    Args:
        payment: 취소된 결제 객체
        cancelled_courses: 취소된 강의 목록
        reason: 취소 사유
    """
    subject = f"[DevRunDev] 결제 취소 알림 (주문번호: {payment.merchant_uid})"

    html_message = render_to_string(
        "emails/payment_cancel_admin_email.html",
        {
            "payment": payment,
            "cancelled_courses": cancelled_courses,
            "reason": reason,
            "user": payment.user,
        },
    )

    plain_message = strip_tags(html_message)

    admin_emails = [admin[1] for admin in settings.ADMINS]
    if admin_emails:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
