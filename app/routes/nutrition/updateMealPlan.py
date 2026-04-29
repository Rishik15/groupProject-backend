from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.update_Meal_Plan import update_meal_plan


@nutrition_bp.route("/meal-plans/update", methods=["PUT"])
def update_meal_plan_route():
    """
Update meal plan
---
tags:
  - nutrition
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - meal_plan_id
      properties:
        meal_plan_id:
          type: integer
        plan_name:
          type: string
        start_date:
          type: string
        end_date:
          type: string
        add_meals:
          type: array
        remove_meals:
          type: array
        update_servings:
          type: array
responses:
  200:
    description: Meal plan updated
  400:
    description: Invalid input
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}

    meal_plan_id = data.get("meal_plan_id")

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        result = update_meal_plan(
            user_id=int(user_id),
            meal_plan_id=int(meal_plan_id),
            plan_name=data.get("plan_name"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            add_meals=data.get("add_meals", []),
            remove_meals=data.get("remove_meals", []),
            update_servings=data.get("update_servings", []),
        )

        return (
            jsonify(
                {
                    "message": "Meal plan updated successfully",
                    "meal_plan_id": result["meal_plan_id"],
                    "total_calories": result["total_calories"],
                    "deleted": result["deleted"],
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "A meal plan with this name already exists"}), 409

        return jsonify({"error": str(e)}), 500
