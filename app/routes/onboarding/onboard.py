from . import onboard_bp
from flask import jsonify, session, request
from datetime import date, datetime
from app.services.onboarding import onboardUser


def _parse_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(str(value).split("T")[0])
    except ValueError:
        try:
            return datetime.fromisoformat(str(value)).date()
        except ValueError:
            return None


@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():
    """
    Submit onboarding survey
    ---
    tags:
      - onboarding
    responses:
      200:
        description: Onboarding completed
      400:
        description: Missing required fields
      401:
        description: Unauthorized
    """
    try:
        data = request.get_json() or {}

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        dob_value = data.get("dob")
        dob = _parse_date(dob_value)

        weight = data.get("weight")
        height = data.get("height")
        goal_weight = (
            data.get("goal_weight") if data.get("goal_weight") is not None else weight
        )
        profile_picture = data.get("profile_picture")

        if weight is None or height is None or dob is None:
            return (
                jsonify({"error": "weight, height, and date of birth are required"}),
                400,
            )

        onboardUser.onboardClientSurvey(
            user_id=user_id,
            profile_picture=profile_picture,
            weight=weight,
            height=height,
            goal_weight=goal_weight,
            dob=dob,
        )

        return jsonify({"message": "Client onboarding completed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
