from . import workouts_bp
from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises
from flask import jsonify

@workouts_bp.route("/workout-plan/<int:plan_id>/exercises", methods=["GET"])
def get_plan_exercises(plan_id):
    try:
        exercises = get_workout_plan_exercises(plan_id)
        
        if not exercises:
            return jsonify({"message": "No exercises found for this plan", "exercises": []}), 200
            
        return jsonify({
            "plan_id": plan_id,
            "exercise_count": len(exercises),
            "exercises": exercises
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500