from flask_socketio import emit
from flask import request
from app import (
    chat_online_users,
    presence_subscribers,
    socket_to_identity,
    user_active_conversation,
)
from app.services.chat.notify_users import notify_presence_change
from app.services import run_query


def register_chat_socket_events(socketio):

    @socketio.on("join_chat_presence")
    def join_chat(data=None):
        identity = socket_to_identity.get(request.sid)

        print("JOIN CHAT PRESENCE")
        print("sid:", request.sid)
        print("identity:", identity)

        if not identity:
            print("NO IDENTITY → FAIL")
            return

        chat_online_users.setdefault(identity, set()).add(request.sid)

        print("CHAT ONLINE USERS:", chat_online_users)

        user_id, mode = identity.split(":")
        notify_presence_change(int(user_id), mode, "chat_online")

    @socketio.on("leave_chat_presence")
    def leave_chat(data=None):
        identity = socket_to_identity.get(request.sid)
        if not identity:
            return

        if identity in chat_online_users:
            chat_online_users[identity].discard(request.sid)

            if not chat_online_users[identity]:
                chat_online_users.pop(identity)

                user_id, mode = identity.split(":")
                notify_presence_change(int(user_id), mode, "chat_offline")

    @socketio.on("subscribe_presence")
    def handle_subscribe(data):
        watcher_identity = socket_to_identity.get(request.sid)

        print("SUBSCRIBE PRESENCE")
        print("watcher_identity:", watcher_identity)
        print("targets:", data.get("identities"))

        if not watcher_identity:
            print("NO WATCHER IDENTITY → FAIL")
            return

        target_identities = data.get("identities", [])

        # remove from all previous subscriptions
        for watchers in presence_subscribers.values():
            watchers.discard(watcher_identity)

        # add new subscriptions
        for target_identity in target_identities:
            presence_subscribers.setdefault(target_identity, set()).add(
                watcher_identity
            )

    @socketio.on("chat_selected")
    def handle_selected(data):
        identity = socket_to_identity.get(request.sid)
        if not identity:
            return

        conv_id = data.get("convId")
        if not conv_id:
            return

        user_id, _ = identity.split(":")
        user_id = int(user_id)

        user_active_conversation[identity] = conv_id

        # reset unread count
        run_query(
            """
            UPDATE conversation_member
            SET unread_count = 0
            WHERE conversation_id = :conv_id
            AND user_id = :user_id
            """,
            {"conv_id": conv_id, "user_id": user_id},
            fetch=False,
            commit=True,
        )

        # mark notifications read
        run_query(
            """
            UPDATE notification
            SET is_read = TRUE
            WHERE user_id = :user_id
            AND conversation_id = :conv_id
            AND is_read = FALSE
            """,
            {"user_id": user_id, "conv_id": conv_id},
            fetch=False,
            commit=True,
        )

        emit(
            "chat_notifications_cleared",
            {"conversationId": conv_id},
            room=identity,
        )

    @socketio.on("chat_deselected")
    def handle_deselected(data):
        identity = socket_to_identity.get(request.sid)
        if not identity:
            return

        user_active_conversation.pop(identity, None)
