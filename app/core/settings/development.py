import os
from datetime import timedelta

# django-rest-framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        "account.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
}

# simple_jwt
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
    'USER_ID_FIELD': 'id'
}
SECRET_KEY = "bookit_sold"

# Cors
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    f'http://{os.getenv("FRONT_CSRF_TRUSTED_ORIGINS")}',
    f'https://{os.getenv("FRONT_CSRF_TRUSTED_ORIGINS")}',
    f'http://{os.getenv("API_CSRF_TRUSTED_ORIGINS")}',
    f'https://{os.getenv("API_CSRF_TRUSTED_ORIGINS")}',
]
CSRF_TRUSTED_ORIGINS = [
    f'http://{os.getenv("FRONT_CSRF_TRUSTED_ORIGINS")}',
    f'https://{os.getenv("FRONT_CSRF_TRUSTED_ORIGINS")}',
    f'http://{os.getenv("API_CSRF_TRUSTED_ORIGINS")}',
    f'https://{os.getenv("API_CSRF_TRUSTED_ORIGINS")}',
]
CSRF_COOKIE_DOMAIN = os.getenv("FRONT_CSRF_TRUSTED_ORIGINS")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        },
        'django.request': {
            'handlers': ['db_log'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}
