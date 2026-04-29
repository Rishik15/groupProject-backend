from datetime import date, time
from flask import jsonify, request, session

from app.routes.manageClient.workouts import manage_workouts_bp
from app.utils.Contract.getClientId import getClientIdFromContract

from app.services.workouts.my_Workouts import get_user_workouts
from app.services.workouts.workoutPlanDays import get_workout_plan_days
from app.services.workouts.assign_Plan import assign_plan_to_user

from app.services.calendar.calendarEvents import (
    get_events_for_user_range,
    create_event,
    update_event,
    delete_event,
)

from app.services.workouts.predefined_Plans import get_predefined_plans


def _get_coach_id():
    coach_id = session.get("user_id")

    if not coach_id:
        return None

    return int(coach_id)


def _get_client_id_from_args():
    coach_id = _get_coach_id()

    if not coach_id:
        return None, None, (jsonify({"error": "Unauthorized"}), 401)

    contract_id = request.args.get("contract_id", type=int)

    if not contract_id:
        return None, None, (jsonify({"error": "contract_id is required"}), 400)

    client_id = getClientIdFromContract(contract_id, coach_id)

    if not client_id:
        return (
            None,
            None,
            (jsonify({"error": "Client not found for this contract"}), 404),
        )

    return coach_id, int(client_id), None


def _get_client_id_from_body(data):
    coach_id = _get_coach_id()

    if not coach_id:
        return None, None, (jsonify({"error": "Unauthorized"}), 401)

    contract_id = data.get("contract_id")

    if not contract_id:
        return None, None, (jsonify({"error": "contract_id is required"}), 400)

    client_id = getClientIdFromContract(int(contract_id), coach_id)

    if not client_id:
        return (
            None,
            None,
            (jsonify({"error": "Client not found for this contract"}), 404),
        )

    return coach_id, int(client_id), None


def _parse_date(value):
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return None


def _parse_time(value):
    if not value:
        return None

    try:
        value = str(value).strip()

        parts = value.split(":")
        if len(parts) < 2:
            return None

        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) > 2 else 0

        return time(hour=hour, minute=minute, second=second)
    except Exception:
        return None


def _validate_plan_day_for_client(client_id, workout_plan_id, workout_day_id):
    try:
        plan_id = int(workout_plan_id)
        day_id = int(workout_day_id)
    except Exception:
        return False, "Invalid workout plan or workout day."

    days = get_workout_plan_days(client_id, plan_id)

    if not days:
        return False, "This workout plan is not assigned to this client."

    valid_day_ids = [int(day["day_id"]) for day in days]

    if day_id not in valid_day_ids:
        return False, "Invalid workout day for this plan."

    return True, None


@manage_workouts_bp.route("/events", methods=["GET"])
def get_events_route():
    """
Get client workout events
---
tags:
  - manage-client-workouts
parameters:
  - name: contract_id
    in: query
    type: integer
    required: true
  - name: start_date
    in: query
    type: string
    required: true
  - name: end_date
    in: query
    type: string
    required: true
responses:
  200:
    description: Events list
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
    coach_id, client_id, error = _get_client_id_from_args()

    if error:
        return error

    start_date_value = request.args.get("start_date")
    end_date_value = request.args.get("end_date")

    if not start_date_value or not end_date_value:
        return jsonify({"error": "start_date and end_date are required"}), 400

    start_date = _parse_date(start_date_value)
    end_date = _parse_date(end_date_value)

    if not start_date or not end_date:
        return jsonify({"error": "Invalid start_date or end_date"}), 400

    if end_date < start_date:
        return jsonify({"error": "end_date cannot be before start_date"}), 400

    events = get_events_for_user_range(
        user_id=client_id,
        start_date=start_date,
        end_date=end_date,
    )

    return jsonify(events), 200


@manage_workouts_bp.route("/events", methods=["POST"])
def create_event_route():
    """
Create client workout event
---
tags:
  - manage-client-workouts
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - contract_id
        - event_date
        - start_time
        - end_time
        - workout_plan_id
        - workout_day_id
responses:
  201:
    description: Event created
  400:
    description: Invalid input
  403:
    description: Invalid plan/day
"""
    data = request.get_json() or {}

    coach_id, client_id, error = _get_client_id_from_body(data)

    if error:
        return error

    required_fields = [
        "event_date",
        "start_time",
        "end_time",
        "description",
        "workout_plan_id",
        "workout_day_id",
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    event_date = _parse_date(data.get("event_date"))
    start_time = _parse_time(data.get("start_time"))
    end_time = _parse_time(data.get("end_time"))

    if not event_date or not start_time or not end_time:
        return jsonify({"error": "Invalid date or time"}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time must be after start_time"}), 400

    is_valid, message = _validate_plan_day_for_client(
        client_id,
        data.get("workout_plan_id"),
        data.get("workout_day_id"),
    )

    if not is_valid:
        return jsonify({"error": message}), 403

    event = create_event(
        user_id=client_id,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        event_type="workout",
        description=data.get("description"),
        notes=data.get("notes"),
        workout_plan_id=int(data.get("workout_plan_id")),
        workout_day_id=int(data.get("workout_day_id")),
    )

    return jsonify(event), 201


@manage_workouts_bp.route("/events", methods=["PATCH"])
def update_event_route():
    """
Update client workout event
---
tags:
  - manage-client-workouts
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - contract_id
        - event_id
responses:
  200:
    description: Event updated
  404:
    description: Event not found
"""
    data = request.get_json() or {}

    coach_id, client_id, error = _get_client_id_from_body(data)

    if error:
        return error

    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    required_fields = [
        "event_date",
        "start_time",
        "end_time",
        "description",
        "workout_plan_id",
        "workout_day_id",
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    event_date = _parse_date(data.get("event_date"))
    start_time = _parse_time(data.get("start_time"))
    end_time = _parse_time(data.get("end_time"))

    if not event_date or not start_time or not end_time:
        return jsonify({"error": "Invalid date or time"}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time must be after start_time"}), 400

    is_valid, message = _validate_plan_day_for_client(
        client_id,
        data.get("workout_plan_id"),
        data.get("workout_day_id"),
    )

    if not is_valid:
        return jsonify({"error": message}), 403

    event = update_event(
        user_id=client_id,
        event_id=int(event_id),
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        description=data.get("description"),
        notes=data.get("notes"),
        workout_plan_id=int(data.get("workout_plan_id")),
        workout_day_id=int(data.get("workout_day_id")),
    )

    if not event:
        return jsonify({"error": "Workout event not found"}), 404

    return jsonify(event), 200


@manage_workouts_bp.route("/events", methods=["DELETE"])
def delete_event_route():
    """
Delete client workout event
---
tags:
  - manage-client-workouts
parameters:
  - name: contract_id
    in: query
    type: integer
    required: true
  - name: event_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Event deleted
  404:
    description: Event not found
"""
    coach_id, client_id, error = _get_client_id_from_args()

    if error:
        return error

    event_id = request.args.get("event_id", type=int)

    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    deleted = delete_event(client_id, event_id)

    if not deleted:
        return jsonify({"error": "Workout event not found"}), 404

    return jsonify({"success": True, "eventId": event_id}), 200


@manage_workouts_bp.route("/client-plans", methods=["GET"])
def get_client_plans_route():
    """
Get client workout plans
---
tags:
  - manage-client-workouts
parameters:
  - name: contract_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Client plans
"""
    coach_id, client_id, error = _get_client_id_from_args()

    if error:
        return error

    plans = get_user_workouts(client_id)

    return jsonify(plans), 200


@manage_workouts_bp.route("/coach-plans", methods=["GET"])
def get_coach_plans_route():
    """
Get coach workout plans
---
tags:
  - manage-client-workouts
responses:
  200:
    description: Coach plans
"""
    coach_id = _get_coach_id()

    if not coach_id:
        return jsonify({"error": "Unauthorized"}), 401

    plans = get_user_workouts(coach_id)

    return jsonify(plans), 200


@manage_workouts_bp.route("/plan-days", methods=["GET"])
def get_plan_days_route():
    """
Get client plan days
---
tags:
  - manage-client-workouts
parameters:
  - name: contract_id
    in: query
    type: integer
    required: true
  - name: plan_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Plan days
"""
    coach_id, client_id, error = _get_client_id_from_args()

    if error:
        return error

    plan_id = request.args.get("plan_id", type=int)

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    days = get_workout_plan_days(client_id, plan_id)

    return jsonify(days), 200


@manage_workouts_bp.route("/coach-plan-days", methods=["GET"])
def get_coach_plan_days_route():
    """
Get coach plan days
---
tags:
  - manage-client-workouts
parameters:
  - name: plan_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Plan days
"""
    coach_id = _get_coach_id()

    if not coach_id:
        return jsonify({"error": "Unauthorized"}), 401

    plan_id = request.args.get("plan_id", type=int)

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    days = get_workout_plan_days(coach_id, plan_id)

    return jsonify(days), 200


@manage_workouts_bp.route("/assign-plan", methods=["POST"])
def assign_plan_route():
    """
Assign workout plan to client
---
tags:
  - manage-client-workouts
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - contract_id
        - plan_id
      properties:
        contract_id:
          type: integer
        plan_id:
          type: integer
        note:
          type: string
responses:
  200:
    description: Plan assigned
"""
    data = request.get_json() or {}

    coach_id, client_id, error = _get_client_id_from_body(data)

    if error:
        return error

    plan_id = data.get("plan_id")

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    result = assign_plan_to_user(
        user_id=client_id,
        plan_id=int(plan_id),
        coach_id=coach_id,
        note=data.get("note") or "Assigned by coach",
    )

    return jsonify(result), 200


@manage_workouts_bp.route("/system-plans", methods=["GET"])
def get_system_plans_route():
    """
Get system workout plans
---
tags:
  - manage-client-workouts
responses:
  200:
    description: System plans
"""
    coach_id = _get_coach_id()

    if not coach_id:
        return jsonify({"error": "Unauthorized"}), 401

    plans = get_predefined_plans()

    mapped_plans = []

    for plan in plans:
        mapped_plans.append(
            {
                "plan_id": plan["plan_id"],
                "plan_name": plan["plan_name"],
                "description": plan["description"],
                "source": "system",
                "total_exercises": plan["exercise_count"],
            }
        )

    return jsonify(mapped_plans), 200
