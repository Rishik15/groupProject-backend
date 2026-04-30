from flask import jsonify
from . import nutrition_bp
from app.services.nutrition.get_Meal_Plans import get_meal_plan_library


@nutrition_bp.route("/meal-plans", methods=["GET"])
def meal_plans_route():
    """
Get meal plan library
---
tags:
  - nutrition
responses:
  200:
    description: List of system meal plans
    schema:
      type: object
      properties:
        meal_plans:
          type: array
          items:
            type: object
            properties:
              meal_plan_id:
                type: integer
              plan_name:
                type: string
              total_calories:
                type: integer
    """
    try:
        plans = get_meal_plan_library()
        return jsonify({"meal_plans": plans}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500