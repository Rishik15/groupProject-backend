from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Todays_Meals import get_todays_meals


@nutrition_bp.route("/meal-plans/today", methods=["POST"])
def get_todays_meals_route():
    """
Get today's meals from plan
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
    description: Today's meals
  400:
    description: Missing meal_plan_id
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data         = request.get_json()
    meal_plan_id = data.get("meal_plan_id")

    if not meal_plan_id:
        return jsonify({"error": "meal_plan_id is required"}), 400

    meals = get_todays_meals(user_id, meal_plan_id)
    return jsonify(meals), 200