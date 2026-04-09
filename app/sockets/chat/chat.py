from flask_socketio import emit, join_room
from flask import session, request
from app import chat_online_users, presence_subscribers
from app.services.chat.notify_users import notify_presence_change


def register_chat_socket_events(socketio):
    @socketio.on("join_chat_presence")
    def join_chat():
        user_id = session.get("user_id")
        sid = request.sid

        chat_online_users.setdefault(user_id, set()).add(sid)

        notify_presence_change(user_id, "chat_online")

    @socketio.on("leave_chat_presence")
    def leave_chat():
        user_id = session.get("user_id")
        sid = request.sid

        if user_id in chat_online_users:
            chat_online_users[user_id].discard(sid)

            if not chat_online_users[user_id]:
                chat_online_users.pop(user_id)

                notify_presence_change(user_id, "chat_offline")


    @socketio.on("subscribe_presence")
    def handle_subscribe(data):
        user_id = session.get("user_id")
        print("SUBSCRIBE CALLED:", user_id, data)

        user_ids = data.get("userIds", [])

        for target_id in user_ids:
            presence_subscribers.setdefault(target_id, set()).add(user_id)

        print("UPDATED SUBSCRIBERS:", presence_subscribers)
