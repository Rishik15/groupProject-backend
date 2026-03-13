import os  
class Config:  
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")  
    SQLALCHEMY_DATABASE_URI = os.getenv(  
    "DATABASE_URL",  
    "mysql+pymysql://root:root@db:3306/exercise_app"  
    )  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "db"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "exercise_app"),
        "port": int(os.getenv("DB_PORT", 3306)),
    }