from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from courses.models import Course
from enrollments.models import Enrollment
from .models import Review


class ReviewAPITestCase(APITestCase):
    """리뷰 API 테스트"""

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

        # 수강 신청 생성
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status="in_progress", progress=0
        )

        # 리뷰 생성
        self.review = Review.objects.create(
            course=self.course, user=self.student, rating=4, comment="좋은 강의입니다."
        )

        # URL 설정
        self.review_list_url = reverse("reviews:review-list")
        self.review_detail_url = reverse("reviews:review-detail", args=[self.review.id])

    def test_get_reviews_list(self):
        """리뷰 목록 조회 테스트"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.review_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션이 있을 경우와 없을 경우를 모두 처리
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_create_review(self):
        """리뷰 생성 테스트"""
        # 다른 강의 생성
        another_course = Course.objects.create(
            instructor=self.instructor,
            title="다른 강의",
            description="다른 강의 설명",
            price=15000,
            status="approved",
        )

        # 다른 강의 수강 신청
        Enrollment.objects.create(
            student=self.other_student,
            course=another_course,
            status="in_progress",
            progress=0,
        )

        self.client.force_authenticate(user=self.other_student)
        data = {
            "course": another_course.id,
            "rating": 5,
            "comment": "매우 유익한 강의입니다.",
        }

        response = self.client.post(self.review_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 리뷰가 생성되었는지 확인
        self.assertTrue(
            Review.objects.filter(
                user=self.other_student, course=another_course
            ).exists()
        )

    def test_update_review(self):
        """리뷰 수정 테스트"""
        self.client.force_authenticate(user=self.student)
        data = {"rating": 5, "comment": "매우 좋은 강의로 평가를 수정합니다."}

        response = self.client.patch(self.review_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 리뷰가 수정되었는지 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "매우 좋은 강의로 평가를 수정합니다.")

    def test_delete_review(self):
        """리뷰 삭제 테스트"""
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(self.review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 리뷰가 삭제되었는지 확인
        self.assertEqual(Review.objects.count(), 0)

    def test_other_student_cannot_update_review(self):
        """다른 학생이 리뷰 수정 시도 (실패 예상)"""
        self.client.force_authenticate(user=self.other_student)
        data = {"rating": 1, "comment": "이 리뷰를 수정해봅니다."}

        response = self.client.patch(self.review_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 리뷰가 변경되지 않았는지 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
