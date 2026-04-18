from app.services import run_query


def get_user_notifications(user_id: int):
    result = run_query(
        """
    SELECT 
        notification_id AS id,
        type,
        conversation_id,
        title,
        body,
        is_read,
        created_at
    FROM notification
    WHERE user_id = :user_id
    AND is_read = FALSE
    ORDER BY created_at DESC
    LIMIT 50
    """,
        {"user_id": user_id},
    )

    notifications = []

    for row in result:
        notifications.append(
            {
                "id": row["id"],
                "type": row["type"],
                "conversationId": row["conversation_id"],
                "title": row["title"],
                "body": row["body"],
                "is_read": row["is_read"],
            }
        )

    return notifications
