from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Weekly_Calories import get_weekly_calories


@nutrition_bp.route("/getWeeklyCaloriesSummary", methods=["GET"])
def get_weekly_calories_summary_route():
    """
Get weekly calorie summary
---
tags:
  - nutrition
responses:
  200:
    description: Weekly calorie summary
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        result = get_weekly_calories(int(user_id))
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
