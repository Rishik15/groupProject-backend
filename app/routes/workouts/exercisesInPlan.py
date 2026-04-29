# app/routes/workouts/exercisesInPlan.py
from . import workouts_bp
from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises
from flask import jsonify, request

@workouts_bp.route("/workout-plan/exercises", methods=["GET"])
def get_plan_exercises():
    """
Get exercises in workout plan
---
tags:
  - workouts
parameters:
  - name: plan_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: List of exercises in plan
  400:
    description: Missing or invalid plan_id
"""
    plan_id = request.args.get('plan_id')
    
    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    try:
        # Convert to int since request.args returns strings
        exercises = get_workout_plan_exercises(int(plan_id))
        
        if not exercises:
            return jsonify({"message": "No exercises found for this plan", "exercises": []}), 200
            
        return jsonify({
            "plan_id": plan_id,
            "exercise_count": len(exercises),
            "exercises": exercises
        }), 200
    except ValueError:
        return jsonify({"error": "plan_id must be a number"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    