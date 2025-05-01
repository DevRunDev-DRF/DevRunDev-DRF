from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# 개발 환경 데이터베이스 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 개발용 이메일 설정 (콘솔에 출력)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 디버그 툴바 추가
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INTERNAL_IPS = ["127.0.0.1"]

# 결제 검증 스킵 (개발 환경에서만)
SKIP_PAYMENT_VERIFICATION = True

# 소셜 로그인 설정 (개발용 더미 값)
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")
KAKAO_CLIENT_ID = env("KAKAO_CLIENT_ID", default="")
KAKAO_CLIENT_SECRET = env("KAKAO_CLIENT_SECRET", default="")
NAVER_CLIENT_ID = env("NAVER_CLIENT_ID", default="")
NAVER_CLIENT_SECRET = env("NAVER_CLIENT_SECRET", default="")

# 결제 관련 설정 (개발용)
PORTONE_PG_PROVIDER = env.str("PORTONE_PG_PROVIDER", default="")
PORTONE_SHOP_ID = env("PORTONE_SHOP_ID", default="")
PORTONE_PG = PORTONE_PG_PROVIDER
PORTONE_API_KEY = env("PORTONE_API_KEY", default="")
PORTONE_API_SECRET = env("PORTONE_API_SECRET", default="")
