from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.create_Exercise import create_exercise


@coach_bp.route("/exercise/create", methods=["POST"])
def create_exercise_route():
    coach_id = session.get("user_id")
    role = session.get("role")

    if not coach_id or role != "coach":
        return jsonify({"error": "Unauthorized. Coach access only."}), 401

    exercise_name = request.form.get("name")
    equipment = request.form.get("equipment")
    description = request.form.get("description")
    video_file = request.files.get("video")

    if not exercise_name:
        return jsonify({"error": "exercise_name is required"}), 400
    if not equipment:
        return jsonify({"error": "equipment is required"}), 400

    try:
        exercise = create_exercise(
            coach_id=coach_id,
            exercise_name=exercise_name,
            equipment=equipment,
            description=description,
            video_file=video_file
        )
        return jsonify({"message": "Exercise created successfully", "exercise": exercise}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500