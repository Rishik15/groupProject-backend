from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="http://localhost:5173") 

online_users = {}      
chat_online_users = {}   
socket_to_user = {}
presence_subscribers = {}
user_active_conversation = {}