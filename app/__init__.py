from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()

online_users = {}
chat_online_users = {}
socket_to_user = {}
presence_subscribers = {}
socket_to_identity = {}
user_active_conversation = {}
