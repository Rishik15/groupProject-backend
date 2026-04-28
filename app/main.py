import os

from flask import Flask, abort, send_from_directory, jsonify
from flask_cors import CORS

from app.config import Config
from . import db, bcrypt
from . import socketio

from flasgger import Swagger

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(Config)
    CORS(app, origins="http://localhost:5173", supports_credentials=True)

    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    os.makedirs(app.config["MEDIA_ROOT"], exist_ok=True)

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

    with app.app_context():
        from app.routes import register_routes
        register_routes(app)

        from app.sockets import register_socket_events

        register_socket_events(socketio)
    
    @app.route("/openapi.json", methods=["GET"])
    def openapi_json():
        return send_from_directory(
            os.path.join(app.root_path, "..", "documentation"),
            "openapi.json",
        )
    Swagger(app) 

    return app

app = create_app()

