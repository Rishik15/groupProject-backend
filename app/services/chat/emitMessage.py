from flask_socketio import emit
from app import socketio, online_users, chat_online_users, user_active_conversation
from app.services import run_query
from datetime import datetime
from app.services.chat.handleChatNotification import handle_chat_notification


def handle_emit_message(message, sender_id, conv_id):

    if message and isinstance(message.get("sent_at"), datetime):
        message["sent_at"] = message["sent_at"].isoformat()

    recipients = run_query(
        """
        SELECT user_id 
        FROM conversation_member
        WHERE conversation_id = :conv_id
        AND user_id != :sender
        """,
        {"conv_id": conv_id, "sender": sender_id},
    )

    sender = run_query(
        """
    SELECT first_name, last_name
    FROM users_immutables
    WHERE user_id = :sender_id
    """,
        {"sender_id": sender_id},
    )[0]

    sender_name = f"{sender['first_name']} {sender['last_name']}"

    for row in recipients:
        user_id = row["user_id"]

        is_viewing = user_active_conversation.get(user_id) == conv_id
        is_chat_online = user_id in chat_online_users
        is_online = user_id in online_users

        if is_viewing:
            socketio.emit("new_message", message, room=str(user_id))
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
            user_id, conv_id, sender_name, message
        )

        if is_chat_online:
            socketio.emit(
                "conversation_update",
                {
                    "conversationId": conv_id,
                    "message": message,
                },
                room=str(user_id),
            )

        elif is_online:
            socketio.emit(
                "update_notification" if is_updated else "new_notification",
                notif_payload,
                room=str(user_id),
            )
