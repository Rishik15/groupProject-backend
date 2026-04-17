from flask_socketio import emit
from app import socketio, online_users, chat_online_users, user_active_conversation
from app.services import run_query
from datetime import datetime
import json


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
            socketio.emit(
                "new_message",
                message,
                room=str(user_id),
            )

        else:
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

            run_query(
                """
                    INSERT INTO notification (user_id, type, conversation_id, title, body, metadata)
                    VALUES (:user_id, 'chat', :conv_id, :title, :body, :metadata)
                    """,
                {
                    "user_id": user_id,
                    "conv_id": conv_id,
                    "title": sender_name,
                    "body": message["content"][:100],
                    "metadata": json.dumps({"sender_name": sender_name}),
                },
                fetch=False,
                commit=True,
            )

            notif_id = run_query(
                "SELECT LAST_INSERT_ID() AS id",
                {},
            )[
                0
            ]["id"]

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
                    "new_notification",
                    {
                        "id": notif_id,
                        "type": "chat",
                        "conversationId": conv_id,
                        "title": f"{sender_name} sent a message",
                        "body": message["content"][:100],
                        "is_read": False,
                    },
                    room=str(user_id),
                )
