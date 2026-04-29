from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.delete_Meal_Plan import delete_meal_plan


@nutrition_bp.route("/meal-plans/delete", methods=["DELETE"])
def delete_meal_plan_route():
    """
Delete meal plan
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
responses:
  200:
    description: Meal plan deleted
  400:
    description: Missing meal_plan_id
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    meal_plan_id = request.args.get("meal_plan_id", type=int) or data.get(
        "meal_plan_id"
    )

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    try:
        delete_meal_plan(int(user_id), int(meal_plan_id))

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Meal plan deleted successfully"}), 200
