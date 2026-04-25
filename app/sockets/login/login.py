from flask_socketio import join_room, emit
from flask import session, request
from app import (
    online_users,
    socket_to_user,
    chat_online_users,
    user_active_conversation,
    socket_to_identity,
)
from app.services.chat.notify_users import notify_presence_change


VALID_MODES = {"client", "coach", "admin"}


def register_login_socket_events(socketio):

    @socketio.on("connect")
    def handle_connect():
        user_id = session.get("user_id")

        if not user_id:
            print("Socket rejected: no user session")
            return False

        socket_to_user[request.sid] = int(user_id)

    @socketio.on("register_mode")
    def register_mode(data):
        sid = request.sid
        user_id = socket_to_user.get(sid)
        mode = (data or {}).get("mode")

        if not user_id or mode not in VALID_MODES:
            print("Socket mode registration failed")
            emit(
                "mode_registration_failed",
                {"reason": "invalid_user_or_mode"},
                room=sid,
            )
            return

        old_identity = socket_to_identity.get(sid)
        new_identity = f"{user_id}:{mode}"

        if old_identity and old_identity != new_identity:
            if old_identity in online_users:
                online_users[old_identity].discard(sid)
                if not online_users[old_identity]:
                    online_users.pop(old_identity, None)

            if old_identity in chat_online_users:
                chat_online_users[old_identity].discard(sid)
                if not chat_online_users[old_identity]:
                    chat_online_users.pop(old_identity, None)

            user_active_conversation.pop(old_identity, None)

        socket_to_identity[sid] = new_identity
        join_room(new_identity)
        online_users.setdefault(new_identity, set()).add(sid)

        emit(
            "mode_registered",
            {
                "mode": mode,
                "identity": new_identity,
            },
            room=sid,
        )

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
                online_users.pop(identity, None)

        if identity in chat_online_users:
            chat_online_users[identity].discard(sid)
            if not chat_online_users[identity]:
                chat_online_users.pop(identity, None)
                notify_presence_change(int(user_id), mode, "chat_offline")

        user_active_conversation.pop(identity, None)

        socket_to_identity.pop(sid, None)
        socket_to_user.pop(sid, None)
