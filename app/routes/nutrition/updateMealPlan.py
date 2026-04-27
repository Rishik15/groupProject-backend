from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.update_Meal_Plan import update_meal_plan


@nutrition_bp.route("/meal-plans/update", methods=["PUT"])
def update_meal_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data            = request.get_json()
    meal_plan_id    = data.get("meal_plan_id")
    plan_name       = data.get("plan_name")
    start_date      = data.get("start_date")
    end_date        = data.get("end_date")
    add_meals       = data.get("add_meals")
    remove_meals    = data.get("remove_meals")
    update_servings = data.get("update_servings")

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        update_meal_plan(
            user_id=user_id,
            meal_plan_id=meal_plan_id,
            plan_name=plan_name,
            start_date=start_date,
            end_date=end_date,
            add_meals=add_meals,
            remove_meals=remove_meals,
            update_servings=update_servings
        )
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": f"Meal plan '{plan_name}' already exists"}), 409
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Meal plan updated successfully"}), 200