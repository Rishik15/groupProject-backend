from datetime import datetime
from flask import jsonify, request, session

from app.routes.calendar import calendar_bp
from app.services.calendar import calendarEvents
from app.utils.Contract.getClientId import getClientIdFromContract


@calendar_bp.route("/events", methods=["GET"])
def get_my_calendar_events():
    try:
        user_id = session.get("user_id")

        print("CALENDAR SESSION:", dict(session))
        print("CALENDAR COOKIES:", request.cookies)
        print("START:", request.args.get("start_date"))
        print("END:", request.args.get("end_date"))

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        start_date_raw = request.args.get("start_date")
        end_date_raw = request.args.get("end_date")

        if not start_date_raw or not end_date_raw:
            return jsonify({"error": "start_date and end_date are required"}), 400

        start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date()

        if end_date < start_date:
            return jsonify({"error": "end_date cannot be before start_date"}), 400

        events = calendarEvents.get_events_for_user_range(
            user_id=int(user_id),
            start_date=start_date,
            end_date=end_date,
        )

        return jsonify({"events": events}), 200

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        print("[calendar] get_my_calendar_events error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/events", methods=["POST"])
def create_my_workout_event():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        event_date_raw = data.get("event_date")
        start_time_raw = data.get("start_time")
        end_time_raw = data.get("end_time")
        description = (data.get("description") or "").strip()
        notes = (data.get("notes") or "").strip()
        workout_plan_id = data.get("workout_plan_id")
        workout_day_id = data.get("workout_day_id")

        if not event_date_raw or not start_time_raw or not end_time_raw:
            return (
                jsonify({"error": "event_date, start_time, and end_time are required"}),
                400,
            )

        if workout_plan_id is None:
            return jsonify({"error": "workout_plan_id is required"}), 400

        if workout_day_id is None:
            return jsonify({"error": "workout_day_id is required"}), 400

        event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()

        try:
            start_time = datetime.strptime(start_time_raw, "%H:%M:%S").time()
        except ValueError:
            start_time = datetime.strptime(start_time_raw, "%H:%M").time()

        try:
            end_time = datetime.strptime(end_time_raw, "%H:%M:%S").time()
        except ValueError:
            end_time = datetime.strptime(end_time_raw, "%H:%M").time()

        workout_plan_id = int(workout_plan_id)
        workout_day_id = int(workout_day_id)

        if end_time <= start_time:
            return jsonify({"error": "end_time must be after start_time"}), 400

        if not calendarEvents.workout_plan_exists(workout_plan_id):
            return jsonify({"error": "Workout plan not found"}), 404

        if not calendarEvents.workout_day_belongs_to_plan(
            workout_plan_id, workout_day_id
        ):
            return (
                jsonify({"error": "Workout day does not belong to selected plan"}),
                400,
            )

        created = calendarEvents.create_event(
            user_id=int(user_id),
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            event_type="workout",
            description=description or "Workout Session",
            notes=notes,
            workout_plan_id=workout_plan_id,
            workout_day_id=workout_day_id,
        )

        return (
            jsonify(
                {
                    "message": "Workout event created successfully",
                    "event": created,
                }
            ),
            201,
        )

    except ValueError:
        return (
            jsonify(
                {
                    "error": "Invalid date, time, workout_plan_id, or workout_day_id format"
                }
            ),
            400,
        )
    except Exception as e:
        print("[calendar] create_my_workout_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/events", methods=["PATCH"])
def update_my_workout_event():
    try:
        user_id = session.get("user_id")
        event_id = request.args.get("event_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400

        event_id = int(event_id)
        existing = calendarEvents.get_event_by_id_for_user(int(user_id), event_id)

        if not existing:
            return jsonify({"error": "Event not found"}), 404

        if existing["eventType"] != "workout":
            return jsonify({"error": "You can only edit workout events"}), 403

        data = request.get_json() or {}

        event_date = None
        start_time = None
        end_time = None
        description = None
        notes = None
        workout_plan_id = None
        workout_day_id = None

        if data.get("event_date") is not None:
            event_date = datetime.strptime(data.get("event_date"), "%Y-%m-%d").date()

        if data.get("start_time") is not None:
            try:
                start_time = datetime.strptime(
                    data.get("start_time"), "%H:%M:%S"
                ).time()
            except ValueError:
                start_time = datetime.strptime(data.get("start_time"), "%H:%M").time()

        if data.get("end_time") is not None:
            try:
                end_time = datetime.strptime(data.get("end_time"), "%H:%M:%S").time()
            except ValueError:
                end_time = datetime.strptime(data.get("end_time"), "%H:%M").time()

        if data.get("description") is not None:
            description = (data.get("description") or "").strip()

        if data.get("notes") is not None:
            notes = (data.get("notes") or "").strip()

        if data.get("workout_plan_id") is not None:
            workout_plan_id = int(data.get("workout_plan_id"))

        if data.get("workout_day_id") is not None:
            workout_day_id = int(data.get("workout_day_id"))

        final_plan_id = (
            workout_plan_id
            if workout_plan_id is not None
            else existing["workoutPlanId"]
        )

        final_day_id = (
            workout_day_id if workout_day_id is not None else existing["workoutDayId"]
        )

        if final_plan_id is None:
            return jsonify({"error": "workout_plan_id is required"}), 400

        if final_day_id is None:
            return jsonify({"error": "workout_day_id is required"}), 400

        if not calendarEvents.workout_plan_exists(int(final_plan_id)):
            return jsonify({"error": "Workout plan not found"}), 404

        if not calendarEvents.workout_day_belongs_to_plan(
            int(final_plan_id), int(final_day_id)
        ):
            return (
                jsonify({"error": "Workout day does not belong to selected plan"}),
                400,
            )

        if start_time is None:
            try:
                start_time_check = datetime.strptime(
                    existing["startTime"], "%H:%M:%S"
                ).time()
            except ValueError:
                start_time_check = datetime.strptime(
                    existing["startTime"], "%H:%M"
                ).time()
        else:
            start_time_check = start_time

        if end_time is None:
            try:
                end_time_check = datetime.strptime(
                    existing["endTime"], "%H:%M:%S"
                ).time()
            except ValueError:
                end_time_check = datetime.strptime(existing["endTime"], "%H:%M").time()
        else:
            end_time_check = end_time

        if end_time_check <= start_time_check:
            return jsonify({"error": "end_time must be after start_time"}), 400

        updated = calendarEvents.update_event(
            user_id=int(user_id),
            event_id=event_id,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            notes=notes,
            workout_plan_id=workout_plan_id,
            workout_day_id=workout_day_id,
        )

        return (
            jsonify(
                {
                    "message": "Workout event updated successfully",
                    "event": updated,
                }
            ),
            200,
        )

    except ValueError:
        return (
            jsonify(
                {
                    "error": "Invalid date, time, event_id, workout_plan_id, or workout_day_id format"
                }
            ),
            400,
        )
    except Exception as e:
        print("[calendar] update_my_workout_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/events", methods=["DELETE"])
def delete_my_workout_event():
    try:
        user_id = session.get("user_id")
        event_id = request.args.get("event_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400

        event_id = int(event_id)
        existing = calendarEvents.get_event_by_id_for_user(int(user_id), event_id)

        if not existing:
            return jsonify({"error": "Event not found"}), 404

        if existing["eventType"] != "workout":
            return jsonify({"error": "You can only delete workout events"}), 403

        calendarEvents.delete_event(int(user_id), event_id)

        return jsonify({"message": "Workout event deleted successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid event_id format"}), 400
    except Exception as e:
        print("[calendar] delete_my_workout_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/contracts/events", methods=["GET"])
def get_contract_calendar_events():
    try:
        coach_id = session.get("user_id")
        contract_id = request.args.get("contract_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not contract_id:
            return jsonify({"error": "contract_id is required"}), 400

        client_id = getClientIdFromContract(int(contract_id), int(coach_id))

        if not client_id:
            return jsonify({"error": "Contract not found or access denied"}), 403

        start_date_raw = request.args.get("start_date")
        end_date_raw = request.args.get("end_date")

        if not start_date_raw or not end_date_raw:
            return jsonify({"error": "start_date and end_date are required"}), 400

        start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date()

        if end_date < start_date:
            return jsonify({"error": "end_date cannot be before start_date"}), 400

        events = calendarEvents.get_events_for_user_range(
            user_id=int(client_id),
            start_date=start_date,
            end_date=end_date,
        )

        return jsonify({"events": events}), 200

    except ValueError:
        return jsonify({"error": "Invalid contract_id or date format"}), 400
    except Exception as e:
        print("[calendar] get_contract_calendar_events error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/contracts/events", methods=["POST"])
def create_contract_coach_session_event():
    try:
        coach_id = session.get("user_id")
        contract_id = request.args.get("contract_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not contract_id:
            return jsonify({"error": "contract_id is required"}), 400

        client_id = getClientIdFromContract(int(contract_id), int(coach_id))

        if not client_id:
            return jsonify({"error": "Contract not found or access denied"}), 403

        data = request.get_json() or {}

        event_date_raw = data.get("event_date")
        start_time_raw = data.get("start_time")
        end_time_raw = data.get("end_time")
        description = (data.get("description") or "").strip()
        notes = (data.get("notes") or "").strip()

        if not event_date_raw or not start_time_raw or not end_time_raw:
            return (
                jsonify({"error": "event_date, start_time, and end_time are required"}),
                400,
            )

        event_date = datetime.strptime(event_date_raw, "%Y-%m-%d").date()

        try:
            start_time = datetime.strptime(start_time_raw, "%H:%M:%S").time()
        except ValueError:
            start_time = datetime.strptime(start_time_raw, "%H:%M").time()

        try:
            end_time = datetime.strptime(end_time_raw, "%H:%M:%S").time()
        except ValueError:
            end_time = datetime.strptime(end_time_raw, "%H:%M").time()

        if end_time <= start_time:
            return jsonify({"error": "end_time must be after start_time"}), 400

        created = calendarEvents.create_event(
            user_id=int(client_id),
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            event_type="coach_session",
            description=description or "Coach Session",
            notes=notes,
            workout_plan_id=None,
            workout_day_id=None,
        )

        return (
            jsonify(
                {
                    "message": "Coach session event created successfully",
                    "event": created,
                }
            ),
            201,
        )

    except ValueError:
        return jsonify({"error": "Invalid contract_id, date, or time format"}), 400
    except Exception as e:
        print("[calendar] create_contract_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/contracts/events", methods=["PATCH"])
def update_contract_coach_session_event():
    try:
        coach_id = session.get("user_id")
        contract_id = request.args.get("contract_id")
        event_id = request.args.get("event_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not contract_id:
            return jsonify({"error": "contract_id is required"}), 400

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400

        client_id = getClientIdFromContract(int(contract_id), int(coach_id))

        if not client_id:
            return jsonify({"error": "Contract not found or access denied"}), 403

        event_id = int(event_id)
        existing = calendarEvents.get_event_by_id_for_user(int(client_id), event_id)

        if not existing:
            return jsonify({"error": "Event not found"}), 404

        if existing["eventType"] != "coach_session":
            return jsonify({"error": "You can only edit coach session events"}), 403

        data = request.get_json() or {}

        event_date = None
        start_time = None
        end_time = None
        description = None
        notes = None

        if data.get("event_date") is not None:
            event_date = datetime.strptime(data.get("event_date"), "%Y-%m-%d").date()

        if data.get("start_time") is not None:
            try:
                start_time = datetime.strptime(
                    data.get("start_time"), "%H:%M:%S"
                ).time()
            except ValueError:
                start_time = datetime.strptime(data.get("start_time"), "%H:%M").time()

        if data.get("end_time") is not None:
            try:
                end_time = datetime.strptime(data.get("end_time"), "%H:%M:%S").time()
            except ValueError:
                end_time = datetime.strptime(data.get("end_time"), "%H:%M").time()

        if data.get("description") is not None:
            description = (data.get("description") or "").strip()

        if data.get("notes") is not None:
            notes = (data.get("notes") or "").strip()

        if start_time is None:
            try:
                start_time_check = datetime.strptime(
                    existing["startTime"], "%H:%M:%S"
                ).time()
            except ValueError:
                start_time_check = datetime.strptime(
                    existing["startTime"], "%H:%M"
                ).time()
        else:
            start_time_check = start_time

        if end_time is None:
            try:
                end_time_check = datetime.strptime(
                    existing["endTime"], "%H:%M:%S"
                ).time()
            except ValueError:
                end_time_check = datetime.strptime(existing["endTime"], "%H:%M").time()
        else:
            end_time_check = end_time

        if end_time_check <= start_time_check:
            return jsonify({"error": "end_time must be after start_time"}), 400

        updated = calendarEvents.update_event(
            user_id=int(client_id),
            event_id=event_id,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            notes=notes,
            clear_workout_fields=True,
        )

        return (
            jsonify(
                {
                    "message": "Coach session event updated successfully",
                    "event": updated,
                }
            ),
            200,
        )

    except ValueError:
        return (
            jsonify({"error": "Invalid contract_id, event_id, date, or time format"}),
            400,
        )
    except Exception as e:
        print("[calendar] update_contract_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@calendar_bp.route("/contracts/events", methods=["DELETE"])
def delete_contract_coach_session_event():
    try:
        coach_id = session.get("user_id")
        contract_id = request.args.get("contract_id")
        event_id = request.args.get("event_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        if not contract_id:
            return jsonify({"error": "contract_id is required"}), 400

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400

        client_id = getClientIdFromContract(int(contract_id), int(coach_id))

        if not client_id:
            return jsonify({"error": "Contract not found or access denied"}), 403

        event_id = int(event_id)
        existing = calendarEvents.get_event_by_id_for_user(int(client_id), event_id)

        if not existing:
            return jsonify({"error": "Event not found"}), 404

        if existing["eventType"] != "coach_session":
            return jsonify({"error": "You can only delete coach session events"}), 403

        calendarEvents.delete_event(int(client_id), event_id)

        return jsonify({"message": "Coach session event deleted successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid contract_id or event_id format"}), 400
    except Exception as e:
        print("[calendar] delete_contract_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500
