from flask import jsonify, request, session

from . import workouts_bp
from app.services.workouts.workoutPlanDays import get_workout_plan_days


@workouts_bp.route("/plan-days", methods=["GET"])
def get_workout_plan_days_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        plan_id = request.args.get("plan_id")

        if not plan_id:
            return jsonify({"error": "plan_id is required"}), 400

        days = get_workout_plan_days(
            user_id=int(user_id),
            plan_id=int(plan_id),
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "days": days,
                }
            ),
            200,
        )

    except ValueError:
        return jsonify({"error": "Invalid plan_id format"}), 400
    except Exception as e:
        print("[workouts] get_workout_plan_days_route error:", e)
        return jsonify({"error": "Internal server error"}), 500
