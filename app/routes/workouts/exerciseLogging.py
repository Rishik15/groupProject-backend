from . import exerciseLog_bp
from flask import jsonify, request, session
from app.services.workouts import workoutLogging
from datetime import datetime


@exerciseLog_bp.route("/log_weights", methods=["POST"])
def logSets():
    """
Log weight training set
---
tags:
  - workouts
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - session_id
        - exercise_id
        - set_number
      properties:
        session_id:
          type: integer
        exercise_id:
          type: integer
        set_number:
          type: integer
        reps:
          type: integer
        weight:
          type: number
        rpe:
          type: number
        datetimeFinished:
          type: string
responses:
  200:
    description: Set logged successfully
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
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

        result = workoutLogging.logWorkoutInformation(
            user_id=int(u_id),
            session_id=session_id,
            exercise_id=exercise_id,
            set_number=set_number,
            reps=reps,
            weight=weight,
            rpe=rpe,
            datetimeFinished=datetimeFinished
        )

        if not result["success"]:
            if result["reason"] == "not_found":
                return jsonify({"error": "Workout session not found"}), 404
            if result["reason"] == "ended":
                return jsonify({"error": "Cannot log to an ended workout session"}), 400

        return jsonify({"message": "Set logged successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid numeric or datetime format"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@exerciseLog_bp.route("/log_cardio", methods=["POST"])
def logCardio():
    """
Log cardio activity
---
tags:
  - workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        session_id:
          type: integer
        steps:
          type: integer
        distance_km:
          type: number
        duration_min:
          type: integer
        calories:
          type: integer
        avg_hr:
          type: integer
responses:
  201:
    description: Cardio logged successfully
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        session_id = data.get("session_id")
        performed_at = data.get("performed_at")
        steps = data.get("steps")
        distance_km = data.get("distance_km")
        duration_min = data.get("duration_min")
        calories = data.get("calories")
        avg_hr = data.get("avg_hr")

        if session_id is not None:
            session_id = int(session_id)

        steps = int(steps) if steps is not None else None
        distance_km = float(distance_km) if distance_km is not None else None
        duration_min = int(duration_min) if duration_min is not None else None
        calories = int(calories) if calories is not None else None
        avg_hr = int(avg_hr) if avg_hr is not None else None

        if performed_at:
            performed_at = datetime.fromisoformat(performed_at)

        if all(value is None for value in [steps, distance_km, duration_min, calories, avg_hr]):
            return jsonify({
                "error": "At least one cardio field is required: steps, distance_km, duration_min, calories, avg_hr"
            }), 400

        if steps is not None and steps < 0:
            return jsonify({"error": "steps cannot be negative"}), 400

        if distance_km is not None and distance_km < 0:
            return jsonify({"error": "distance_km cannot be negative"}), 400

        if duration_min is not None and duration_min < 0:
            return jsonify({"error": "duration_min cannot be negative"}), 400

        if calories is not None and calories < 0:
            return jsonify({"error": "calories cannot be negative"}), 400

        if avg_hr is not None and avg_hr < 0:
            return jsonify({"error": "avg_hr cannot be negative"}), 400

        result = workoutLogging.logCardioActivity(
            user_id=int(u_id),
            session_id=session_id,
            performed_at=performed_at,
            steps=steps,
            distance_km=distance_km,
            duration_min=duration_min,
            calories=calories,
            avg_hr=avg_hr
        )

        if not result["success"]:
            if result["reason"] == "not_found":
                return jsonify({"error": "Workout session not found"}), 404
            if result["reason"] == "ended":
                return jsonify({"error": "Cannot log cardio to an ended workout session"}), 400

        return jsonify({"message": "Cardio logged successfully"}), 201

    except ValueError:
        return jsonify({"error": "Invalid numeric or datetime format"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500