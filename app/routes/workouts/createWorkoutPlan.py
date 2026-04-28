from flask import jsonify, request, session
from . import workouts_bp
from app.services.workouts.createWorkout_Plan import create_workout_plan
from app.services import run_query

@workouts_bp.route("/create", methods=["POST"])
def create_workout_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    plan_name = data.get("name")
    days = data.get("days", [])

    if not plan_name:
        return jsonify({"error": "plan_name is required"}), 400

    if not days or not isinstance(days, list) or len(days) == 0:
        return jsonify({"error": "At least one day is required"}), 400

    for i, day in enumerate(days):
        if not day.get("exercises") or len(day["exercises"]) == 0:
            return jsonify({"error": f"Day {i + 1} must have at least one exercise"}), 400

    user = run_query(
        "SELECT first_name, last_name FROM users_immutables WHERE user_id = :user_id",
        {"user_id": user_id},
        fetch=True, commit=False
    )
    
    full_name = f"{user[0]['first_name']} {user[0]['last_name']}" if user else "Unknown"
    description = f"This workout plan was created by {full_name}"

    try:
        new_plan_id = create_workout_plan(user_id, plan_name, days, description)
        return jsonify({
            "message": "Workout plan created successfully",
            "plan_id": new_plan_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500