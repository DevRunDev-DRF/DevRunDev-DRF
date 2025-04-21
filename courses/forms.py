from django import forms
from .models import Course, Section, Lesson


class CourseForm(forms.ModelForm):
    """강의 생성 및 수정 폼"""

    class Meta:
        model = Course
        fields = ["title", "description", "price", "thumbnail", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "강의 제목을 입력하세요",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "강의에 대한 자세한 설명을 작성하세요",
                    "rows": 5,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "강의 가격을 입력하세요",
                    "min": 0,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # 사용자 객체 가져오기
        super().__init__(*args, **kwargs)

        # 새 강의 생성 시 상태 필드 제외
        if not self.instance.pk:
            self.fields.pop("status")
        # 기존 강의 수정 시, 관리자나 매니저가 아니면 상태 필드 읽기 전용으로 설정
        elif self.user and not (
            self.user.is_staff
            or getattr(self.user, "role", None)
            == getattr(self.user, "Role.MANAGER", None)
        ):
            # 필드를 읽기 전용으로 만들지만, 템플릿에서 처리하므로 여기서는 아무 작업도 하지 않음
            pass


class SectionForm(forms.ModelForm):
    """섹션 생성 및 수정 폼"""

    class Meta:
        model = Section
        fields = ["title", "order"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "섹션 제목을 입력하세요",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "섹션 순서를 입력하세요",
                    "min": 1,
                }
            ),
        }


class LessonForm(forms.ModelForm):
    """레슨 생성 및 수정 폼"""

    class Meta:
        model = Lesson
        fields = ["title", "video_url", "order"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "레슨 제목을 입력하세요",
                }
            ),
            "video_url": forms.URLInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "YouTube 비디오 URL을 입력하세요",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "레슨 순서를 입력하세요",
                    "min": 1,
                }
            ),
        }
