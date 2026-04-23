from flask_socketio import join_room
from flask import session, request
from app import (
    online_users,
    socket_to_user,
    chat_online_users,
    user_active_conversation,
    socket_to_identity,
)
from app.services.chat.notify_users import notify_presence_change


def register_login_socket_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        user_id = session.get("user_id")

        print("CONNECT EVENT")
        print("session user_id:", user_id)
        print("sid:", request.sid)

        if not user_id:
            print("NO USER ID → REJECT")
            return False

        socket_to_user[request.sid] = user_id

    @socketio.on("register_mode")
    def register_mode(data):
        sid = request.sid
        user_id = socket_to_user.get(sid)
        mode = data.get("mode")

        print("REGISTER MODE EVENT")
        print("sid:", sid)
        print("user_id:", user_id)
        print("mode:", mode)

        if not user_id or mode not in ["client", "coach", "admin"]:
            print("REGISTER MODE FAILED")
            return

        identity = f"{user_id}:{mode}"

        print("REGISTERED IDENTITY:", identity)

        socket_to_identity[sid] = identity
        join_room(identity)
        online_users.setdefault(identity, set()).add(sid)

        print("ONLINE USERS:", online_users)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid

        identity = socket_to_identity.get(sid)
        if not identity:
            socket_to_user.pop(sid, None)
            return

        user_id, mode = identity.split(":")

        if identity in online_users:
            online_users[identity].discard(sid)
            if not online_users[identity]:
                online_users.pop(identity)

        if identity in chat_online_users:
            chat_online_users[identity].discard(sid)
            if not chat_online_users[identity]:
                chat_online_users.pop(identity)
                notify_presence_change(int(user_id), mode, "chat_offline")

        if identity in user_active_conversation:
            user_active_conversation.pop(identity, None)

        socket_to_identity.pop(sid, None)
        socket_to_user.pop(sid, None)
