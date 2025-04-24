import random
import re
import os
from datetime import timedelta
from io import BytesIO
import urllib.request

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings

from accounts.models import User
from courses.models import Course, Lesson, Section
from quizzes.models import Answer, Choice, Question, Quiz, QuizAttempt

# 실제 온라인 강의와 유사한 데이터
COURSE_DATA = [
    # 프로그래밍 기초
    {
        "title": "파이썬 프로그래밍 기초",
        "description": "파이썬 언어를 처음부터 배워 프로그래밍의 기초 개념을 익히는 강의입니다. 변수, 데이터 타입, 조건문, 반복문 등 기본 개념부터 함수와 클래스까지 다룹니다.",
        "price": 49900,
        "color": (65, 105, 225),  # 로얄 블루
        "sections": [
            {
                "title": "파이썬 소개 및 환경설정",
                "lessons": [
                    {
                        "title": "프로그래밍 언어란?",
                        "video_url": "https://www.youtube.com/watch?v=Y8Tko2YC5hA",
                    },
                    {
                        "title": "파이썬 설치 및 IDE 설정",
                        "video_url": "https://www.youtube.com/watch?v=K02AEykQ7og",
                    },
                    {
                        "title": "첫 번째 파이썬 프로그램",
                        "video_url": "https://www.youtube.com/watch?v=DaGJ3ZuYN7c",
                    },
                ],
            },
            {
                "title": "변수와 데이터 타입",
                "lessons": [
                    {
                        "title": "변수란?",
                        "video_url": "https://www.youtube.com/watch?v=Z1Yd7upQsXY",
                    },
                    {
                        "title": "숫자형 데이터",
                        "video_url": "https://www.youtube.com/watch?v=khKv-8q7YmY",
                    },
                    {
                        "title": "문자열 데이터",
                        "video_url": "https://www.youtube.com/watch?v=k9TUPpGqYTo",
                    },
                ],
            },
            {
                "title": "조건문과 반복문",
                "lessons": [
                    {
                        "title": "if문 기초",
                        "video_url": "https://www.youtube.com/watch?v=c2mGK7qO0Vk",
                    },
                    {
                        "title": "for 반복문",
                        "video_url": "https://www.youtube.com/watch?v=P-HMdIFNCmw",
                    },
                    {
                        "title": "while 반복문",
                        "video_url": "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ",
                    },
                ],
            },
        ],
        "quiz_data": [
            {
                "title": "변수와 데이터 타입 퀴즈",
                "description": "파이썬의 변수와 데이터 타입에 대한 이해도를 평가합니다.",
                "section_index": 1,  # 2번째 섹션
                "lesson_index": 1,  # 2번째 레슨
                "questions": [
                    {
                        "text": "파이썬에서 변수를 선언할 때 사용하는 키워드는?",
                        "choices": [
                            {"text": "var", "is_correct": False},
                            {"text": "let", "is_correct": False},
                            {"text": "const", "is_correct": False},
                            {
                                "text": "별도의 키워드 없이 직접 할당",
                                "is_correct": True,
                            },
                        ],
                    },
                    {
                        "text": "파이썬에서 문자열을 선언하는 방법으로 올바른 것은?",
                        "choices": [
                            {"text": 'str = "Hello World"', "is_correct": True},
                            {"text": "str = (Hello World)", "is_correct": False},
                            {"text": 'string str = "Hello World"', "is_correct": False},
                            {"text": "str = 'Hello World';", "is_correct": False},
                        ],
                    },
                ],
            },
            {
                "title": "반복문 퀴즈",
                "description": "파이썬의 반복문에 대한 이해도를 평가합니다.",
                "section_index": 2,  # 3번째 섹션
                "lesson_index": 2,  # 3번째 레슨
                "questions": [
                    {
                        "text": "다음 중 파이썬의 조건문 문법으로 올바른 것은?",
                        "choices": [
                            {
                                "text": 'if (x > 5) { print("x는 5보다 크다") }',
                                "is_correct": False,
                            },
                            {
                                "text": 'if x > 5: print("x는 5보다 크다")',
                                "is_correct": True,
                            },
                            {
                                "text": 'if x > 5 then print("x는 5보다 크다")',
                                "is_correct": False,
                            },
                            {
                                "text": 'if x > 5: { print("x는 5보다 크다") }',
                                "is_correct": False,
                            },
                        ],
                    },
                    {
                        "text": "파이썬의 while 반복문에 대한 설명으로 올바른 것은?",
                        "choices": [
                            {
                                "text": "조건이 참인 동안 계속 반복한다",
                                "is_correct": True,
                            },
                            {"text": "정해진 횟수만큼 반복한다", "is_correct": False},
                            {"text": "항상 최소 한 번은 실행된다", "is_correct": False},
                            {
                                "text": "반복 횟수를 미리 정할 수 있다",
                                "is_correct": False,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    # 웹 개발
    {
        "title": "HTML과 CSS로 시작하는 웹개발",
        "description": "웹 개발의 기초가 되는 HTML과 CSS를 배우는 강의입니다. 웹 페이지 구조 설계부터 스타일링까지 실습을 통해 학습합니다.",
        "price": 39900,
        "color": (255, 69, 0),  # 오렌지
        "sections": [
            {
                "title": "HTML 기초",
                "lessons": [
                    {
                        "title": "HTML이란?",
                        "video_url": "https://www.youtube.com/watch?v=qz0aGYrrlhU",
                    },
                    {
                        "title": "기본 태그 사용법",
                        "video_url": "https://www.youtube.com/watch?v=UB1O30fR-EE",
                    },
                    {
                        "title": "폼과 입력 요소",
                        "video_url": "https://www.youtube.com/watch?v=dD2EISBDjWM",
                    },
                ],
            },
            {
                "title": "CSS 기초",
                "lessons": [
                    {
                        "title": "CSS 소개",
                        "video_url": "https://www.youtube.com/watch?v=1PnVor36_40",
                    },
                    {
                        "title": "선택자와 속성",
                        "video_url": "https://www.youtube.com/watch?v=yfoY53QXEnI",
                    },
                    {
                        "title": "박스 모델",
                        "video_url": "https://www.youtube.com/watch?v=rIO5326FgPE",
                    },
                ],
            },
            {
                "title": "레이아웃 디자인",
                "lessons": [
                    {
                        "title": "Flexbox 활용",
                        "video_url": "https://www.youtube.com/watch?v=JJSoEo8JSnc",
                    },
                    {
                        "title": "Grid 레이아웃",
                        "video_url": "https://www.youtube.com/watch?v=9zBsdzdE4sM",
                    },
                    {
                        "title": "반응형 웹 디자인",
                        "video_url": "https://www.youtube.com/watch?v=srvUrASNj0s",
                    },
                ],
            },
        ],
        "quiz_data": [
            {
                "title": "HTML과 CSS 기초 퀴즈",
                "description": "HTML 태그와 CSS 속성에 대한 이해도를 평가합니다.",
                "section_index": 1,  # 2번째 섹션
                "lesson_index": 1,  # 2번째 레슨
                "questions": [
                    {
                        "text": "다음 중 HTML의 제목 태그가 아닌 것은?",
                        "choices": [
                            {"text": "<h1>", "is_correct": False},
                            {"text": "<h3>", "is_correct": False},
                            {"text": "<heading>", "is_correct": True},
                            {"text": "<h6>", "is_correct": False},
                        ],
                    },
                    {
                        "text": "CSS에서 클래스 선택자는 어떤 기호로 시작하는가?",
                        "choices": [
                            {"text": "#", "is_correct": False},
                            {"text": ".", "is_correct": True},
                            {"text": "@", "is_correct": False},
                            {"text": "&", "is_correct": False},
                        ],
                    },
                    {
                        "text": "Flexbox에서 컨테이너 내 아이템을 가로축 기준으로 정렬하는 속성은?",
                        "choices": [
                            {"text": "align-items", "is_correct": False},
                            {"text": "justify-content", "is_correct": True},
                            {"text": "flex-direction", "is_correct": False},
                            {"text": "align-content", "is_correct": False},
                        ],
                    },
                ],
            },
            {
                "title": "레이아웃 디자인 퀴즈",
                "description": "CSS 레이아웃에 대한 이해도를 평가합니다.",
                "section_index": 2,  # 3번째 섹션
                "lesson_index": 2,  # 3번째 레슨
                "questions": [
                    {
                        "text": "반응형 웹 디자인에 필수적인 HTML 태그는?",
                        "choices": [
                            {"text": "<responsive>", "is_correct": False},
                            {"text": "<viewport>", "is_correct": False},
                            {"text": '<meta name="viewport">', "is_correct": True},
                            {"text": "<media>", "is_correct": False},
                        ],
                    },
                    {
                        "text": "CSS Grid에서 열(column)의 크기를 지정하는 속성은?",
                        "choices": [
                            {"text": "grid-column-size", "is_correct": False},
                            {"text": "grid-template-columns", "is_correct": True},
                            {"text": "column-template", "is_correct": False},
                            {"text": "grid-columns", "is_correct": False},
                        ],
                    },
                ],
            },
        ],
    },
    # 자바스크립트
    {
        "title": "실전 JavaScript 프로그래밍",
        "description": "JavaScript의 핵심 개념과 DOM 조작, 이벤트 처리, 비동기 프로그래밍 등을 배우는 강의입니다. 실제 프로젝트를 통해 실습합니다.",
        "price": 59900,
        "color": (255, 215, 0),  # 골드
        "sections": [
            {
                "title": "JavaScript 기초",
                "lessons": [
                    {
                        "title": "변수와 데이터 타입",
                        "video_url": "https://www.youtube.com/watch?v=W6NZfCO5SIk",
                    },
                    {
                        "title": "연산자와 표현식",
                        "video_url": "https://www.youtube.com/watch?v=hdI2bqOjy3c",
                    },
                    {
                        "title": "함수와 스코프",
                        "video_url": "https://www.youtube.com/watch?v=Qqx_wzMmFeA",
                    },
                ],
            },
            {
                "title": "DOM 조작",
                "lessons": [
                    {
                        "title": "DOM 요소 선택하기",
                        "video_url": "https://www.youtube.com/watch?v=0ik6X4DJKCc",
                    },
                    {
                        "title": "이벤트 처리",
                        "video_url": "https://www.youtube.com/watch?v=XF1_MlZ5l6M",
                    },
                    {
                        "title": "HTML 요소 생성 및 수정",
                        "video_url": "https://www.youtube.com/watch?v=y17RuWkWdn8",
                    },
                ],
            },
            {
                "title": "비동기 프로그래밍",
                "lessons": [
                    {
                        "title": "Promise 이해하기",
                        "video_url": "https://www.youtube.com/watch?v=DHvZLI7Db8E",
                    },
                    {
                        "title": "async/await 활용",
                        "video_url": "https://www.youtube.com/watch?v=V_Kr9OSfDeU",
                    },
                    {
                        "title": "API 호출과 데이터 처리",
                        "video_url": "https://www.youtube.com/watch?v=4K33w-0-p2c",
                    },
                ],
            },
        ],
        "quiz_data": [
            {
                "title": "JavaScript 기본 개념 퀴즈",
                "description": "JavaScript의 기본 문법과 DOM 조작에 대한 이해도를 평가합니다.",
                "section_index": 1,  # 2번째 섹션
                "lesson_index": 1,  # 2번째 레슨
                "questions": [
                    {
                        "text": "JavaScript에서 변수를 선언하는 키워드가 아닌 것은?",
                        "choices": [
                            {"text": "var", "is_correct": False},
                            {"text": "let", "is_correct": False},
                            {"text": "const", "is_correct": False},
                            {"text": "function", "is_correct": True},
                        ],
                    },
                    {
                        "text": "다음 중 DOM 요소를 선택하는 메소드가 아닌 것은?",
                        "choices": [
                            {"text": "getElementById()", "is_correct": False},
                            {"text": "querySelector()", "is_correct": False},
                            {"text": "selectElement()", "is_correct": True},
                            {"text": "getElementsByClassName()", "is_correct": False},
                        ],
                    },
                    {
                        "text": "Promise의 상태가 아닌 것은?",
                        "choices": [
                            {"text": "pending", "is_correct": False},
                            {"text": "fulfilled", "is_correct": False},
                            {"text": "rejected", "is_correct": False},
                            {"text": "completed", "is_correct": True},
                        ],
                    },
                ],
            },
            {
                "title": "비동기 프로그래밍 퀴즈",
                "description": "JavaScript의 비동기 프로그래밍에 대한 이해도를 평가합니다.",
                "section_index": 2,  # 3번째 섹션
                "lesson_index": 2,  # 3번째 레슨
                "questions": [
                    {
                        "text": "async/await는 무엇을 기반으로 하는가?",
                        "choices": [
                            {"text": "Callbacks", "is_correct": False},
                            {"text": "Events", "is_correct": False},
                            {"text": "Promises", "is_correct": True},
                            {"text": "Observers", "is_correct": False},
                        ],
                    },
                    {
                        "text": "다음 중 비동기 작업을 처리하는 방법이 아닌 것은?",
                        "choices": [
                            {"text": "Callbacks", "is_correct": False},
                            {"text": "Promises", "is_correct": False},
                            {"text": "async/await", "is_correct": False},
                            {"text": "synchronized", "is_correct": True},
                        ],
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "개발 및 테스트용 가상 데이터를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="기존 데이터를 모두 삭제하고 진행합니다.",
        )

    def handle(self, *args, **options):
        self.stdout.write("가상 데이터 생성을 시작합니다...")

        with transaction.atomic():
            # 기존 데이터 초기화 (선택 사항)
            if (
                options["clear"]
                or input(
                    "기존 데이터를 모두 삭제하고 진행하시겠습니까? (y/n): "
                ).lower()
                == "y"
            ):
                self.clear_data()
                self.stdout.write(
                    self.style.SUCCESS("기존 데이터가 모두 삭제되었습니다.")
                )

            # 1. 사용자 생성
            students = self.create_students(10)
            instructors = self.create_instructors(10)
            self.create_managers(3)

            # 2. 강좌, 섹션, 레슨, 퀴즈 생성
            all_courses = []
            for i, instructor in enumerate(instructors):
                # 각 강사당 3개의 강좌 생성
                for j in range(3):
                    # 강의 데이터는 미리 정의된 템플릿에서 선택하고 강사별로 약간 변형
                    template = COURSE_DATA[j % len(COURSE_DATA)]
                    course_idx = i * 3 + j + 1  # 강좌 고유 번호

                    # 강좌 생성
                    course_title = f"{template['title']} {course_idx}"
                    course = Course.objects.create(
                        instructor=instructor,
                        title=course_title,
                        description=template["description"],
                        price=template["price"],
                        status="approved",
                    )

                    # 섹션 생성
                    sections = []
                    # 첫 번째 섹션의 첫 번째 레슨에서 유튜브 ID를 가져와 썸네일 설정
                    try:
                        first_lesson_url = template["sections"][0]["lessons"][0][
                            "video_url"
                        ]
                        self.set_youtube_thumbnail(course, first_lesson_url)
                    except Exception as e:
                        # 유튜브 썸네일 설정에 실패하면 색상 기반 썸네일 생성
                        self.create_and_set_thumbnail(course, template["color"])

                    all_courses.append(course)

                    # 섹션 생성
                    sections = []
                    for k, section_data in enumerate(template["sections"]):
                        section = Section.objects.create(
                            course=course, title=section_data["title"], order=k + 1
                        )
                        sections.append(section)

                        # 레슨 생성
                        for index, lesson_data in enumerate(section_data["lessons"]):
                            Lesson.objects.create(
                                section=section,
                                title=lesson_data["title"],
                                video_url=lesson_data["video_url"],
                                order=index + 1,
                            )

                    # 퀴즈 생성
                    if "quiz_data" in template:
                        for quiz_data in template["quiz_data"]:
                            # 섹션과 레슨 인덱스 가져오기
                            section_index = quiz_data.get(
                                "section_index", 0
                            )  # 기본값은 첫 번째 섹션
                            lesson_index = quiz_data.get(
                                "lesson_index", 0
                            )  # 기본값은 첫 번째 레슨

                            # 인덱스 범위 체크
                            if section_index < len(sections):
                                target_section = sections[section_index]
                            else:
                                target_section = sections[0] if sections else None

                            # 해당 섹션의 레슨 가져오기
                            if target_section:
                                target_lessons = Lesson.objects.filter(
                                    section=target_section
                                ).order_by("order")
                                if lesson_index < len(target_lessons):
                                    target_lesson = target_lessons[lesson_index]
                                else:
                                    target_lesson = (
                                        target_lessons.first()
                                        if target_lessons.exists()
                                        else None
                                    )
                            else:
                                target_lesson = None

                            # 퀴즈 생성
                            quiz = Quiz.objects.create(
                                title=f"{course_title} - {quiz_data['title']}",
                                description=quiz_data["description"],
                                course=course,
                                section=target_section,
                                lesson=target_lesson,
                                instructor=instructor,
                            )

                            # 문제 및 선택지 생성
                            for q_idx, question_data in enumerate(
                                quiz_data["questions"]
                            ):
                                question = Question.objects.create(
                                    quiz=quiz,
                                    text=question_data["text"],
                                    order=q_idx + 1,
                                )

                                for c_idx, choice_data in enumerate(
                                    question_data["choices"]
                                ):
                                    Choice.objects.create(
                                        question=question,
                                        text=choice_data["text"],
                                        is_correct=choice_data["is_correct"],
                                    )

                            # 퀴즈 시도 생성 (학생마다 일부 퀴즈만 풀도록)
                            if random.random() < 0.7:  # 70% 확률로 퀴즈 시도 생성
                                for student in students[:5]:  # 일부 학생만 퀴즈 시도
                                    self.create_quiz_attempt(quiz, student)

            # 3. 요약 출력
            self.print_summary()

        self.stdout.write(self.style.SUCCESS("가상 데이터 생성이 완료되었습니다!"))

    def set_youtube_thumbnail(self, course, youtube_url):
        """유튜브 동영상 썸네일을 강의 썸네일로 설정"""
        try:
            # 유튜브 비디오 ID 추출
            video_id = self.get_youtube_id(youtube_url)
            if not video_id:
                raise ValueError(f"유효한 YouTube ID를 찾을 수 없습니다: {youtube_url}")

            # 유튜브 썸네일 URL
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

            # 썸네일 이미지 다운로드
            try:
                image_content = urllib.request.urlopen(thumbnail_url).read()
            except:
                # maxresdefault.jpg가 없으면 hqdefault.jpg 시도
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                image_content = urllib.request.urlopen(thumbnail_url).read()

            # 이미지 파일 이름 생성
            image_name = f"course_{course.id}_thumbnail.jpg"

            # Course 모델에 이미지 저장
            course.thumbnail.save(image_name, ContentFile(image_content), save=True)

            print(f"YouTube 썸네일 설정 완료: {course.title}")
            return True

        except Exception as e:
            print(f"YouTube 썸네일 가져오기 실패: {e}")
            return False

    def create_and_set_thumbnail(self, course, color):
        """강의 썸네일 이미지 생성 및 설정"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # 임시 이미지 생성 (1280x720)
            width, height = 1280, 720
            image = Image.new("RGB", (width, height), color)
            draw = ImageDraw.Draw(image)

            # 배경에 패턴 추가 (선택적)
            for i in range(20):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                draw.line((x1, y1, x2, y2), fill=(255, 255, 255, 50), width=2)

            # 강의 제목 추가
            title = course.title
            # PIL에서 TTF 폰트를 사용할 수 있으나, 기본 폰트로 진행
            # 텍스트 위치 계산 (중앙 정렬)
            text_width = width // 2
            text_height = height // 2

            # 텍스트 그리기
            draw.text(
                (text_width, text_height), title, fill=(255, 255, 255), anchor="mm"
            )

            # 이미지를 저장하고 강의 모델에 할당
            image_io = BytesIO()
            image.save(image_io, format="JPEG", quality=90)
            image_name = f"course_{course.id}_thumbnail.jpg"

            # 이미지 파일 저장 및 모델에 할당
            course.thumbnail.save(
                image_name, ContentFile(image_io.getvalue()), save=True
            )

            print(f"Created thumbnail for course: {course.title}")
        except Exception as e:
            print(f"Error creating thumbnail: {e}")

    def clear_data(self):
        """기존 데이터를 모두 삭제합니다."""
        Answer.objects.all().delete()
        QuizAttempt.objects.all().delete()
        Choice.objects.all().delete()
        Question.objects.all().delete()
        Quiz.objects.all().delete()
        Lesson.objects.all().delete()
        Section.objects.all().delete()
        Course.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_students(self, count):
        """학생 사용자를 생성합니다."""
        students = []
        self.stdout.write(f"{count}명의 학생 생성 중...")

        for i in range(1, count + 1):
            email = f"student{i}@example.com"

            # 이미 존재하는 이메일은 건너뜁니다
            if User.objects.filter(email=email).exists():
                student = User.objects.get(email=email)
                students.append(student)
                continue

            student = User.objects.create_user(
                email=email,
                username=f"student{i}",
                password=f"student{i}",
                role=User.Role.STUDENT,
                is_verified=True,
            )
            students.append(student)

        self.stdout.write(
            self.style.SUCCESS(f"{len(students)}명의 학생이 생성되었습니다.")
        )
        return students

    def create_instructors(self, count):
        """강사 사용자를 생성합니다."""
        instructors = []
        self.stdout.write(f"{count}명의 강사 생성 중...")

        specialties = [
            "Python",
            "JavaScript",
            "Java",
            "Web",
            "Mobile",
            "Data",
            "AI",
            "DevOps",
            "Security",
            "Game",
        ]

        for i in range(1, count + 1):
            email = f"instructor{i}@example.com"

            # 이미 존재하는 이메일은 건너뜁니다
            if User.objects.filter(email=email).exists():
                instructor = User.objects.get(email=email)
                instructors.append(instructor)
                continue

            specialties[i % len(specialties)]
            instructor = User.objects.create_user(
                email=email,
                username=f"instructor{i}",
                password=f"instructor{i}",
                role=User.Role.INSTRUCTOR,
                is_verified=True,
            )
            instructors.append(instructor)

        self.stdout.write(
            self.style.SUCCESS(f"{len(instructors)}명의 강사가 생성되었습니다.")
        )
        return instructors

    def create_managers(self, count):
        """관리자 사용자를 생성합니다."""
        managers = []
        self.stdout.write(f"{count}명의 관리자 생성 중...")

        for i in range(1, count + 1):
            email = f"manager{i}@example.com"

            # 이미 존재하는 이메일은 건너뜁니다
            if User.objects.filter(email=email).exists():
                manager = User.objects.get(email=email)
                managers.append(manager)
                continue

            manager = User.objects.create_user(
                email=email,
                username=f"manager{i}",
                password=f"manager{i}",
                role=User.Role.MANAGER,
                is_staff=True,
                is_verified=True,
            )
            managers.append(manager)

        self.stdout.write(
            self.style.SUCCESS(f"{len(managers)}명의 관리자가 생성되었습니다.")
        )
        return managers

    def create_quiz_attempt(self, quiz, student):
        """퀴즈 시도와 답변을 생성합니다."""
        # 퀴즈 시도 생성
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            is_completed=True,
            completed_at=timezone.now() - timedelta(days=random.randint(0, 30)),
        )

        # 각 문제에 답변 생성
        questions = Question.objects.filter(quiz=quiz)
        for question in questions:
            choices = Choice.objects.filter(question=question)
            if not choices.exists():
                continue

            # 70% 확률로 정답, 30% 확률로 오답 선택
            if random.random() < 0.7:
                selected_choice = choices.filter(is_correct=True).first()
            else:
                wrong_choices = choices.filter(is_correct=False)
                selected_choice = (
                    random.choice(list(wrong_choices))
                    if wrong_choices.exists()
                    else choices.first()
                )

            if selected_choice:
                Answer.objects.create(
                    attempt=attempt, question=question, selected_choice=selected_choice
                )

        # 점수 계산은 Answer 모델의 save() 메소드에서 자동으로 처리됨
        return attempt

    def get_youtube_id(self, url):
        """YouTube URL에서 ID 추출"""
        # URL이 이미 임베드 형식인지 확인
        if "youtube.com/embed/" in url:
            return url.split("/")[-1]

        # 일반 YouTube URL에서 ID 추출
        pattern = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def print_summary(self):
        """생성된 데이터의 요약 정보를 출력합니다."""
        self.stdout.write("\n=== 데이터 생성 요약 ===")
        self.stdout.write(f"총 사용자: {User.objects.count()}명")
        self.stdout.write(
            f"- 학생: {User.objects.filter(role=User.Role.STUDENT).count()}명"
        )
        self.stdout.write(
            f"- 강사: {User.objects.filter(role=User.Role.INSTRUCTOR).count()}명"
        )
        self.stdout.write(
            f"- 관리자: {User.objects.filter(role=User.Role.MANAGER).count()}명"
        )
        self.stdout.write(f"총 강좌: {Course.objects.count()}개")
        self.stdout.write(f"총 섹션: {Section.objects.count()}개")
        self.stdout.write(f"총 레슨: {Lesson.objects.count()}개")
        self.stdout.write(f"총 퀴즈: {Quiz.objects.count()}개")
        self.stdout.write(f"총 문제: {Question.objects.count()}개")
        self.stdout.write(f"총 선택지: {Choice.objects.count()}개")
        self.stdout.write(f"총 퀴즈 시도: {QuizAttempt.objects.count()}개")
        self.stdout.write(f"총 답변: {Answer.objects.count()}개")
        self.stdout.write("=======================\n")
