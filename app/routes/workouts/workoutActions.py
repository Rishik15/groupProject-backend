from . import workoutAction_bp
from flask import jsonify, request, session
from app.services.workouts import workoutLogging
from datetime import datetime

@workoutAction_bp.route("/active", methods=["GET"])
def getActiveWorkoutSession():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        workout_session = workoutLogging.getActiveWorkoutSession(int(u_id))
        if not workout_session:
            return jsonify({"message": "No active workout session", "session": None}), 200

        sets = workoutLogging.getSessionSets(int(u_id), int(workout_session["session_id"])) or []
        cardio = workoutLogging.getSessionCardio(int(u_id), int(workout_session["session_id"])) or []

        return jsonify({
            "session": workout_session,
            "sets": sets,
            "cardio": cardio
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@workoutAction_bp.route("/start", methods=["POST"])
def startWorkoutSession():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        workout_plan_id = data.get("workout_plan_id")
        notes = data.get("notes")

        if workout_plan_id is not None:
            workout_plan_id = int(workout_plan_id)

        created = workoutLogging.startWorkoutSession(
            user_id=int(u_id),
            workout_plan_id=workout_plan_id,
            notes=notes
        )

        return jsonify({
            "message": "Workout session started successfully",
            "session": created
        }), 201

    except ValueError:
        return jsonify({"error": "Invalid workout_plan_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workoutAction_bp.route("/get_workout", methods=["GET"])
def getWorkoutSession():
    data = request.get_json() 

    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401
        session_id = data.get("session_id")
        workout_session = workoutLogging.getWorkoutSessionById(int(u_id), )
        if not workout_session:
            return jsonify({"error": "Workout session not found"}), 404

        sets = workoutLogging.getSessionSets(int(u_id), session_id) or []
        cardio = workoutLogging.getSessionCardio(int(u_id), session_id) or []

        return jsonify({
            "session": workout_session,
            "sets": sets,
            "cardio": cardio
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workoutAction_bp.route("/mark_workout_done", methods=["PATCH"])
def markDone():
    try:
        data = request.get_json() or {}
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        session_id = data.get("session_id")
        if session_id is None:
            return jsonify({"error": "session_id is required"}), 400

        result = workoutLogging.endWorkoutSession(int(u_id), int(session_id))

        if not result["success"]:
            if result["reason"] == "not_found":
                return jsonify({"error": "Workout session not found"}), 404
            if result["reason"] == "already_ended":
                return jsonify({"error": "Workout session already ended"}), 400

        return jsonify({"message": "Workout session ended successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid session_id"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
