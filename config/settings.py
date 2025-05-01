import os
from pathlib import Path
import environ

# BASE_DIR 설정 (기본값 유지)
BASE_DIR = Path(__file__).resolve().parent.parent

# django-environ 초기화
env = environ.Env(DEBUG=(bool, False))
# .env 파일 읽기
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# .env 파일 누락 시 경고 표시 (선택 사항)
if not os.path.exists(os.path.join(BASE_DIR, ".env")):
    print("⚠️  .env 파일이 존재하지 않습니다. 환경변수를 불러올 수 없습니다.")

# 환경변수로부터 값 가져오기
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

PORTONE_PG_PROVIDER = env.str("PORTONE_PG_PROVIDER", default="")
PORTONE_SHOP_ID = env("PORTONE_SHOP_ID", default="")

PORTONE_PG = PORTONE_PG_PROVIDER
PORTONE_API_KEY = env("PORTONE_API_KEY", default="")
PORTONE_API_SECRET = env("PORTONE_API_SECRET", default="")
# 데이터베이스 설정
DATABASES = {"default": env.db()}

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_yasg",
    "debug_toolbar",
    "django_filters",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.kakao",
    "allauth.socialaccount.providers.naver",
]

LOCAL_APPS = [
    "accounts",
    "courses",
    "courses.templatetags",
    "enrollments",
    "quizzes",
    "reviews",
    "qna",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

INTERNAL_IPS = ["127.0.0.1"]

SKIP_PAYMENT_VERIFICATION = DEBUG

SITE_ID = 1

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")

KAKAO_CLIENT_ID = env("KAKAO_CLIENT_ID", default="")
KAKAO_CLIENT_SECRET = env("KAKAO_CLIENT_SECRET", default="")

NAVER_CLIENT_ID = env("NAVER_CLIENT_ID", default="")
NAVER_CLIENT_SECRET = env("NAVER_CLIENT_SECRET", default="")

SOCIALACCOUNT_LOGIN_ON_GET = True

# 수정된 코드 - 필요한 소셜 로그인만 활성화
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print(
        "Warning: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are not set. Google login will be disabled."
    )

if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    print(
        "Warning: NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are not set. Naver login will be disabled."
    )

if not KAKAO_CLIENT_ID or not KAKAO_CLIENT_SECRET:
    print(
        "Warning: KAKAO_CLIENT_ID and KAKAO_CLIENT_SECRET are not set. Kakao login will be disabled."
    )

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "kakao": {
        "APP": {
            "client_id": KAKAO_CLIENT_ID,
            "secret": KAKAO_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "profile_nickname",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "naver": {
        "APP": {
            "client_id": NAVER_CLIENT_ID,
            "secret": NAVER_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "name",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
}


LOGIN_REDIRECT_URL = "/"  # 로그인 성공 후 이동할 URL
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # 로그아웃 후 이동할 URL
ACCOUNT_SIGNUP_REDIRECT_URL = "account_login"

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "none"

# 템플릿 오버라이드를 위한 추가 설정
ACCOUNT_TEMPLATE_EXTENSION = "html"

# 회원가입 후 자동 로그인 설정
ACCOUNT_SESSION_REMEMBER = True  # 세션 유지
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # 이메일 확인 시 자동 로그인

# 로그인 및 회원가입 필드 설정 (새로운 방식)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# 소셜 계정 이메일 검증 비활성화
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False


# 자동 가입 활성화 (True 시 /accounts/signup/ 없이 자동 가입)
SOCIALACCOUNT_AUTO_SIGNUP = True

# 유저명 중복 방지
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_ADAPTER = "accounts.adapters.CustomSocialAccountAdapter"
