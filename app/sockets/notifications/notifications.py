import json
from datetime import date, datetime

from app import socketio, online_users
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


def _serialize_notification(notification):
    if not notification:
        return None

    cleaned = {}

    for key, value in notification.items():
        if isinstance(value, (datetime, date)):
            cleaned[key] = value.isoformat()
        else:
            cleaned[key] = value

    cleaned["metadata"] = _parse_metadata(cleaned.get("metadata"))

    return cleaned


def _is_user_online_in_mode(user_id: int, mode: str):
    target_identity = f"{user_id}:{mode}"

    return (
        target_identity,
        target_identity in online_users and online_users[target_identity],
    )


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

    if mode not in ["client", "coach"]:
        raise ValueError("mode must be client or coach")

    if route:
        metadata["route"] = route

    run_query(
        """
        INSERT INTO notification
        (
            user_id,
            type,
            mode,
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
            :mode,
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
            "mode": mode,
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
            user_id AS userId,
            type,
            mode,
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

    notification = _serialize_notification(rows[0]) if rows else None

    target_identity, is_online = _is_user_online_in_mode(user_id, mode)

    print("NOTIFICATION CREATED:", notification)
    print("TARGET IDENTITY:", target_identity)
    print("IS ONLINE:", is_online)

    if is_online and notification:
        socketio.emit(
            "new_notification",
            notification,
            room=target_identity,
        )

        if extra_event:
            print("SENDING EXTRA EVENT:", extra_event, extra_payload)
            socketio.emit(
                extra_event,
                extra_payload or {},
                room=target_identity,
            )

    return notification


def clear_notification(
    user_id: int,
    mode: str,
    notification_id: int,
):
    if mode not in ["client", "coach"]:
        raise ValueError("mode must be client or coach")

    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE notification_id = :notification_id
        AND user_id = :user_id
        AND mode = :mode
        """,
        {
            "notification_id": notification_id,
            "user_id": user_id,
            "mode": mode,
        },
        fetch=False,
        commit=True,
    )

    target_identity, is_online = _is_user_online_in_mode(user_id, mode)

    print("CLEAR NOTIFICATION:", notification_id)
    print("TARGET IDENTITY:", target_identity)
    print("IS ONLINE:", is_online)

    if is_online:
        socketio.emit(
            "clear_notification",
            {
                "id": notification_id,
                "notification_id": notification_id,
            },
            room=target_identity,
        )

    return True


def clear_notifications_by_type(
    user_id: int,
    mode: str,
    notification_type: str,
):
    if mode not in ["client", "coach"]:
        raise ValueError("mode must be client or coach")

    rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
        AND type = :type
        AND mode = :mode
        AND is_read = FALSE
        """,
        {
            "user_id": user_id,
            "type": notification_type,
            "mode": mode,
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
        AND mode = :mode
        """,
        {
            "user_id": user_id,
            "type": notification_type,
            "mode": mode,
        },
        fetch=False,
        commit=True,
    )

    ids = [row["notification_id"] for row in rows]

    target_identity, is_online = _is_user_online_in_mode(user_id, mode)

    print("CLEAR NOTIFICATIONS BY TYPE:", notification_type)
    print("IDS:", ids)
    print("TARGET IDENTITY:", target_identity)
    print("IS ONLINE:", is_online)

    if is_online:
        socketio.emit(
            "clear_notifications",
            {
                "ids": ids,
                "type": notification_type,
            },
            room=target_identity,
        )

    return True
