from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Nutrition_Today import get_nutrition_today


@nutrition_bp.route("/getNutritionToday", methods=["GET"])
def get_nutrition_today_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        result = get_nutrition_today(int(user_id))
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
