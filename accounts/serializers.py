from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, InstructorApplication


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "role",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = ["date_joined", "is_verified"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # 비밀번호가 변경되면 해시하여 저장
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    """회원가입 전용 시리얼라이저"""

    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }

    def validate(self, data):
        # 비밀번호 일치 검증
        if data["password"] != data.pop("password2"):
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """로그인 전용 시리얼라이저"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )
            if not user:
                raise serializers.ValidationError(
                    "이메일 또는 비밀번호가 올바르지 않습니다.", code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "이메일과 비밀번호를 모두 입력해주세요.", code="authorization"
            )

        data["user"] = user
        return data


class InstructorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorApplication
        fields = [
            "id",
            "user",
            "qualifications",
            "experience",
            "sample_video_url",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at", "user"]
