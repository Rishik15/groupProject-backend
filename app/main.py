from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from . import db, bcrypt
from . import socketio


def create_app():
    app = Flask(__name__, static_folder='../static')    
    app.config.from_object(Config)
    CORS(app, origins="http://localhost:5173", supports_credentials=True)

    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from app.routes import register_routes

        register_routes(app)

        from app.sockets import register_socket_events

        register_socket_events(socketio)

    return app


app = create_app()
