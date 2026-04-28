import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv("/app/.env")
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:root@db:3306/exercise_app"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "UTC")
    DB_TIMEZONE = os.getenv("DB_TIMEZONE", "+00:00")

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing. Set it in .env")

    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 200 * 1024 * 1024))

    MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/app/media")
    MEDIA_URL_PREFIX = os.getenv("MEDIA_URL_PREFIX", "/uploads")
    MEAL_IMAGES_SUBDIR = os.getenv("MEAL_IMAGES_SUBDIR", "meal_images")

    GOOGLE_OAUTH_CLIENT_SECRETS_FILE = os.getenv(
        "GOOGLE_OAUTH_CLIENT_SECRETS_FILE", "/app/client_secret.json"
    )

    GOOGLE_LOGIN_REDIRECT_URI = os.getenv(
        "GOOGLE_LOGIN_REDIRECT_URI", "http://localhost:8080/auth/googleLogin/callback"
    )
    GOOGLE_LOGIN_SCOPES = [
        scope.strip()
        for scope in os.getenv(
            "GOOGLE_LOGIN_SCOPES",
            "openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile",
        ).split(",")
        if scope.strip()
    ]
    GOOGLE_LOGIN_FRONTEND_REDIRECT_URI = os.getenv(
        "GOOGLE_LOGIN_FRONTEND_REDIRECT_URI", "http://localhost:5173"
    )

    GOOGLE_OAUTH_REDIRECT_URI = os.getenv(
        "GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8080/auth/googleOauth/callback"
    )
    GOOGLE_OAUTH_SCOPES = [
        scope.strip()
        for scope in os.getenv(
            "GOOGLE_OAUTH_SCOPES",
            "https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email",
        ).split(",")
        if scope.strip()
    ]
