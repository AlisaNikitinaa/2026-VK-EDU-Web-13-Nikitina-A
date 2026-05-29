import os
from pathlib import Path
from dotenv import load_dotenv

env_file = '.env.local' if os.path.exists('.env.local') else '.env.docker'
load_dotenv(env_file)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-_jxmv2xhp_=@4x601h4mj(0%69y%qup(jh4%&z8388s1g_kvk*')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'app',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'askme_nikitina.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'askme_nikitina.wsgi.application'

DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.getenv('DB_NAME', 'askme_db'),
            'USER': os.getenv('DB_USER', 'askme_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = ['127.0.0.1', 'localhost']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# ─── Redis ────────────────────────────────────────────────────
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

# Авто-заплатка для локальной разработки на Windows (вне Docker)
if os.name == 'nt' and REDIS_HOST == 'redis':
    REDIS_HOST = '127.0.0.1'

REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_CACHE_DB  = 0   # для кеша django
REDIS_BROKER_DB = 1   # для celery broker
REDIS_BEAT_DB   = 2   # для celery beat расписания


# ─── Cache (django-redis) ─────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 60 * 10,
    }
}


# ─── Celery ───────────────────────────────────────────────────
CELERY_BROKER_URL     = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"
CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_REDBEAT_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "update-popular-tags": {
        "task": "app.tasks.update_popular_tags",
        "schedule": crontab(minute=0, hour="*/3"),   # каждые 3 часа
    },
    "update-best-members": {
        "task": "app.tasks.update_best_members",
        "schedule": crontab(minute=30, hour="*/1"),  # каждый час в :30
    },
}


# ─── Email (MailDev) ──────────────────────────────────────────
EMAIL_BACKEND     = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST        = os.getenv('EMAIL_HOST', 'maildev')

if os.name == 'nt' and EMAIL_HOST == 'maildev':
    EMAIL_HOST = '127.0.0.1'

EMAIL_PORT        = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_USE_TLS     = False
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@askme.local')


# ─── Centrifugo ───────────────────────────────────────────────
CENTRIFUGO_HOST = os.getenv('CENTRIFUGO_HOST', 'centrifugo')

if os.name == 'nt' and CENTRIFUGO_HOST == 'centrifugo':
    CENTRIFUGO_HOST = '127.0.0.1'

CENTRIFUGO_URL     = os.getenv('CENTRIFUGO_URL', f'http://{CENTRIFUGO_HOST}:8000')
CENTRIFUGO_API_KEY = os.getenv('CENTRIFUGO_API_KEY', '')
CENTRIFUGO_SECRET  = os.getenv('CENTRIFUGO_SECRET', '')