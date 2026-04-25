import json
from app import socketio
from app.services import run_query


def _parse_metadata(metadata):
    if not metadata:
        return {}

    if isinstance(metadata, dict):
        return metadata

    if isinstance(metadata, str):
        try:
            return json.loads(metadata)
        except Exception:
            return {}

    return {}


def send_notification(
    user_id: int,
    mode: str,
    notification_type: str,
    title: str,
    body: str,
    route: str | None = None,
    metadata: dict | None = None,
    reference_id=None,
    conversation_id=None,
    extra_event: str | None = None,
    extra_payload: dict | None = None,
):
    metadata = metadata or {}

    if route:
        metadata["route"] = route

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

    rows = run_query(
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

    notification = rows[0] if rows else None

    if notification:
        notification["metadata"] = _parse_metadata(notification.get("metadata"))

    room = f"{user_id}:{mode}"

    socketio.emit("new_notification", notification, room=room)

    if extra_event:
        socketio.emit(extra_event, extra_payload or {}, room=room)

    return notification


def clear_notification(
    user_id: int,
    mode: str,
    notification_id: int,
):
    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE notification_id = :notification_id
        AND user_id = :user_id
        """,
        {
            "notification_id": notification_id,
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )

    room = f"{user_id}:{mode}"

    socketio.emit(
        "clear_notification",
        {
            "id": notification_id,
            "notification_id": notification_id,
        },
        room=room,
    )

    return True


def clear_notifications_by_type(
    user_id: int,
    mode: str,
    notification_type: str,
):
    rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
        AND type = :type
        AND is_read = FALSE
        """,
        {
            "user_id": user_id,
            "type": notification_type,
        },
        fetch=True,
        commit=False,
    )

    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE user_id = :user_id
        AND type = :type
        """,
        {
            "user_id": user_id,
            "type": notification_type,
        },
        fetch=False,
        commit=True,
    )

    room = f"{user_id}:{mode}"

    socketio.emit(
        "clear_notifications",
        {
            "ids": [row["notification_id"] for row in rows],
            "type": notification_type,
        },
        room=room,
    )

    return True
