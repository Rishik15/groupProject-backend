from flask import jsonify, session
from . import survey_bp
from app.services.survey.reward import reward_daily_survey


@survey_bp.route("/daily/reward", methods=["POST"])
def reward_daily_survey_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        result = reward_daily_survey(int(user_id))

        return jsonify({
            "message": "success",
            "reward": result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500