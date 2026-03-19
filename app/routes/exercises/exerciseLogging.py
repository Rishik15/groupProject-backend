from . import exerciseLog_bp, markExerciseDone_bp
from flask import jsonify, request, session
from app.services.workouts import workoutLogging
from datetime import datetime


@exerciseLog_bp.route("/", methods=["POST"])
def logSets():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        session_id = data.get("session_id")
        exercise_id = data.get("exercise_id")
        set_number = data.get("set_number")
        reps = data.get("reps")
        weight = data.get("weight")
        rpe = data.get("rpe")
        datetimeFinished = data.get("datetimeFinished")

        required_fields = [session_id, exercise_id, set_number]
        if any(field is None for field in required_fields):
            return jsonify({"error": "session_id, exercise_id, and set_number are required"}), 400

        session_id = int(session_id)
        exercise_id = int(exercise_id)
        set_number = int(set_number)
        reps = int(reps) if reps is not None else None
        weight = float(weight) if weight is not None else None
        rpe = float(rpe) if rpe is not None else None

        if set_number < 1:
            return jsonify({"error": "set_number must be at least 1"}), 400

        if reps is not None and reps < 0:
            return jsonify({"error": "reps cannot be negative"}), 400

        if weight is not None and weight < 0:
            return jsonify({"error": "weight cannot be negative"}), 400

        if rpe is not None and rpe < 0:
            return jsonify({"error": "rpe cannot be negative"}), 400

        if datetimeFinished:
            datetimeFinished = datetime.fromisoformat(datetimeFinished)

        workoutLogging.logWorkoutInformation(
            session_id=session_id,
            exercise_id=exercise_id,
            set_number=set_number,
            reps=reps,
            weight=weight,
            rpe=rpe,
            datetimeFinished=datetimeFinished
        )

        return jsonify({"message": "Set logged successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid numeric or datetime format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@markExerciseDone_bp.route("/", methods=["PATCH"])
def markDone():
    try:
        data = request.get_json() or {}
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        session_id = data.get("session_id")
        if session_id is None:
            return jsonify({"error": "session_id is required"}), 400

        workoutLogging.endWorkoutSession(int(u_id), int(session_id))
        return jsonify({"message": "Workout session ended successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid session_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500