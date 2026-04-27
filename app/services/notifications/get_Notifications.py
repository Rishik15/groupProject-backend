import json
from datetime import date, datetime, time

from app.services import run_query


def parse_metadata(metadata):
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


def make_json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    return value


def get_user_notifications(user_id: int, mode: str):
    result = run_query(
        """
        SELECT 
            notification_id AS id,
            user_id,
            type,
            mode,
            conversation_id,
            reference_id,
            metadata,
            title,
            body,
            is_read,
            created_at,
            updated_at
        FROM notification
        WHERE user_id = :user_id
        AND is_read = FALSE
        AND mode = :mode
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 50
        """,
        {
            "user_id": user_id,
            "mode": mode,
        },
        fetch=True,
        commit=False,
    )

    return [
        {
            "id": row["id"],
            "userId": row["user_id"],
            "type": row["type"],
            "mode": row["mode"],
            "conversationId": row["conversation_id"],
            "referenceId": row["reference_id"],
            "metadata": parse_metadata(row.get("metadata")),
            "title": row["title"],
            "body": row["body"],
            "isRead": bool(row["is_read"]),
            "createdAt": make_json_safe(row.get("created_at")),
            "updatedAt": make_json_safe(row.get("updated_at")),
        }
        for row in result
    ]
