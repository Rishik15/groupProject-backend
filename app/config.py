import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in ["true", "1", "yes", "y"]


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_timeout": 30,
        "connect_args": {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "charset": "utf8mb4",
        },
    }

    CORS_ORIGIN = os.getenv("CORS_ORIGIN")

    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "America/New_York")
    DB_TIMEZONE = os.getenv("DB_TIMEZONE", "-04:00")

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing. Set it in .env")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is missing. Set it in .env")

    if not CORS_ORIGIN:
        raise RuntimeError("CORS_ORIGIN is missing. Set it in .env")

    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", "4"))
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = str_to_bool(os.getenv("SESSION_COOKIE_SECURE"), False)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

    MEAL_IMAGES_SUBDIR = os.getenv("MEAL_IMAGES_SUBDIR", "meal_images")

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    if not CLOUDINARY_CLOUD_NAME:
        raise RuntimeError("CLOUDINARY_CLOUD_NAME is missing. Set it in .env")

    if not CLOUDINARY_API_KEY:
        raise RuntimeError("CLOUDINARY_API_KEY is missing. Set it in .env")

    if not CLOUDINARY_API_SECRET:
        raise RuntimeError("CLOUDINARY_API_SECRET is missing. Set it in .env")

    GOOGLE_LOGIN_REDIRECT_URI = os.getenv("GOOGLE_LOGIN_REDIRECT_URI")
    GOOGLE_LOGIN_FRONTEND_REDIRECT_URI = os.getenv("GOOGLE_LOGIN_FRONTEND_REDIRECT_URI")
    GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

    GOOGLE_OAUTH_CLIENT_SECRETS_FILE = os.getenv(
        "GOOGLE_OAUTH_CLIENT_SECRETS_FILE",
        "/app/client_secret.json",
    )

    GOOGLE_LOGIN_SCOPES = [
        scope.strip()
        for scope in os.getenv(
            "GOOGLE_LOGIN_SCOPES",
            "openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile",
        ).split(",")
        if scope.strip()
    ]

    GOOGLE_OAUTH_SCOPES = [
        scope.strip()
        for scope in os.getenv(
            "GOOGLE_OAUTH_SCOPES",
            "https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email",
        ).split(",")
        if scope.strip()
    ]
