from logging import root
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-ai-resume-analyzer-key-2026!'),
    DB_TYPE=(str, 'mysql'), # 'sqlite' or 'mysql'
    DB_NAME=(str, 'resume_analyzer'),
    DB_USER=(str, 'root'),
    DB_PASSWORD=(str, 'krisha@231005'),
    DB_HOST=(str, '127.0.0.1'),
    DB_PORT=(str, '3306'),
)

# Read .env file if it exists
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# Quick-start development settings - unsuitable for production
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analyzer.apps.AnalyzerConfig',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resume_analyzer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resume_analyzer.wsgi.application'

# Database configuration (MySQL with SQLite fallback)
DB_TYPE = env('DB_TYPE')

if DB_TYPE == 'mysql':
    import pymysql
    mysql_connected = False
    host = env('DB_HOST')
    port = int(env('DB_PORT', 3306) or 3306)
    user = env('DB_USER')
    password = env('DB_PASSWORD')
    db_name = env('DB_NAME')
    
    try:
        # Fast test connection to verify database credentials
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=2
        )
        conn.close()
        mysql_connected = True
    except pymysql.err.OperationalError as e:
        # Error 1049 is "Unknown database". We ignore this here because 
        # our apps.py ready() function will auto-create the database schema!
        if e.args[0] == 1049:
            mysql_connected = True
        else:
            print("\n" + "="*80)
            print("ResuAI DATABASE ERROR: MySQL connection failed!")
            print(f"Error Details: {e}")
            print("\nPlease update your '.env' file with the correct MySQL credentials.")
            print(f"Current Config -> Host: {host}:{port} | User: {user} | Password: {'[PROVIDED]' if password else '[EMPTY]'}")
            print("\nACTION: Falling back to SQLite ('db.sqlite3') to keep the server running.")
            print("="*80 + "\n")
    except Exception as e:
        print("\n" + "="*80)
        print("ResuAI DATABASE ERROR: Unexpected connection error.")
        print(f"Error Details: {e}")
        print("\nACTION: Falling back to SQLite ('db.sqlite3') to keep the server running.")
        print("="*80 + "\n")

    if mysql_connected:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': db_name,
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                }
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = []

# Media files (Uploaded resumes)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
