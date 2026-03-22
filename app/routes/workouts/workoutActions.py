from . import workoutAction_bp
from flask import jsonify, request, session
from app.services.workouts import workoutLogging, workoutActionsFuncs


@workoutAction_bp.route("/getSWPids", methods=["GET"])
def getPlanid_sessionId():
    """
    returns
        json {
            "message": str,
            "Sessions": [
                {
                    "session_id": int,
                    "workout_plan_id": int,
                    "plan_name": str
                }
            ]
        }
    """
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)
        obj = workoutActionsFuncs.getPlanNamesAndIds(u_id)

        return jsonify({
            "message": "successful",
            "Sessions": obj
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/getExerciseInfo", methods=["GET"])
def getExerciseInfo():
    """
    returns
        json {
            "message": str,
            "exercise_info": [
                {
                    "exercise_id": int,
                    "order_in_workout": int,
                    "sets_goal": int,
                    "reps_goal": int,
                    "weight_goal": float,
                    "exercise_name": str,
                    "equipment": str,
                    "video_url": str
                }
            ]
        }
    """
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        plan_id = data.get("workout_plan_id")

        if plan_id is None:
            return jsonify({"error": "workout_plan_id is required"}), 400

        plan_id = int(plan_id)
        exercise_info = workoutActionsFuncs.get_ExerciseInfo(plan_id)

        return jsonify({
            "message": "success",
            "exercise_info": exercise_info
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid workout_plan_id"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/active", methods=["GET"])
def getActiveWorkoutSession():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)

        workout_session = workoutActionsFuncs.getActiveWorkoutSession(u_id)
        if not workout_session:
            return jsonify({
                "message": "No active workout session",
                "session": None
            }), 200

        session_id = int(workout_session["session_id"])
        sets = workoutActionsFuncs.getSessionSets(u_id, session_id)
        cardio = workoutActionsFuncs.getSessionCardio(u_id, session_id)

        return jsonify({
            "session": workout_session,
            "sets": sets,
            "cardio": cardio
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


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

        created = workoutActionsFuncs.startWorkoutSession(
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
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/get_workout", methods=["GET"])
def getWorkoutSession():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        session_id = data.get("session_id")

        if session_id is None:
            return jsonify({"error": "session_id is required"}), 400

        session_id = int(session_id)
        u_id = int(u_id)

        workout_session = workoutActionsFuncs.getWorkoutSessionById(u_id, session_id)
        if not workout_session:
            return jsonify({"error": "Workout session not found"}), 404

        sets = workoutActionsFuncs.getSessionSets(u_id, session_id)
        cardio = workoutActionsFuncs.getSessionCardio(u_id, session_id)

        return jsonify({
            "session": workout_session,
            "sets": sets,
            "cardio": cardio
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid session_id"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


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

        result = workoutActionsFuncs.endWorkoutSession(int(u_id), int(session_id))

        if not result["success"]:
            if result["reason"] == "not_found":
                return jsonify({"error": "Workout session not found"}), 404
            if result["reason"] == "already_ended":
                return jsonify({"error": "Workout session already ended"}), 400

        return jsonify({"message": "Workout session ended successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid session_id"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500