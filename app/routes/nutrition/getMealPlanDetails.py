from flask import jsonify, request
from . import nutrition_bp
from app.services.nutrition.get_Meal_Plan_Details import get_meal_plan_detail


@nutrition_bp.route("/meal-plans/detail", methods=["POST"])
def meal_plan_detail_route():
    data = request.get_json()
    plan_id = data.get("meal_plan_id")

    if not plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        detail = get_meal_plan_detail(int(plan_id))
        if not detail:
            return jsonify({"error": "Meal plan not found"}), 404
        return jsonify(detail), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500