from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register(self):
        """회원가입 테스트"""
        url = reverse("accounts:register")
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "password2": "password123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("token" in response.data)
        self.assertEqual(User.objects.count(), 2)

    def test_login(self):
        """로그인 테스트"""
        url = reverse("accounts:login")
        data = {"email": "test@example.com", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("token" in response.data)

    def test_logout(self):
        """로그아웃 테스트"""
        # 먼저 로그인
        login_url = reverse("accounts:login")
        data = {"email": "test@example.com", "password": "password123"}
        login_response = self.client.post(login_url, data, format="json")
        token = login_response.data["token"]

        # 로그아웃 요청
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        logout_url = reverse("accounts:logout")
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 토큰이 더 이상 유효하지 않은지 확인
        me_url = reverse("accounts:user-me")
        me_response = self.client.get(me_url)
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile(self):
        """사용자 프로필 가져오기 테스트"""
        # 로그인
        login_url = reverse("accounts:login")
        data = {"email": "test@example.com", "password": "password123"}
        login_response = self.client.post(login_url, data, format="json")
        token = login_response.data["token"]

        # 프로필 요청
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        me_url = reverse("accounts:user-me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
