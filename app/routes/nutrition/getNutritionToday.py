from flask import jsonify, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.get_Nutrition_Today import get_nutrition_today


@nutrition_bp.route("/getNutritionToday", methods=["GET"])
def get_nutrition_today_route():
    """
Get today's nutrition summary
---
tags:
  - nutrition
responses:
  200:
    description: Daily nutrition summary
    schema:
      type: object
      properties:
        message:
          type: string
        calories:
          type: object
          properties:
            current:
              type: number
            goal:
              type: number
        macros:
          type: object
          properties:
            protein:
              type: object
              properties:
                current:
                  type: number
                goal:
                  type: number
            carbs:
              type: object
              properties:
                current:
                  type: number
                goal:
                  type: number
            fats:
              type: object
              properties:
                current:
                  type: number
                goal:
                  type: number
        meals:
          type: array
          items:
            type: object
            properties:
              log_id:
                type: integer
              meal_name:
                type: string
              meal_type:
                type: string
              eaten_at:
                type: string
                format: date-time
              time_label:
                type: string
              servings:
                type: number
              notes:
                type: string
              photo_url:
                type: string
              calories:
                type: number
              protein:
                type: number
              carbs:
                type: number
              fats:
                type: number
  401:
    description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        result = get_nutrition_today(int(user_id))
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
