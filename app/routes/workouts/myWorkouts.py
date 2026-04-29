from flask import session, jsonify
from app.services.workouts.my_Workouts import get_user_workouts
from . import workouts_bp

@workouts_bp.route("/my-workouts", methods=["GET"])
def my_workouts_route():
    """
Get user's workout plans
---
tags:
  - workouts
responses:
  200:
    description: List of workout plans
    schema:
      type: object
      properties:
        message:
          type: string
        workouts:
          type: array
          items:
            type: object
            properties:
              plan_id:
                type: integer
              plan_name:
                type: string
              description:
                type: string
              source:
                type: string
                enum:
                  - authored
                  - assigned
              total_exercises:
                type: integer
  401:
    description: Unauthorized
    """
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        plans = get_user_workouts(int(u_id))
        
        return jsonify({
            "message": "success",
            "workouts": plans
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500