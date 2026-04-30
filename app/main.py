import os

from flask import Flask, abort, send_from_directory, jsonify
from flask_cors import CORS
from flasgger import Swagger
from sqlalchemy import text

from app.config import Config
from . import db, bcrypt, socketio


def ping_database(app):
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("Database connected successfully")
            return True

        except Exception as e:
            db.session.rollback()
            print("Database connection failed")
            print(str(e))
            return False


def create_app():
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(Config)

    CORS(
        app,
        origins=app.config["CORS_ORIGIN"],
        supports_credentials=True,
    )

    db.init_app(app)
    bcrypt.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGIN"],
    )

    os.makedirs(app.config["MEDIA_ROOT"], exist_ok=True)

    ping_database(app)

    @app.route("/health/db", methods=["GET"])
    def database_health_check():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify({"status": "ok", "database": "connected"}), 200

        except Exception as e:
            db.session.rollback()

            return (
                jsonify(
                    {"status": "error", "database": "not connected", "error": str(e)}
                ),
                500,
            )

    @app.route("/uploads/<path:relative_path>", methods=["GET"])
    def serve_uploaded_file(relative_path):
        media_root = os.path.abspath(app.config["MEDIA_ROOT"])
        requested_path = os.path.abspath(os.path.join(media_root, relative_path))

        if not requested_path.startswith(media_root + os.sep):
            abort(404)

        if not os.path.isfile(requested_path):
            abort(404)

        directory = os.path.dirname(requested_path)
        filename = os.path.basename(requested_path)

        return send_from_directory(directory, filename)

    @app.route("/openapi.json", methods=["GET"])
    def openapi_json():
        return send_from_directory(
            os.path.join(app.root_path, "..", "documentation"),
            "openapi.json",
        )

    with app.app_context():
        from app.routes import register_routes
        from app.sockets import register_socket_events

        register_routes(app)
        register_socket_events(socketio)

    Swagger(app)

    return app


app = create_app()
