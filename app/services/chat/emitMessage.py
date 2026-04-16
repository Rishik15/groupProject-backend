from flask_socketio import emit
from app import socketio, online_users, chat_online_users, user_active_conversation
from app.services import run_query


def handle_emit_message(message, sender_id, conv_id):
    recipients = run_query(
        """
        SELECT user_id 
        FROM conversation_member
        WHERE conversation_id = :conv_id
        AND user_id != :sender
        """,
        {"conv_id": conv_id, "sender": sender_id},
    )

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
                run_query(
                    """
                    INSERT INTO notification (user_id, type, conversation_id, title, body)
                    VALUES (:user_id, 'chat', :conv_id, 'New Message', :body)
                    """,
                    {
                        "user_id": user_id,
                        "conv_id": conv_id,
                        "body": message["content"][:100],
                    },
                    fetch=False,
                    commit=True,
                )

                socketio.emit(
                    "new_notification",
                    {},
                    room=str(user_id),
                )

            else:
                run_query(
                    """
                    INSERT INTO notification (user_id, type, conversation_id, title, body)
                    VALUES (:user_id, 'chat', :conv_id, 'New Message', :body)
                    """,
                    {
                        "user_id": user_id,
                        "conv_id": conv_id,
                        "body": message["content"][:100],
                    },
                    fetch=False,
                    commit=True,
                )
