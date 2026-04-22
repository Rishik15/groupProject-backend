from flask import session, jsonify
from app.services.workouts.my_Workouts import get_user_workouts
from . import workouts_bp

@workouts_bp.route("/my-workouts", methods=["GET"])
def my_workouts_route():
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