"""
Django settings for the IssueHub backend.

All environment-specific values are read from environment variables (see
.env.example) so the same settings module works for local dev, Docker and
production deployment.
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# The frontend origin(s) allowed to talk to this API.
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    # default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)

# Used to build links (email verification, password reset) that point at the
# frontend app rather than the API itself.
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "core",
    "accounts",
    "tickets",
    "rag",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
        conn_max_age=600,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=config("ACCESS_TOKEN_LIFETIME_MIN", default=15, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_LIFETIME_DAYS", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Email
# In development this prints emails to the console instead of sending them.
# Point EMAIL_BACKEND at django.core.mail.backends.smtp.EmailBackend (and set
# the EMAIL_HOST_* vars) to send real email in production.
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="IssueHub <noreply@issuehub.local>")

# How long an email verification / password reset link stays valid.
EMAIL_TOKEN_EXPIRY_HOURS = config("EMAIL_TOKEN_EXPIRY_HOURS", default=48, cast=int)
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = config("PASSWORD_RESET_TOKEN_EXPIRY_HOURS", default=2, cast=int)

# RAG (Retrieval-Augmented Generation) settings.
# The retrieval half always works with no external services: the default
# embedding provider is a small local deterministic model and the default
# vector backend is rebuilt in-memory from KnowledgeEntry rows. Plug in a real
# LLM provider + key to get generated answers instead of extractive snippets,
# and/or switch the vector backend to pgvector for production. See
# docs/RAG_SETUP.md.
RAG_EMBED_PROVIDER = config("RAG_EMBED_PROVIDER", default="local")  # local | gemini | openai | mock
RAG_LLM_PROVIDER = config("RAG_LLM_PROVIDER", default="none")  # none | gemini | openai | mock
RAG_VECTOR_BACKEND = config("RAG_VECTOR_BACKEND", default="memory")  # memory | pgvector
RAG_TOP_K = config("RAG_TOP_K", default=4, cast=int)
RAG_CHUNK_SIZE = config("RAG_CHUNK_SIZE", default=512, cast=int)
RAG_CHUNK_OVERLAP = config("RAG_CHUNK_OVERLAP", default=40, cast=int)
# Embedding vector width. Must match the embedding provider: 256 for the local
# default, 768 for Gemini text-embedding-004, 1536 for OpenAI
# text-embedding-3-small. Only the pgvector store needs this to be exact.
RAG_EMBED_DIM = config("RAG_EMBED_DIM", default=256, cast=int)

# Provider model names + API keys (only read when the matching provider is set).
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")
GEMINI_EMBED_MODEL = config("GEMINI_EMBED_MODEL", default="models/text-embedding-004")
GEMINI_LLM_MODEL = config("GEMINI_LLM_MODEL", default="models/gemini-1.5-flash")

OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_EMBED_MODEL = config("OPENAI_EMBED_MODEL", default="text-embedding-3-small")
OPENAI_LLM_MODEL = config("OPENAI_LLM_MODEL", default="gpt-4o-mini")

# The pgvector store connects with this (defaults to the main DATABASE_URL).
RAG_PGVECTOR_URL = config("RAG_PGVECTOR_URL", default=config("DATABASE_URL", default=""))
