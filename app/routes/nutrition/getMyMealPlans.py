from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_My_Meal_Plans import get_my_meal_plans


@nutrition_bp.route("/meal-plans/my-plans", methods=["GET"])
def get_my_meal_plans_route():
    """
Get user's meal plans
---
tags:
  - nutrition
responses:
  200:
    description: List of user meal plans
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    plans = get_my_meal_plans(user_id)
    return jsonify(plans), 200
