from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import User
from courses.models import Course, Section, Lesson
from enrollments.models import Enrollment
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class QuizAPITestCase(APITestCase):
    """퀴즈 API 테스트"""

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

        # 다른 강사 계정 생성 (권한 테스트용)
        self.other_instructor = User.objects.create_user(
            email="other@example.com",
            username="other_instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
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

        # 학생 수강 신청
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status="in_progress", progress=0
        )

        # 퀴즈 생성
        self.quiz = Quiz.objects.create(
            title="테스트 퀴즈",
            description="테스트 퀴즈 설명",
            course=self.course,
            section=self.section,
            lesson=self.lesson,
            instructor=self.instructor,
        )

        # 문제 생성
        self.question = Question.objects.create(
            quiz=self.quiz, text="테스트 문제", order=1
        )

        # 선택지 생성
        self.choice1 = Choice.objects.create(
            question=self.question, text="정답", is_correct=True
        )

        self.choice2 = Choice.objects.create(
            question=self.question, text="오답1", is_correct=False
        )

        self.choice3 = Choice.objects.create(
            question=self.question, text="오답2", is_correct=False
        )

        # URL 설정
        self.quiz_list_url = reverse("quizzes:quiz-list")
        self.quiz_detail_url = reverse("quizzes:quiz-detail", args=[self.quiz.id])
        self.question_list_url = reverse("quizzes:question-list")
        self.question_detail_url = reverse(
            "quizzes:question-detail", args=[self.question.id]
        )
        self.start_attempt_url = reverse(
            "quizzes:quiz-start-attempt", args=[self.quiz.id]
        )
        self.submit_attempt_url = reverse(
            "quizzes:quiz-submit-attempt", args=[self.quiz.id]
        )
        self.attempt_list_url = reverse("quizzes:quizattempt-list")

    def test_get_quizzes_list_as_instructor(self):
        """강사로 퀴즈 목록 조회 테스트"""
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션이 있을 경우와 없을 경우를 모두 처리
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_get_quizzes_list_as_student(self):
        """학생으로 퀴즈 목록 조회 테스트"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.quiz_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션이 있을 경우와 없을 경우를 모두 처리
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_create_quiz_as_instructor(self):
        """강사로 퀴즈 생성 테스트"""
        self.client.force_authenticate(user=self.instructor)

        data = {
            "title": "새 퀴즈",
            "description": "새 퀴즈 설명",
            "course": self.course.id,
            "section": self.section.id,
            "lesson": self.lesson.id,
        }

        response = self.client.post(self.quiz_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)  # 기존 1개 + 새로 생성 1개

        new_quiz = Quiz.objects.latest("id")
        self.assertEqual(new_quiz.title, "새 퀴즈")
        self.assertEqual(new_quiz.instructor, self.instructor)

    def test_create_quiz_as_student(self):
        """학생으로 퀴즈 생성 테스트 (실패 예상)"""
        self.client.force_authenticate(user=self.student)

        data = {
            "title": "새 퀴즈",
            "description": "새 퀴즈 설명",
            "course": self.course.id,
            "section": self.section.id,
            "lesson": self.lesson.id,
        }

        response = self.client.post(self.quiz_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Quiz.objects.count(), 1)  # 기존 1개만 유지

    def test_update_quiz_as_owner(self):
        """퀴즈 소유자로 퀴즈 수정 테스트"""
        self.client.force_authenticate(user=self.instructor)

        data = {"title": "수정된 퀴즈", "description": "수정된 퀴즈 설명"}

        response = self.client.patch(self.quiz_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 변경 사항 확인
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "수정된 퀴즈")
        self.assertEqual(self.quiz.description, "수정된 퀴즈 설명")

    def test_update_quiz_as_other_instructor(self):
        """다른 강사로 퀴즈 수정 테스트 (실패 예상)"""
        self.client.force_authenticate(user=self.other_instructor)

        data = {"title": "수정된 퀴즈", "description": "수정된 퀴즈 설명"}

        response = self.client.patch(self.quiz_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 변경되지 않았음을 확인
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "테스트 퀴즈")  # 원래 값 유지

    def test_create_question_as_instructor(self):
        """강사로 문제 생성 테스트"""
        self.client.force_authenticate(user=self.instructor)

        data = {
            "quiz": self.quiz.id,
            "text": "새 문제",
            "order": 2,
            "choices": [
                {"text": "정답", "is_correct": True},
                {"text": "오답1", "is_correct": False},
                {"text": "오답2", "is_correct": False},
            ],
        }

        response = self.client.post(self.question_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)  # 기존 1개 + 새로 생성 1개

        # 선택지가 생성되었는지 확인
        new_question = Question.objects.get(text="새 문제")
        self.assertEqual(new_question.choices.count(), 3)

    def test_start_quiz_attempt(self):
        """학생으로 퀴즈 시도 시작 테스트"""
        self.client.force_authenticate(user=self.student)

        response = self.client.post(self.start_attempt_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 퀴즈 시도가 생성되었는지 확인
        self.assertEqual(QuizAttempt.objects.count(), 1)

        attempt = QuizAttempt.objects.first()
        self.assertEqual(attempt.quiz, self.quiz)
        self.assertEqual(attempt.student, self.student)
        self.assertFalse(attempt.is_completed)
        self.assertEqual(attempt.total_questions, 1)  # 문제 1개

    def test_submit_quiz_attempt(self):
        """학생으로 퀴즈 제출 테스트"""
        self.client.force_authenticate(user=self.student)

        # 먼저 퀴즈 시도 시작
        start_response = self.client.post(self.start_attempt_url)
        self.assertEqual(start_response.status_code, status.HTTP_201_CREATED)

        # 시도 ID 확인
        attempt_id = start_response.data["id"]

        # 답변 제출
        data = {
            "answers": [
                {
                    "question": str(self.question.id),
                    "selected_choice": str(self.choice1.id),  # 정답 선택
                }
            ]
        }

        submit_response = self.client.post(self.submit_attempt_url, data, format="json")
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)

        # 퀴즈 시도가 완료되었는지 확인
        attempt = QuizAttempt.objects.get(id=attempt_id)
        self.assertTrue(attempt.is_completed)
        self.assertEqual(attempt.correct_answers, 1)  # 정답 1개
        self.assertEqual(attempt.score, 100)  # 100% 정답

        # 답변이 저장되었는지 확인
        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.first()
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.selected_choice, self.choice1)
        self.assertTrue(answer.is_correct)

    def test_submit_wrong_answer(self):
        """학생으로 오답 제출 테스트"""
        self.client.force_authenticate(user=self.student)

        # 먼저 퀴즈 시도 시작
        self.client.post(self.start_attempt_url)

        # 오답 제출
        data = {
            "answers": [
                {
                    "question": str(self.question.id),
                    "selected_choice": str(self.choice2.id),  # 오답 선택
                }
            ]
        }

        response = self.client.post(self.submit_attempt_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 퀴즈 시도 확인
        attempt = QuizAttempt.objects.first()
        self.assertTrue(attempt.is_completed)
        self.assertEqual(attempt.correct_answers, 0)  # 정답 0개
        self.assertEqual(attempt.score, 0)  # 0% 정답

        # 답변 확인
        answer = Answer.objects.first()
        self.assertEqual(answer.selected_choice, self.choice2)
        self.assertFalse(answer.is_correct)

    def test_attempt_list_as_student(self):
        """학생으로 자신의 퀴즈 시도 목록 조회 테스트"""
        # 퀴즈 시도 생성
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=self.student,
            is_completed=True,
            score=80,
            total_questions=1,
            correct_answers=1,
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.attempt_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션이 있을 경우와 없을 경우를 모두 처리
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
            self.assertEqual(response.data["results"][0]["id"], attempt.id)
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["id"], attempt.id)

    def test_other_student_attempt_access(self):
        """다른 학생의 퀴즈 시도에 접근 테스트"""
        # 다른 학생 계정 생성
        other_student = User.objects.create_user(
            email="other_student@example.com",
            username="other_student",
            password="password123",
            role=User.Role.STUDENT,
        )

        # 다른 학생의 수강 등록
        Enrollment.objects.create(
            student=other_student, course=self.course, status="in_progress", progress=0
        )

        # 다른 학생의 퀴즈 시도 생성
        other_attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            student=other_student,
            is_completed=True,
            score=80,
            total_questions=1,
            correct_answers=1,
        )

        # 첫 번째 학생으로 로그인
        self.client.force_authenticate(user=self.student)

        # 다른 학생의 시도 상세 조회 시도
        attempt_detail_url = reverse(
            "quizzes:quizattempt-detail", args=[other_attempt.id]
        )
        response = self.client.get(attempt_detail_url)

        # 다른 학생의 시도는 볼 수 없어야 함 (404 또는 403 둘 다 가능)
        self.assertIn(
            response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
        )
