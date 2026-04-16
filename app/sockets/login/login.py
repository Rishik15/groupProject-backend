from flask_socketio import emit, join_room
from flask import session, request
from app import (
    online_users,
    socket_to_user,
    chat_online_users,
    user_active_conversation,
)
from app.services.chat.notify_users import notify_presence_change


def register_login_socket_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        user_id = session.get("user_id")

        if not user_id:
            return False

        join_room(str(user_id))

        online_users.setdefault(user_id, set()).add(request.sid)
        socket_to_user[request.sid] = user_id

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid

        if sid not in socket_to_user:
            return "No Socket Connection found", 404

        user_id = socket_to_user[sid]

        if user_id in online_users:
            online_users[user_id].discard(sid)

            if not online_users[user_id]:
                online_users.pop(user_id)

        if user_id in chat_online_users:
            chat_online_users[user_id].discard(sid)

            if not chat_online_users[user_id]:
                chat_online_users.pop(user_id)

                notify_presence_change(user_id, "chat_offline")

        if user_id in user_active_conversation:
            user_active_conversation.pop(user_id)

        socket_to_user.pop(sid)
