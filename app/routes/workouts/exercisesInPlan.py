from . import workouts_bp
from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises
from flask import jsonify, request


@workouts_bp.route("/workout-plan/exercises", methods=["GET"])
def get_plan_exercises():
    """
    Get exercises in workout plan grouped by workout days
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
        description: Workout plan days with exercises
      400:
        description: Missing or invalid plan_id
    """
    plan_id = request.args.get("plan_id", type=int)

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    try:
        days = get_workout_plan_exercises(plan_id)

        exercise_count = sum(len(day["exercises"]) for day in days)

        return (
            jsonify(
                {
                    "message": "success",
                    "plan_id": plan_id,
                    "day_count": len(days),
                    "exercise_count": exercise_count,
                    "days": days,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
