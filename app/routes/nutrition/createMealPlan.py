from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.create_Meal_Plan import create_meal_plan


@nutrition_bp.route("/meal-plans/create", methods=["POST"])
def create_meal_plan_route():
    """
Create a meal plan
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
        - plan_name
      properties:
        plan_name:
          type: string
        start_date:
          type: string
          format: date
        end_date:
          type: string
          format: date
        meals:
          type: array
          items:
            type: object
            required:
              - meal_id
              - day_of_week
              - meal_type
            properties:
              meal_id:
                type: integer
              day_of_week:
                type: string
              meal_type:
                type: string
                enum:
                  - breakfast
                  - lunch
                  - dinner
                  - snack
              servings:
                type: number
responses:
  201:
    description: Meal plan created
    schema:
      type: object
      properties:
        message:
          type: string
        meal_plan_id:
          type: integer
  400:
    description: Invalid input
  409:
    description: Duplicate plan
  401:
    description: Unauthorized
    """
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