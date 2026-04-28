from flask import jsonify
from . import nutrition_bp
from app.services.nutrition.get_Meal_Plans import get_meal_plan_library


@nutrition_bp.route("/meal-plans", methods=["GET"])
def meal_plans_route():
    try:
        plans = get_meal_plan_library()
        return jsonify({"meal_plans": plans}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500