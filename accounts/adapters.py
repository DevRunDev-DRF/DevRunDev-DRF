from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # 이미 로그인 되어있는 경우는 그냥 넘어감
        if sociallogin.is_existing:
            return

        # 이메일이 있는 경우
        if sociallogin.email_addresses:
            # 기존 이메일 있는지 확인
            existing_user = sociallogin.user_model.objects.filter(
                email=sociallogin.email_addresses[0].email
            ).first()

            # 기존 유저가 있으면 그 유저로 로그인 처리
            if existing_user:
                sociallogin.connect(request, existing_user)
                messages.success(request, "기존 계정으로 로그인되었습니다.")
                # 이 부분은 일부러 return 문이 없음 - 이후 자동 로그인 처리를 위해

    def save_user(self, request, sociallogin, form=None):
        # 기본 사용자 저장 메서드 호출
        user = super().save_user(request, sociallogin, form)

        # 사용자 저장 후 자동으로 로그인 처리
        # (새 계정일 경우 이 메서드가 호출됨)
        perform_login(
            request, user, email_verification=self.adapter.settings.EMAIL_VERIFICATION
        )

        messages.success(
            request,
            f"환영합니다! {user.username}님, 소셜 계정으로 회원가입 및 로그인되었습니다.",
        )

        return user
