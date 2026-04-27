from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.create_Meal_Plan import create_meal_plan


@nutrition_bp.route("/meal-plans/create", methods=["POST"])
def create_meal_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data       = request.get_json()
    plan_name  = data.get("plan_name")
    start_date = data.get("start_date")
    end_date   = data.get("end_date")
    meals      = data.get("meals", [])

    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400

    try:
        meal_plan_id = create_meal_plan(user_id, plan_name, meals, start_date, end_date)
    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": f"Meal plan '{plan_name}' already exists"}), 409
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Meal plan created successfully", "meal_plan_id": meal_plan_id}), 201