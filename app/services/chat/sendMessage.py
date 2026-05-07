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


def addMessage(sender, conv_id, message, user_timezone: str | None = None):
    run_query(
        """
        INSERT INTO message (conversation_id, sender_user_id, content)
        VALUES (:conv_id, :sender, :message)
        """,
        {
            "conv_id": conv_id,
            "sender": sender,
            "message": message,
        },
        fetch=False,
        commit=True,
    )

    result = run_query(
        """
        SELECT message_id, conversation_id, sender_user_id, content, sent_at
        FROM message
        WHERE conversation_id = :conv_id
        ORDER BY sent_at DESC
        LIMIT 1
        """,
        {
            "conv_id": conv_id,
        },
    )

    msg = result[0] if result else None

    if msg:
        msg["sent_at"] = _format_datetime(msg["sent_at"], user_timezone)

    return msg
