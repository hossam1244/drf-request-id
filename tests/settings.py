SECRET_KEY = "test-only-insecure-key"
DEBUG = False
ALLOWED_HOSTS = ["*"]
USE_TZ = True
ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "drf_request_id",
]

MIDDLEWARE = [
    "drf_request_id.middleware.RequestIDMiddleware",
    "django.middleware.common.CommonMiddleware",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
