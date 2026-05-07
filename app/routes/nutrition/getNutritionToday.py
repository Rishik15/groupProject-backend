from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Nutrition_Today import get_nutrition_today


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@nutrition_bp.route("/getNutritionToday", methods=["GET"])
def get_nutrition_today_route():
    """
    Get today's nutrition summary
    ---
    tags:
      - nutrition
    responses:
      200:
        description: Daily nutrition summary
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        result = get_nutrition_today(
            user_id=int(user_id),
            user_timezone=_get_session_timezone(),
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
