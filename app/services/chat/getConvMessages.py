from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def getConvMessages(conv_id, user_id, user_timezone: str | None = None):
    query = """
        SELECT 
            m.message_id,
            m.sender_user_id,
            m.content,
            m.sent_at
        FROM message m
        JOIN conversation_member cm
            ON cm.conversation_id = m.conversation_id
        WHERE m.conversation_id = :conv_id
        AND cm.user_id = :user_id
        AND m.deleted_at IS NULL
        ORDER BY m.sent_at ASC
    """

    result = run_query(
        query,
        {
            "conv_id": conv_id,
            "user_id": user_id,
        },
    )

    messages = []

    for row in result:
        messages.append(
            {
                "id": row["message_id"],
                "text": row["content"],
                "timestamp": _format_datetime(row["sent_at"], user_timezone),
                "type": (
                    "sent" if int(row["sender_user_id"]) == int(user_id) else "received"
                ),
            }
        )

    return messages
