from flask import request, jsonify, session
from app.services.workouts.assign_Plan import assign_plan
from . import workouts_bp


@workouts_bp.route("/assign", methods=["POST"])
def assign_plan_route():
    requester_id = session.get("user_id")

    if not requester_id:
        return jsonify({"error": "Unauthorized"}), 401

    data            = request.get_json()
    plan_id         = data.get("plan_id")
    day_assignments = data.get("day_assignments")
    target_user_id  = data.get("target_user_id")
    force           = data.get("force", False)
    note            = data.get("note")

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    if not day_assignments or not isinstance(day_assignments, list):
        return jsonify({"error": "day_assignments must be a non-empty list"}), 400

    try:
        assign_plan(
            requester_id=requester_id,
            plan_id=plan_id,
            day_assignments=day_assignments,
            target_user_id=target_user_id,
            force=force,
            note=note
        )
        return jsonify({"message": "Plan assigned successfully"}), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        error_str = str(e)
        if error_str.startswith("EXISTING_PLAN:"):
            parts = error_str.split("EXISTING_PLAN:")[1].split("|")
            existing_plan_name = parts[0]
            conflicting_date   = parts[1] if len(parts) > 1 else ""
            return jsonify({
                "error": "existing_plan",
                "existing_plan_name": existing_plan_name,
                "conflicting_date": conflicting_date,
                "message": f"'{existing_plan_name}' is already assigned on {conflicting_date}. Send force=true to replace it."
            }), 409
        return jsonify({"error": error_str}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500