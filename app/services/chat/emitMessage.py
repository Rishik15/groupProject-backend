from app import socketio, online_users, chat_online_users, user_active_conversation
from app.services import run_query
from datetime import datetime
from app.services.chat.handleChatNotification import handle_chat_notification


def handle_emit_message(message, sender_id, conv_id, sender_identity):

    if message and isinstance(message.get("sent_at"), datetime):
        message["sent_at"] = message["sent_at"].isoformat()

    sender_user_id, sender_mode = sender_identity.split(":")
    sender_user_id = int(sender_user_id)

    receiver_mode = "client" if sender_mode == "coach" else "coach"

    recipients = run_query(
        """
        SELECT user_id
        FROM conversation_member
        WHERE conversation_id = :conv_id
        AND user_id != :sender
        """,
        {"conv_id": conv_id, "sender": sender_user_id},
    )

    sender = run_query(
        """
        SELECT first_name, last_name
        FROM users_immutables
        WHERE user_id = :sender_id
        """,
        {"sender_id": sender_user_id},
    )[0]

    sender_name = f"{sender['first_name']} {sender['last_name']}"

    for row in recipients:
        user_id = row["user_id"]

        target_identity = f"{user_id}:{receiver_mode}"

        is_viewing = user_active_conversation.get(target_identity) == conv_id
        is_chat_online = target_identity in chat_online_users
        is_online = target_identity in online_users and online_users[target_identity]

        if is_viewing:
            socketio.emit("new_message", message, room=target_identity)
            continue

        run_query(
            """
            UPDATE conversation_member
            SET unread_count = unread_count + 1
            WHERE conversation_id = :conv_id
            AND user_id = :user_id
            """,
            {"conv_id": conv_id, "user_id": user_id},
            fetch=False,
            commit=True,
        )

        notif_payload, is_updated = handle_chat_notification(
            user_id, conv_id, sender_name, message, receiver_mode
        )

        if is_chat_online:
            socketio.emit(
                "conversation_update",
                {
                    "conversationId": conv_id,
                    "message": message,
                },
                room=target_identity,
            )

        elif is_online:
            socketio.emit(
                "update_notification" if is_updated else "new_notification",
                notif_payload,
                room=target_identity,
            )
