from flask import jsonify, session
from . import survey_bp
from app.services.survey.reward import reward_daily_survey


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@survey_bp.route("/daily/reward", methods=["POST"])
def reward_daily_survey_route():
    """
    Claim daily survey reward
    ---
    tags:
      - survey
    responses:
      200:
        description: Reward granted
      401:
        description: Unauthorized
    """
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        result = reward_daily_survey(
            user_id=int(user_id),
            user_timezone=_get_session_timezone(),
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "reward": result,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
