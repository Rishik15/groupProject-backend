import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in ["true", "1", "yes", "y"]


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    return value


class Config:
    ENVIRONMENT = get_env("ENVIRONMENT", "development")

    LOCAL_DATABASE_URL = "mysql+pymysql://root:root@db:3306/exercise_app"

    if ENVIRONMENT == "development":
        SQLALCHEMY_DATABASE_URI = LOCAL_DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = get_env("DATABASE_URL")

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

    CRON_SECRET = get_env("CRON_SECRET")

    CORS_ORIGIN = get_env("CORS_ORIGIN", "http://localhost:5173")

    APP_TIMEZONE = get_env("APP_TIMEZONE", "UTC")
    DB_TIMEZONE = get_env("DB_TIMEZONE", "+00:00")

    SECRET_KEY = get_env("SECRET_KEY")

    if not SECRET_KEY:
        if ENVIRONMENT == "development":
            SECRET_KEY = "local-dev-secret-key-change-in-production"
        else:
            raise RuntimeError("SECRET_KEY is missing. Set it in .env")

    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is missing. Set it in .env")

    if not CORS_ORIGIN:
        raise RuntimeError("CORS_ORIGIN is missing. Set it in .env")

    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(get_env("SESSION_LIFETIME_HOURS", "4"))
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = str_to_bool(
        get_env("SESSION_COOKIE_SECURE"),
        False,
    )
    SESSION_COOKIE_SAMESITE = get_env("SESSION_COOKIE_SAMESITE", "Lax")

    MAX_CONTENT_LENGTH = int(get_env("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

    MEAL_IMAGES_SUBDIR = get_env("MEAL_IMAGES_SUBDIR", "meal_images")

    CLOUDINARY_CLOUD_NAME = get_env("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = get_env("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = get_env("CLOUDINARY_API_SECRET")

    if ENVIRONMENT != "development":
        if not CLOUDINARY_CLOUD_NAME:
            raise RuntimeError("CLOUDINARY_CLOUD_NAME is missing. Set it in .env")

        if not CLOUDINARY_API_KEY:
            raise RuntimeError("CLOUDINARY_API_KEY is missing. Set it in .env")

        if not CLOUDINARY_API_SECRET:
            raise RuntimeError("CLOUDINARY_API_SECRET is missing. Set it in .env")

    GOOGLE_LOGIN_REDIRECT_URI = get_env(
        "GOOGLE_LOGIN_REDIRECT_URI",
        "http://localhost:8080/auth/googleLogin/callback",
    )

    GOOGLE_LOGIN_FRONTEND_REDIRECT_URI = get_env(
        "GOOGLE_LOGIN_FRONTEND_REDIRECT_URI",
        "http://localhost:5173",
    )

    GOOGLE_OAUTH_REDIRECT_URI = get_env(
        "GOOGLE_OAUTH_REDIRECT_URI",
        "http://localhost:8080/auth/googleOauth/callback",
    )

    GOOGLE_OAUTH_CLIENT_SECRETS_FILE = get_env(
        "GOOGLE_OAUTH_CLIENT_SECRETS_FILE",
        "/etc/secrets/client_secret.json",
    )

    GOOGLE_LOGIN_SCOPES = [
        scope.strip()
        for scope in get_env(
            "GOOGLE_LOGIN_SCOPES",
            "openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile",
        ).split(",")
        if scope.strip()
    ]

    GOOGLE_OAUTH_SCOPES = [
        scope.strip()
        for scope in get_env(
            "GOOGLE_OAUTH_SCOPES",
            "https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email",
        ).split(",")
        if scope.strip()
    ]