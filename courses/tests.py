import tempfile
from PIL import Image
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.models import User
from courses.models import Course, Section, Lesson


class CourseAPITestCase(APITestCase):
    """Course API 테스트"""

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

        # 임시 이미지 생성
        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file, "jpeg")
        tmp_file.seek(0)

        # 강의 생성
        self.course = Course.objects.create(
            instructor=self.instructor,
            title="테스트 강의",
            description="테스트 강의 설명",
            price=10000,
            status="approved",
            thumbnail=tmp_file.name,
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

        # API 클라이언트
        self.client = APIClient()

        # API URL
        self.api_prefix = "/api/"
        self.course_list_url = f"{self.api_prefix}courses/"
        self.course_detail_url = f"{self.api_prefix}courses/{self.course.id}/"

    def test_get_courses_list_unauthenticated(self):
        """인증되지 않은 사용자의 강의 목록 조회 테스트"""
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # 승인된 강의만 볼 수 있음

    def test_get_courses_list_as_student(self):
        """학생으로 강의 목록 조회 테스트"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # 승인된 강의만 볼 수 있음

    def test_get_courses_list_as_instructor(self):
        """강사로 강의 목록 조회 테스트"""
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 모든 강의가 조회되는지 확인
        response = self.client.get(
            f"{self.course_list_url}?instructor={self.instructor.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_course_as_instructor(self):
        """강사로 강의 생성 테스트"""
        self.client.force_authenticate(user=self.instructor)

        data = {
            "title": "새 강의",
            "description": "새 강의 설명",
            "price": 20000,
        }

        response = self.client.post(self.course_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(
            Course.objects.latest("id").status, "review"
        )  # 신규 강의는 review 상태

    def test_create_course_as_student(self):
        """학생으로 강의 생성 테스트 (실패해야 함)"""
        self.client.force_authenticate(user=self.student)

        data = {
            "title": "새 강의",
            "description": "새 강의 설명",
            "price": 20000,
        }

        response = self.client.post(self.course_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 권한 없음

    def test_course_detail(self):
        """강의 상세 조회 테스트"""
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.course.title)
        self.assertEqual(len(response.data["sections"]), 1)

    def test_update_course_as_owner(self):
        """강의 소유자로 강의 수정 테스트"""
        self.client.force_authenticate(user=self.instructor)

        data = {
            "title": "수정된 강의 제목",
            "description": "수정된 강의 설명",
            "price": 15000,
        }

        response = self.client.patch(self.course_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "수정된 강의 제목")

    def test_update_course_as_non_owner(self):
        """다른 강사로 강의 수정 테스트 (실패해야 함)"""
        other_instructor = User.objects.create_user(
            email="other@example.com",
            username="other_instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

        self.client.force_authenticate(user=other_instructor)

        data = {
            "title": "수정된 강의 제목",
        }

        response = self.client.patch(self.course_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # 권한 없음
