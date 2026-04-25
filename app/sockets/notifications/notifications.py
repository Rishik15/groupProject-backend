import json
from app import socketio
from app.services import run_query


def send_notification_to_user(
    user_id: int,
    mode: str,
    event: str,
    notification_type: str,
    title: str,
    body: str,
    metadata: dict | None = None,
    conversation_id=None,
    reference_id=None,
):
    metadata = metadata or {}

    run_query(
        """
        INSERT INTO notification
        (
            user_id,
            type,
            conversation_id,
            reference_id,
            metadata,
            title,
            body,
            is_read
        )
        VALUES
        (
            :user_id,
            :type,
            :conversation_id,
            :reference_id,
            :metadata,
            :title,
            :body,
            FALSE
        )
        """,
        {
            "user_id": user_id,
            "type": notification_type,
            "conversation_id": conversation_id,
            "reference_id": reference_id,
            "metadata": json.dumps(metadata),
            "title": title,
            "body": body,
        },
        fetch=False,
        commit=True,
    )

    result = run_query(
        """
        SELECT
            notification_id AS id,
            user_id,
            type,
            conversation_id AS conversationId,
            reference_id AS referenceId,
            metadata,
            title,
            body,
            is_read AS isRead,
            created_at AS createdAt,
            updated_at AS updatedAt
        FROM notification
        WHERE notification_id = LAST_INSERT_ID()
        """,
        fetch=True,
        commit=False,
    )

    notification = result[0] if result else None

    if notification and isinstance(notification.get("metadata"), str):
        try:
            notification["metadata"] = json.loads(notification["metadata"])
        except Exception:
            notification["metadata"] = {}

    room = f"{user_id}:{mode}"

    socketio.emit(
        event,
        {
            "notification": notification,
            "metadata": metadata,
        },
        room=room,
    )

    return notification
