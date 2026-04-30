from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.my_Exercises import get_my_exercises


@coach_bp.route("/exercise/my-exercises", methods=["GET"])
def my_exercises_route():
    coach_id = session.get("user_id")

    if not coach_id:
        return jsonify({"error": "Unauthorized"}), 401

    mode = request.args.get("mode")

    if mode != "coach":
        return jsonify({"error": "Unauthorized. Coach access only."}), 401

    try:
        exercises = get_my_exercises(coach_id=int(coach_id))
        return jsonify({"exercises": exercises}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500