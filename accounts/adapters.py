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
