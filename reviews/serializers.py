from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """리뷰 시리얼라이저"""

    user_name = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Review
        fields = [
            "id",
            "course",
            "user",
            "user_name",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]
