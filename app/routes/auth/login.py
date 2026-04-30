from . import auth_bp
from app import bcrypt
from flask import session, request
from app.services import run_query
from app.services.auth.getUser import getUserCreds, getUserInfo
from app.services.auth.getUserRoles import getUserRoles
from app.services.auth.coachApplicationStatus import getCoachApplicationStatus
from app.sockets.notifications.notifications import send_notification


def has_completed_daily_survey_today(user_id: int):
    rows = run_query(
        """
        SELECT survey_id
        FROM mental_wellness_survey
        WHERE user_id = :user_id
        AND survey_date = CURDATE()
        LIMIT 1
        """,
        {
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    return bool(rows)


def get_daily_survey_notification_today(user_id: int):
    rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
        AND mode = 'client'
        AND type = 'daily_survey'
        AND DATE(created_at) = CURDATE()
        ORDER BY notification_id DESC
        LIMIT 1
        """,
        {
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    return rows[0]


def update_daily_survey_notification(notification_id: int):
    run_query(
        """
        UPDATE notification
        SET
            title = 'Complete your daily check-in',
            body = 'Complete today''s wellness survey and earn 100 points.',
            is_read = FALSE,
            updated_at = NOW()
        WHERE notification_id = :notification_id
        """,
        {
            "notification_id": notification_id,
        },
        fetch=False,
        commit=True,
    )


def maybe_send_daily_survey_notification(user_id: int):
    if has_completed_daily_survey_today(user_id):
        return

    existing_notification = get_daily_survey_notification_today(user_id)

    if existing_notification:
        update_daily_survey_notification(existing_notification["notification_id"])
        return

    send_notification(
        user_id=user_id,
        mode="client",
        notification_type="daily_survey",
        title="Complete your daily check-in",
        body="Complete today's wellness survey and earn 100 points.",
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

    maybe_send_daily_survey_notification(user_id)

    return {
        "success": True,
        "roles": roles,
        "user": user_info,
        "coach_application_status": coach_application_status,
    }, 200
