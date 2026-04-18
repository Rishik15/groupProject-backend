from flask import jsonify, request, session
from . import workouts_bp
from app.services.workouts.createWorkout_Plan import create_workout_plan
from app.services.workouts.checkForDuplicate import get_plan_conflict

@workouts_bp.route("/create", methods=["POST"])
def create_workout_plan_route():
    data = request.get_json()
    plan_name = data.get("name")
    exercises = data.get("exercises", [])
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400
    if not exercises:
        return jsonify({"error": "At least one exercise is required"}), 400

    try:
        conflict = get_plan_conflict(user_id, exercises, plan_name)

        if conflict == "name":
            return jsonify({"error": "You already have a plan with this name."}), 409

        if conflict == "structure":
            return jsonify({"error": "You already have a plan with these exact exercises and goals."}), 409

        description = f"Custom plan created for user {user_id}"
        new_plan_id = create_workout_plan(user_id, plan_name, exercises, description)

        return jsonify({
            "message": "Workout plan created successfully",
            "plan_id": new_plan_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500