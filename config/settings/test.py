from .base import *

DEBUG = False
ALLOWED_HOSTS = ["testserver"]

# 테스트용 데이터베이스 (인메모리 SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 테스트 이메일 설정
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 테스트 시 비밀번호 해싱 속도 높이기
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# 테스트 시 파일 업로드 설정
MEDIA_ROOT = BASE_DIR / "test_media"

# 결제 검증 스킵 (테스트 환경에서)
SKIP_PAYMENT_VERIFICATION = True

# 소셜 로그인 테스트 설정
GOOGLE_CLIENT_ID = "test_id"
GOOGLE_CLIENT_SECRET = "test_secret"
KAKAO_CLIENT_ID = "test_id"
KAKAO_CLIENT_SECRET = "test_secret"
NAVER_CLIENT_ID = "test_id"
NAVER_CLIENT_SECRET = "test_secret"
