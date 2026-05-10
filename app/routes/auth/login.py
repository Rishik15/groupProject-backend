import json
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import auth_bp
from app import bcrypt
from flask import session, request
from app.services import run_query
from app.services.auth.getUser import getUserCreds, getUserInfo
from app.services.auth.getUserRoles import getUserRoles
from app.services.auth.coachApplicationStatus import getCoachApplicationStatus
from app.sockets.notifications.notifications import send_notification


def get_valid_timezone(value: str | None) -> str:
    if not value:
        return "America/New_York"

    try:
        ZoneInfo(value)
        return value
    except ZoneInfoNotFoundError:
        return "America/New_York"


def get_user_today_and_utc_bounds(user_timezone: str):
    tz = ZoneInfo(user_timezone)

    today = datetime.now(tz).date()

    start_local = datetime.combine(today, time.min, tzinfo=tz)
    end_local = datetime.combine(today, time.max, tzinfo=tz)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

    return today, start_utc, end_utc


def has_completed_daily_survey_today(user_id: int, today):
    rows = run_query(
        """
        SELECT survey_id
        FROM mental_wellness_survey
        WHERE user_id = :user_id
          AND survey_date = :today
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "today": today,
        },
        fetch=True,
        commit=False,
    )

    return bool(rows)


def get_daily_survey_notification_today(user_id: int, start_utc, end_utc):
    rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
          AND mode = 'client'
          AND type = 'daily_survey'
          AND created_at >= :start_utc
          AND created_at <= :end_utc
        ORDER BY notification_id DESC
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "start_utc": start_utc,
            "end_utc": end_utc,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    return rows[0]


def clear_old_daily_survey_notifications(
    user_id: int, keep_notification_id: int | None = None
):
    params = {
        "user_id": user_id,
        "keep_notification_id": keep_notification_id,
    }

    if keep_notification_id:
        query = """
            UPDATE notification
            SET
                is_read = TRUE,
                updated_at = NOW()
            WHERE user_id = :user_id
              AND mode = 'client'
              AND type = 'daily_survey'
              AND notification_id != :keep_notification_id
        """
    else:
        query = """
            UPDATE notification
            SET
                is_read = TRUE,
                updated_at = NOW()
            WHERE user_id = :user_id
              AND mode = 'client'
              AND type = 'daily_survey'
        """

    run_query(
        query,
        params,
        fetch=False,
        commit=True,
    )


def update_daily_survey_notification(notification_id: int):
    metadata = {
        "route": "/client",
        "points": 100,
        "surveyType": "mental_wellness",
    }

    run_query(
        """
        UPDATE notification
        SET
            title = 'Complete your daily check-in',
            body = 'Complete today''s wellness survey and earn 100 points.',
            metadata = :metadata,
            is_read = FALSE,
            updated_at = NOW()
        WHERE notification_id = :notification_id
        """,
        {
            "notification_id": notification_id,
            "metadata": json.dumps(metadata),
        },
        fetch=False,
        commit=True,
    )


def maybe_send_daily_survey_notification(user_id: int, user_timezone: str):
    today, start_utc, end_utc = get_user_today_and_utc_bounds(user_timezone)

    if has_completed_daily_survey_today(user_id, today):
        clear_old_daily_survey_notifications(user_id)
        return

    existing_notification = get_daily_survey_notification_today(
        user_id,
        start_utc,
        end_utc,
    )

    if existing_notification:
        notification_id = existing_notification["notification_id"]

        update_daily_survey_notification(notification_id)
        clear_old_daily_survey_notifications(user_id, notification_id)

        return

    clear_old_daily_survey_notifications(user_id)

    send_notification(
        user_id=user_id,
        mode="client",
        notification_type="daily_survey",
        title="Complete your daily check-in",
        body="Complete today's wellness survey and earn 100 points.",
        route="/client",
        metadata={
            "points": 100,
            "surveyType": "mental_wellness",
        },
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login
    ---
    tags:
      - auth
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    user_timezone = get_valid_timezone(data.get("timezone"))

    user = getUserCreds(email)

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not bcrypt.check_password_hash(user["password_hash"], password):
        return {"error": "Invalid credentials"}, 401

    user_id = int(user["user_id"])

    roles = getUserRoles(user_id)
    user_info = getUserInfo(user_id)
    coach_application_status = getCoachApplicationStatus(user_id)

    session.permanent = True
    session["user_id"] = user_id
    session["role"] = user["role"]
    session["timezone"] = user_timezone

    maybe_send_daily_survey_notification(user_id, user_timezone)

    return {
        "success": True,
        "roles": roles,
        "user": user_info,
        "coach_application_status": coach_application_status,
        "timezone": user_timezone,
    }, 200
