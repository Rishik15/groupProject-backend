from app.services import run_query
import json


def handle_chat_notification(user_id, conv_id, sender_name, message):
    existing = run_query(
        """
        SELECT notification_id AS id
        FROM notification
        WHERE user_id = :user_id
        AND conversation_id = :conv_id
        AND type = 'chat'
        AND is_read = FALSE
        LIMIT 1
        """,
        {"user_id": user_id, "conv_id": conv_id},
    )

    title = sender_name
    body = message.get("content") or message.get("text", "")[:100]
    metadata = json.dumps({"sender_name": sender_name})

    if existing:
        notif_id = existing[0]["id"]

        run_query(
            """
            UPDATE notification
            SET 
                title = :title,
                body = :body,
                metadata = :metadata,
                updated_at = NOW()
            WHERE notification_id = :id
            """,
            {
                "id": notif_id,
                "title": title,
                "body": body,
                "metadata": metadata,
            },
            fetch=False,
            commit=True,
        )

        return {
            "id": notif_id,
            "type": "chat",
            "conversationId": conv_id,
            "title": title,
            "body": body,
            "is_read": False,
        }, True  # updated

    else:
        run_query(
            """
            INSERT INTO notification (user_id, type, conversation_id, title, body, metadata)
            VALUES (:user_id, 'chat', :conv_id, :title, :body, :metadata)
            """,
            {
                "user_id": user_id,
                "conv_id": conv_id,
                "title": title,
                "body": body,
                "metadata": metadata,
            },
            fetch=False,
            commit=True,
        )

        notif_id = run_query("SELECT LAST_INSERT_ID() AS id", {})[0]["id"]

        return {
            "id": notif_id,
            "type": "chat",
            "conversationId": conv_id,
            "title": title,
            "body": body,
            "is_read": False,
        }, False  # new
