from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Course, Section, Lesson

User = get_user_model()


class CourseSerializerTests(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            username="testinstructor", email="test@example.com", password="testpassword"
        )
        # 강사 권한 설정 (accounts 앱 구현에 따라 다를 수 있음)
        # self.user.is_instructor = True
        # self.user.save()

        # 테스트 강의 생성
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            price=10000,
            instructor=self.user,
        )

        # 테스트 섹션 생성
        self.section = Section.objects.create(
            title="Test Section", course=self.course, order=1
        )

        # 테스트 레슨 생성
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            section=self.section,
            video_url="https://example.com/video",
            order=1,
        )

        # 테스트 사용자 로그인
        self.client.force_authenticate(user=self.user)

    def test_course_list_serializer(self):
        """강의 목록 Serializer 테스트"""
        url = "/courses/test/courses/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_course_detail_serializer(self):
        """강의 상세 Serializer 테스트"""
        url = f"/courses/test/courses/{self.course.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Course")
        self.assertEqual(len(response.data["sections"]), 1)
