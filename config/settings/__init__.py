import os

# 기본값은 개발 환경
environment = os.environ.get("DJANGO_ENVIRONMENT", "development")

if environment == "production":
    from .production import *
elif environment == "test":
    from .test import *
else:
    from .development import *
