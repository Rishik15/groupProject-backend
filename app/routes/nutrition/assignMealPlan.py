from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.assign_Meal_Plan import assign_meal_plan


@nutrition_bp.route("/meal-plans/assign", methods=["POST"])
def assign_meal_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data         = request.get_json()
    meal_plan_id = data.get("meal_plan_id")
    start_date   = data.get("start_date")
    force        = data.get("force", False)

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        new_plan_id = assign_meal_plan(user_id, meal_plan_id, start_date, force)
    except ValueError as e:
        error_str = str(e)
        if error_str.startswith("EXISTING_PLAN:"):
            existing_plan_name = error_str.split("EXISTING_PLAN:")[1]
            return jsonify({
                "error": "existing_plan",
                "existing_plan_name": existing_plan_name,
                "message": f"'{existing_plan_name}' is already assigned for this week. Send force=true to replace it."
            }), 409
        return jsonify({"error": error_str}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Meal plan assigned successfully",
        "meal_plan_id": new_plan_id
    }), 201