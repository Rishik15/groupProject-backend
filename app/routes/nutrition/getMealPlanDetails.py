from flask import jsonify, request
from . import nutrition_bp
from app.services.nutrition.get_Meal_Plan_Details import get_meal_plan_detail


@nutrition_bp.route("/meal-plans/detail", methods=["POST"])
def meal_plan_detail_route():
    """
Get meal plan details
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
    description: Meal plan details
    schema:
      type: object
      properties:
        meal_plan_id:
          type: integer
        plan_name:
          type: string
        total_calories:
          type: integer
        meals:
          type: array
          items:
            type: object
            properties:
              meal_id:
                type: integer
              name:
                type: string
              calories:
                type: number
              protein:
                type: number
              carbs:
                type: number
              fats:
                type: number
              meal_type:
                type: string
              day_of_week:
                type: string
              servings:
                type: number
  400:
    description: Missing meal_plan_id
  404:
    description: Meal plan not found
    """
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