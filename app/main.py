from flask import Flask
from flask_cors import CORS
from app.config import Config
from . import db, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins="http://localhost:5173", supports_credentials=True)

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from app.routes import register_routes

        register_routes(app)

    return app


app = create_app()
