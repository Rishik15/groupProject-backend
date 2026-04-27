from datetime import date, datetime, time
from flask import jsonify, request, session

from app.routes.coachsession import coach_session_bp
from app.services.coachsession import coachSessionService
from app.utils.Contract.getClientId import getClientIdFromContract


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M:%S").time()
    except ValueError:
        return datetime.strptime(value, "%H:%M").time()


def make_json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}

    return value


def get_client_from_contract(contract_id_raw, coach_id):
    if not contract_id_raw:
        return None, None, (jsonify({"error": "contract_id is required"}), 400)

    try:
        contract_id = int(contract_id_raw)
    except ValueError:
        return None, None, (jsonify({"error": "Invalid contract_id format"}), 400)

    client_id = getClientIdFromContract(contract_id, int(coach_id))

    if not client_id:
        return (
            None,
            None,
            (
                jsonify({"error": "Contract not found or access denied"}),
                403,
            ),
        )

    return contract_id, int(client_id), None


@coach_session_bp.route("/events", methods=["GET"])
def get_coach_session_events():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        start_date_raw = request.args.get("start_date")
        end_date_raw = request.args.get("end_date")

        if not start_date_raw or not end_date_raw:
            return jsonify({"error": "start_date and end_date are required"}), 400

        start_date = parse_date(start_date_raw)
        end_date = parse_date(end_date_raw)

        if end_date < start_date:
            return jsonify({"error": "end_date cannot be before start_date"}), 400

        events = coachSessionService.get_all_coach_session_events(
            coach_id=int(coach_id),
            start_date=start_date,
            end_date=end_date,
        )

        return jsonify({"events": make_json_safe(events)}), 200

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        print("[coachsession] get_coach_session_events error:", e)
        return jsonify({"error": "Internal server error"}), 500


@coach_session_bp.route("/events", methods=["POST"])
def create_coach_session_event():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}

        contract_id, client_id, error_response = get_client_from_contract(
            data.get("contract_id"),
            coach_id,
        )

        if error_response:
            return error_response

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

        event_date = parse_date(event_date_raw)
        start_time = parse_time(start_time_raw)
        end_time = parse_time(end_time_raw)

        if end_time <= start_time:
            return jsonify({"error": "end_time must be after start_time"}), 400

        conflicts = coachSessionService.get_time_conflicts(
            coach_id=int(coach_id),
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
        )

        if conflicts:
            return (
                jsonify(
                    make_json_safe(
                        {
                            "error": "You already have a coach session during this time",
                            "conflicts": conflicts,
                        }
                    )
                ),
                409,
            )

        created = coachSessionService.create_coach_session_event(
            contract_id=contract_id,
            coach_id=int(coach_id),
            client_id=client_id,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            description=description or "Coach Session",
            notes=notes,
        )

        return (
            jsonify(
                make_json_safe(
                    {
                        "message": "Coach session created successfully",
                        "event": created,
                    }
                )
            ),
            201,
        )

    except ValueError:
        return jsonify({"error": "Invalid date, time, or contract_id format"}), 400
    except Exception as e:
        print("[coachsession] create_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@coach_session_bp.route("/events", methods=["PATCH"])
def update_coach_session_event():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        event_id_raw = request.args.get("event_id")

        if not event_id_raw:
            return jsonify({"error": "event_id is required"}), 400

        event_id = int(event_id_raw)

        existing = coachSessionService.get_coach_session_event_by_id(
            coach_id=int(coach_id),
            event_id=event_id,
        )

        if not existing:
            return jsonify({"error": "Coach session event not found"}), 404

        data = request.get_json() or {}

        event_date = None
        start_time = None
        end_time = None
        description = None
        notes = None
        contract_id = None
        client_id = None

        if data.get("contract_id") is not None:
            contract_id, client_id, error_response = get_client_from_contract(
                data.get("contract_id"),
                coach_id,
            )

            if error_response:
                return error_response

        if data.get("event_date") is not None:
            event_date = parse_date(data.get("event_date"))

        if data.get("start_time") is not None:
            start_time = parse_time(data.get("start_time"))

        if data.get("end_time") is not None:
            end_time = parse_time(data.get("end_time"))

        if data.get("description") is not None:
            description = (data.get("description") or "").strip()

        if data.get("notes") is not None:
            notes = (data.get("notes") or "").strip()

        final_date = event_date or parse_date(existing["date"])
        final_start_time = start_time or parse_time(existing["startTime"])
        final_end_time = end_time or parse_time(existing["endTime"])

        if final_end_time <= final_start_time:
            return jsonify({"error": "end_time must be after start_time"}), 400

        conflicts = coachSessionService.get_time_conflicts(
            coach_id=int(coach_id),
            event_date=final_date,
            start_time=final_start_time,
            end_time=final_end_time,
            exclude_event_id=event_id,
        )

        if conflicts:
            return (
                jsonify(
                    make_json_safe(
                        {
                            "error": "You already have a coach session during this time",
                            "conflicts": conflicts,
                        }
                    )
                ),
                409,
            )

        updated = coachSessionService.update_coach_session_event(
            coach_id=int(coach_id),
            event_id=event_id,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            notes=notes,
            contract_id=contract_id,
            client_id=client_id,
        )

        return (
            jsonify(
                make_json_safe(
                    {
                        "message": "Coach session updated successfully",
                        "event": updated,
                    }
                )
            ),
            200,
        )

    except ValueError:
        return (
            jsonify({"error": "Invalid date, time, contract_id, or event_id format"}),
            400,
        )
    except Exception as e:
        print("[coachsession] update_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@coach_session_bp.route("/events", methods=["DELETE"])
def delete_coach_session_event():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        event_id_raw = request.args.get("event_id")

        if not event_id_raw:
            return jsonify({"error": "event_id is required"}), 400

        event_id = int(event_id_raw)

        existing = coachSessionService.get_coach_session_event_by_id(
            coach_id=int(coach_id),
            event_id=event_id,
        )

        if not existing:
            return jsonify({"error": "Coach session event not found"}), 404

        coachSessionService.delete_coach_session_event(
            coach_id=int(coach_id),
            event_id=event_id,
        )

        return jsonify({"message": "Coach session deleted successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid event_id format"}), 400
    except Exception as e:
        print("[coachsession] delete_coach_session_event error:", e)
        return jsonify({"error": "Internal server error"}), 500


@coach_session_bp.route("/status", methods=["PATCH"])
def update_coach_session_status():
    try:
        coach_id = session.get("user_id")

        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        event_id_raw = request.args.get("event_id")

        if not event_id_raw:
            return jsonify({"error": "event_id is required"}), 400

        event_id = int(event_id_raw)
        data = request.get_json() or {}
        status = data.get("status")

        if status not in ["scheduled", "completed", "cancelled"]:
            return jsonify({"error": "Invalid status"}), 400

        updated = coachSessionService.update_coach_session_status(
            coach_id=int(coach_id),
            event_id=event_id,
            status=status,
        )

        if not updated:
            return jsonify({"error": "Coach session event not found"}), 404

        return (
            jsonify(
                make_json_safe(
                    {
                        "message": "Coach session status updated successfully",
                        "event": updated,
                    }
                )
            ),
            200,
        )

    except ValueError:
        return jsonify({"error": "Invalid event_id format"}), 400
    except Exception as e:
        print("[coachsession] update_coach_session_status error:", e)
        return jsonify({"error": "Internal server error"}), 500
