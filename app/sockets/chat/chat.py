from flask_socketio import emit, join_room
from flask import session, request
from app import (
    chat_online_users,
    presence_subscribers,
    socket_to_user,
    user_active_conversation,
)
from app.services.chat.notify_users import notify_presence_change


def register_chat_socket_events(socketio):
    @socketio.on("join_chat_presence")
    def join_chat():
        sid = request.sid
        user_id = socket_to_user.get(sid)
        if not user_id:
            return
        chat_online_users.setdefault(user_id, set()).add(sid)

        notify_presence_change(user_id, "chat_online")

    @socketio.on("leave_chat_presence")
    def leave_chat():

        sid = request.sid
        user_id = socket_to_user[sid]
        if user_id in chat_online_users:
            chat_online_users[user_id].discard(sid)

            if not chat_online_users[user_id]:
                chat_online_users.pop(user_id)

                notify_presence_change(user_id, "chat_offline")

    @socketio.on("subscribe_presence")
    def handle_subscribe(data):
        user_id = socket_to_user[request.sid]

        user_ids = data.get("userIds", [])

        for target_id in user_ids:
            presence_subscribers.setdefault(target_id, set()).add(user_id)

    @socketio.on("chat_selected")
    def handle_selected(data):
        user_id = session.get("user_id")
        conv_id = data.get("convId")

        user_active_conversation[user_id] = conv_id

    @socketio.on("chat_deselected")
    def handle_deselected(data):
        user_id = session.get("user_id")

        if user_id in user_active_conversation:
            user_active_conversation.pop(user_id)
