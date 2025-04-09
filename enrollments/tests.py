# enrollments/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import User
from courses.models import Course, Section, Lesson
from .models import Enrollment, LessonProgress, Certificate, CartItem


class EnrollmentAPITestCase(APITestCase):
    """수강 신청 API 테스트"""

    def setUp(self):
        """테스트 데이터 설정"""
        # 강사 계정 생성
        self.instructor = User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

        # 학생 계정 생성
        self.student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="password123",
            role=User.Role.STUDENT,
        )

        # 다른 학생 계정 생성 (권한 테스트용)
        self.other_student = User.objects.create_user(
            email="other@example.com",
            username="other_student",
            password="password123",
            role=User.Role.STUDENT,
        )

        # 강의 생성
        self.course = Course.objects.create(
            instructor=self.instructor,
            title="테스트 강의",
            description="테스트 강의 설명",
            price=10000,
            status="approved",
        )

        # 섹션 생성
        self.section = Section.objects.create(
            course=self.course, title="테스트 섹션", order=1
        )

        # 레슨 생성
        self.lesson = Lesson.objects.create(
            section=self.section,
            title="테스트 레슨",
            video_url="https://www.youtube.com/watch?v=test123",
            order=1,
        )

        # 수강 신청 생성
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status="in_progress", progress=0
        )

        # URL 설정
        self.enrollment_list_url = reverse("enrollments:enrollment-list")
        self.enrollment_detail_url = reverse(
            "enrollments:enrollment-detail", args=[self.enrollment.id]
        )
        self.cart_list_url = reverse("enrollments:cartitem-list")

    def test_get_enrollments_as_student(self):
        """학생으로 수강 신청 목록 조회 테스트"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.enrollment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션이 있을 경우와 없을 경우를 모두 처리
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_create_enrollment(self):
        """수강 신청 생성 테스트"""
        # 다른 강의 생성
        another_course = Course.objects.create(
            instructor=self.instructor,
            title="다른 강의",
            description="다른 강의 설명",
            price=15000,
            status="approved",
        )

        self.client.force_authenticate(user=self.other_student)
        data = {
            "course": another_course.id,
            "status": "in_progress",
        }

        response = self.client.post(self.enrollment_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 새로운 수강 신청이 생성되었는지 확인
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.other_student, course=another_course
            ).exists()
        )

    def test_update_enrollment_status(self):
        """수강 상태 업데이트 테스트"""
        self.client.force_authenticate(user=self.student)
        data = {"status": "completed"}

        response = self.client.patch(self.enrollment_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 상태가 업데이트되었는지 확인
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, "completed")

    def test_other_student_cannot_update_enrollment(self):
        """다른 학생이 수강 정보 수정 시도 (실패 예상)"""
        self.client.force_authenticate(user=self.other_student)
        data = {"status": "dropped"}

        response = self.client.patch(self.enrollment_detail_url, data, format="json")
        # 403 오류(권한 없음) 또는 404 오류(찾을 수 없음) 모두 허용
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

        # 상태가 변경되지 않았는지 확인
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, "in_progress")

    def test_mark_lesson_completed(self):
        """레슨 완료 표시 테스트"""
        self.client.force_authenticate(user=self.student)
        url = reverse("enrollments:lessonprogress-mark-completed")
        data = {"lesson": self.lesson.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 레슨 진행 정보가 생성되고 완료 표시되었는지 확인
        progress = LessonProgress.objects.get(student=self.student, lesson=self.lesson)
        self.assertTrue(progress.completed)

        # 수강 정보의 진행률이 업데이트되었는지 확인
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress, 100.00)  # 레슨이 하나뿐이므로 100%

    def test_add_course_to_cart(self):
        """장바구니에 강의 추가 테스트"""
        # 다른 강의 생성
        another_course = Course.objects.create(
            instructor=self.instructor,
            title="다른 강의",
            description="다른 강의 설명",
            price=15000,
            status="approved",
        )

        self.client.force_authenticate(user=self.other_student)
        data = {"course": another_course.id}

        response = self.client.post(self.cart_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 장바구니에 추가되었는지 확인
        self.assertTrue(
            CartItem.objects.filter(
                user=self.other_student, course=another_course
            ).exists()
        )

    def test_checkout_cart(self):
        """장바구니 결제 테스트"""
        # 다른 강의 생성
        another_course = Course.objects.create(
            instructor=self.instructor,
            title="다른 강의",
            description="다른 강의 설명",
            price=15000,
            status="approved",
        )

        # 장바구니에 담기
        CartItem.objects.create(user=self.other_student, course=another_course)

        self.client.force_authenticate(user=self.other_student)
        url = reverse("enrollments:cartitem-checkout")

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 수강 신청이 생성되었는지 확인
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.other_student, course=another_course
            ).exists()
        )

        # 장바구니가 비워졌는지 확인
        self.assertFalse(CartItem.objects.filter(user=self.other_student).exists())
