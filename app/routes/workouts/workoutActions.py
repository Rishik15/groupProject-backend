from . import workoutAction_bp
from flask import jsonify, request, session
from app.services.workouts import workoutLogging, workoutActionsFuncs, workoutSchedule
from datetime import datetime


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
    """
Get active workout session
---
tags:
  - workouts
responses:
  200:
    description: Active session data
  401:
    description: Unauthorized
"""
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
        sets = workoutActionsFuncs.getSessionSets(u_id, session_id) or []
        cardio = workoutActionsFuncs.getSessionCardio(u_id, session_id) or []

        return jsonify({
            "session": workout_session,
            "sets": sets,
            "cardio": cardio
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/start", methods=["POST"])
def startWorkoutSession():
    """
Start workout session
---
tags:
  - workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        workout_plan_id:
          type: integer
        notes:
          type: string
responses:
  201:
    description: Workout session started
  401:
    description: Unauthorized
"""
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

        session_id = request.args.get("session_id")

        if session_id is None:
            return jsonify({"error": "session_id is required"}), 400

        session_id = int(session_id)
        u_id = int(u_id)

        workout_session = workoutActionsFuncs.getWorkoutSessionById(u_id, session_id)
        if not workout_session:
            return jsonify({"error": "Workout session not found"}), 404

        sets = workoutActionsFuncs.getSessionSets(u_id, session_id) or []
        cardio = workoutActionsFuncs.getSessionCardio(u_id, session_id) or []

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
    """
End workout session
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
      properties:
        session_id:
          type: integer
responses:
  200:
    description: Workout session ended
  400:
    description: Invalid session
  401:
    description: Unauthorized
"""
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


@workoutAction_bp.route("/schedule", methods=["GET"])
def getWorkoutSchedule():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return jsonify({"error": "start_date and end_date are required"}), 400

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if end_date < start_date:
            return jsonify({"error": "end_date cannot be before start_date"}), 400

        events = workoutSchedule.getWorkoutScheduleEventsForRange(
            int(u_id),
            start_date,
            end_date
        )

        return jsonify({
            "events": events
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/schedule", methods=["POST"])
def createWorkoutScheduleEvent():
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        title = (data.get("title") or "").strip()
        event_date = data.get("event_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        session_type = (data.get("session_type") or "strength").strip()
        status = (data.get("status") or "scheduled").strip()
        notes = data.get("notes")
        workout_plan_id = data.get("workout_plan_id")

        if not title or not event_date or not start_time or not end_time:
            return jsonify({
                "error": "title, event_date, start_time, and end_time are required"
            }), 400

        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()

        try:
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        except ValueError:
            start_time = datetime.strptime(start_time, "%H:%M").time()

        try:
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        except ValueError:
            end_time = datetime.strptime(end_time, "%H:%M").time()

        if workout_plan_id is not None:
            workout_plan_id = int(workout_plan_id)

        created = workoutSchedule.createWorkoutScheduleEvent(
            user_id=int(u_id),
            title=title,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            session_type=session_type,
            status=status,
            notes=notes,
            workout_plan_id=workout_plan_id
        )

        return jsonify({
            "message": "Workout schedule event created successfully",
            "event": created
        }), 201

    except ValueError:
        return jsonify({"error": "Invalid date, time, or workout_plan_id format"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/schedule/<int:event_id>", methods=["PATCH"])
def updateWorkoutScheduleEvent(event_id):
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        title = data.get("title")
        event_date = data.get("event_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        session_type = data.get("session_type")
        status = data.get("status")
        notes = data.get("notes")
        workout_plan_id = data.get("workout_plan_id")

        if event_date is not None:
            event_date = datetime.strptime(event_date, "%Y-%m-%d").date()

        if start_time is not None:
            try:
                start_time = datetime.strptime(start_time, "%H:%M:%S").time()
            except ValueError:
                start_time = datetime.strptime(start_time, "%H:%M").time()

        if end_time is not None:
            try:
                end_time = datetime.strptime(end_time, "%H:%M:%S").time()
            except ValueError:
                end_time = datetime.strptime(end_time, "%H:%M").time()

        if workout_plan_id is not None:
            workout_plan_id = int(workout_plan_id)

        updated = workoutSchedule.updateWorkoutScheduleEvent(
            user_id=int(u_id),
            event_id=event_id,
            title=title,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            session_type=session_type,
            status=status,
            notes=notes,
            workout_plan_id=workout_plan_id
        )

        if not updated:
            return jsonify({"error": "Workout schedule event not found"}), 404

        return jsonify({
            "message": "Workout schedule event updated successfully",
            "event": updated
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid date, time, or workout_plan_id format"}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@workoutAction_bp.route("/schedule/<int:event_id>", methods=["DELETE"])
def deleteWorkoutScheduleEvent(event_id):
    try:
        u_id = session.get("user_id")
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        deleted = workoutSchedule.deleteWorkoutScheduleEvent(int(u_id), event_id)

        if not deleted:
            return jsonify({"error": "Workout schedule event not found"}), 404

        return jsonify({
            "message": "Workout schedule event deleted successfully"
        }), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500