from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import client_bp
from app.services.client.check_Survey import check_survey_status_service
from flask import jsonify, session


def _get_session_timezone():
    user_timezone = session.get("timezone") or "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _get_today_for_user():
    user_timezone = _get_session_timezone()
    return datetime.now(ZoneInfo(user_timezone)).date().isoformat()


@client_bp.route("/mental-survey/check", methods=["GET"])
def check_survey():
    """
    Check if mental survey taken today
    ---
    tags:
      - client
    responses:
      200:
        description: Survey status
        schema:
          type: object
          properties:
            taken_today:
              type: boolean
      400:
        description: Missing user_id
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    today = _get_today_for_user()

    has_taken = check_survey_status_service(user_id, today)

    return jsonify({"taken_today": has_taken}), 200
