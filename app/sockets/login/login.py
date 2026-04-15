from flask_socketio import emit, join_room
from flask import session, request
from app import online_users, socket_to_user


def register_login_socket_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        user_id = session.get("user_id")

        if not user_id:
            return False

        join_room(str(user_id))

        online_users[user_id] = request.sid
        socket_to_user[request.sid] = user_id

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid

        if sid in socket_to_user:
            user_id = socket_to_user[sid]

            del online_users[user_id]
            del socket_to_user[sid]

            print(f"{user_id} went offline")
