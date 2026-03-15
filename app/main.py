from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from . import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins="http://localhost:5173")

    db.init_app(
        app
    )  # This actually connects the mysql server to the backend and initializes the db object to actually manage our database.

    with app.app_context():
        from app.routes import register_routes

        register_routes(app)

    return app

app = create_app()

