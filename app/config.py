import os


class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:root@db:3306/exercise_app"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
