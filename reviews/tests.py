from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

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
        self.other_enrollment = Enrollment.objects.create(
            student=self.other_student,
            course=self.course,
            status="in_progress",
            progress=0,
        )

        # 리뷰 생성
        self.review = Review.objects.create(
            user=self.student,
            course=self.course,
            rating=5,
            comment="정말 좋은 강의입니다.",
        )

        # URL 설정
        self.api_prefix = "/api/"
        self.review_list_url = reverse("reviews:reviews-list")
        self.review_detail_url = reverse(
            "reviews:reviews-detail", args=[self.review.id]
        )

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
        self.client.force_authenticate(user=self.other_student)

        data = {
            "course": self.course.id,
            "rating": 4,
            "comment": "좋은 강의입니다만 개선할 점도 있어요.",
        }

        response = self.client.post(self.review_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 리뷰가 생성되었는지 확인
        self.assertEqual(Review.objects.count(), 2)
        new_review = Review.objects.get(user=self.other_student)
        self.assertEqual(new_review.rating, 4)
        self.assertEqual(new_review.comment, "좋은 강의입니다만 개선할 점도 있어요.")

    def test_update_review(self):
        """리뷰 수정 테스트"""
        self.client.force_authenticate(user=self.student)

        data = {
            "rating": 4,
            "comment": "수정된 리뷰 내용입니다.",
        }

        response = self.client.patch(self.review_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 리뷰가 수정되었는지 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, "수정된 리뷰 내용입니다.")

    def test_other_student_cannot_update_review(self):
        """다른 학생이 리뷰 수정 시도 (실패 예상)"""
        self.client.force_authenticate(user=self.other_student)

        data = {
            "rating": 3,
            "comment": "다른 학생이 수정한 리뷰 내용",
        }

        response = self.client.patch(self.review_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 리뷰가 수정되지 않았는지 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "정말 좋은 강의입니다.")

    def test_delete_review(self):
        """리뷰 삭제 테스트"""
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self.review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 리뷰가 삭제되었는지 확인
        self.assertEqual(Review.objects.count(), 0)

    def test_other_student_cannot_delete_review(self):
        """다른 학생이 리뷰 삭제 시도 (실패 예상)"""
        self.client.force_authenticate(user=self.other_student)

        response = self.client.delete(self.review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 리뷰가 삭제되지 않았는지 확인
        self.assertEqual(Review.objects.count(), 1)

    def test_course_avg_rating_update(self):
        """리뷰 작성/수정 시 평균 평점 업데이트 테스트"""
        # 초기 평균 평점
        self.course.refresh_from_db()
        initial_avg_rating = self.course.avg_rating
        self.assertEqual(initial_avg_rating, 5.0)  # 하나의 5점 리뷰

        # 다른 학생이 3점 리뷰 작성
        self.client.force_authenticate(user=self.other_student)
        data = {
            "course": self.course.id,
            "rating": 3,
            "comment": "평균적인 강의입니다.",
        }
        self.client.post(self.review_list_url, data, format="json")

        # 평균 평점 업데이트 확인
        self.course.refresh_from_db()
        updated_avg_rating = self.course.avg_rating
        self.assertEqual(updated_avg_rating, 4.0)  # (5+3)/2 = 4.0
