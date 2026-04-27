from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Meals import get_meals


@nutrition_bp.route("/meals", methods=["GET"])
def get_meals_route():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    meals = get_meals()
    return jsonify(meals), 200