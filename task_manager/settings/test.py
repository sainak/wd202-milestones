"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-hn4*^-v@9xjaxl&+-1u$hrl*d5wn^&j5_ir%18$-j2z@77u-g6",
)
TEST_RUNNER = "django.test.runner.DiscoverRunner"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
