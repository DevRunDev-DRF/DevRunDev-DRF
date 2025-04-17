from rest_framework import serializers
from .models import Review
from accounts.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """리뷰 시리얼라이저"""

    user_details = UserSerializer(source="user", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_details",
            "course",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate(self, data):
        # 새 리뷰 생성 시 중복 체크
        request = self.context.get("request")
        if request and request.method == "POST":
            user = request.user
            course = data.get("course")

            # 이미 리뷰를 작성했는지 확인
            if Review.objects.filter(user=user, course=course).exists():
                raise serializers.ValidationError(
                    "이미 이 강의에 대한 리뷰를 작성했습니다."
                )

            # 수강 중인 강의인지 확인
            if not course.enrollments.filter(student=user).exists():
                raise serializers.ValidationError(
                    "수강 중인 강의에만 리뷰를 작성할 수 있습니다."
                )

        return data


class ReviewCreateSerializer(serializers.ModelSerializer):
    """리뷰 생성 전용 시리얼라이저"""

    class Meta:
        model = Review
        fields = ["course", "rating", "comment"]
