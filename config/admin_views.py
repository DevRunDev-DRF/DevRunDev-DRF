from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

from accounts.models import User, InstructorApplication
from courses.models import Course
from enrollments.models import Enrollment, Certificate


@staff_member_required
def admin_dashboard_data(request):
    """관리자 대시보드용 데이터 API"""

    # 대시보드에 표시할 주요 데이터 수집
    data = {
        # 강사 신청 관련
        "pending_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.PENDING
        ).count(),
        "approved_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.APPROVED
        ).count(),
        "rejected_instructor_count": InstructorApplication.objects.filter(
            status=InstructorApplication.Status.REJECTED
        ).count(),
        # 강의 관련
        "review_course_count": Course.objects.filter(status="review").count(),
        "approved_course_count": Course.objects.filter(status="approved").count(),
        "not_approved_course_count": Course.objects.filter(
            status="not_approved"
        ).count(),
        # 사용자 관련
        "student_count": User.objects.filter(role=User.Role.STUDENT).count(),
        "instructor_count": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "manager_count": User.objects.filter(role=User.Role.MANAGER).count(),
        # 수강 관련
        "enrollment_count": Enrollment.objects.count(),
        "certificate_count": Certificate.objects.count(),
        # 기타 요약 정보
        "total_users": User.objects.count(),
        "total_courses": Course.objects.count(),
    }

    return JsonResponse(data)
