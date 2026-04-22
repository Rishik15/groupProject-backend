from flask import jsonify, request, session
from . import nutrition_bp
from app.services.nutrition.assign_Meal_Plan import assign_meal_plan


@nutrition_bp.route("/meal-plans/assign", methods=["POST"])
def assign_meal_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    plan_id = data.get("meal_plan_id")

    if not plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        assign_meal_plan(user_id=int(user_id), plan_id=int(plan_id))
        return jsonify({"message": "Meal plan assigned successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500