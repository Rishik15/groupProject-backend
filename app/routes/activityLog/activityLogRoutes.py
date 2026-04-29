from flask import jsonify, request, session

from app.routes.activityLog import activity_log_bp
from app.services.activityLog.activityLogService import (
    get_activity_logs,
    get_full_activity_logs,
    log_cardio_activity,
    log_strength_set,
    update_cardio_log,
    update_strength_set,
)


@activity_log_bp.route("/logs", methods=["GET"])
def get_activity_logs_route():
    """
Get activity logs
---
tags:
  - activity-log
parameters:
  - name: session_id
    in: query
    type: integer
responses:
  200:
    description: Activity logs
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    session_id = request.args.get("session_id")
    session_id = int(session_id) if session_id else None

    result = get_activity_logs(user_id, session_id)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@activity_log_bp.route("/full-logs", methods=["GET"])
def get_full_activity_logs_route():
    """
Get full activity history
---
tags:
  - activity-log
responses:
  200:
    description: Full activity logs
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    result = get_full_activity_logs(user_id)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@activity_log_bp.route("/strength", methods=["POST"])
def log_strength_set_route():
    """
Log strength set
---
tags:
  - activity-log
parameters:
  - name: body
    in: body
    schema:
      type: object
responses:
  200:
    description: Strength set logged
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}

    result = log_strength_set(user_id, data)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@activity_log_bp.route("/strength", methods=["PATCH"])
def update_strength_set_route():
    """
Update strength set
---
tags:
  - activity-log
parameters:
  - name: set_log_id
    in: query
    type: integer
    required: true
  - name: body
    in: body
    schema:
      type: object
responses:
  200:
    description: Strength set updated
  400:
    description: Missing set_log_id
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    set_log_id = request.args.get("set_log_id")

    if not set_log_id:
        return jsonify({"error": "set_log_id is required"}), 400

    data = request.get_json() or {}

    result = update_strength_set(user_id, int(set_log_id), data)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@activity_log_bp.route("/cardio", methods=["POST"])
def log_cardio_activity_route():
    """
Log cardio activity
---
tags:
  - activity-log
parameters:
  - name: body
    in: body
    schema:
      type: object
responses:
  200:
    description: Cardio logged
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}

    result = log_cardio_activity(user_id, data)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@activity_log_bp.route("/cardio", methods=["PATCH"])
def update_cardio_log_route():
    """
Update cardio log
---
tags:
  - activity-log
parameters:
  - name: cardio_log_id
    in: query
    type: integer
    required: true
  - name: body
    in: body
    schema:
      type: object
responses:
  200:
    description: Cardio updated
  400:
    description: Missing cardio_log_id
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    cardio_log_id = request.args.get("cardio_log_id")

    if not cardio_log_id:
        return jsonify({"error": "cardio_log_id is required"}), 400

    data = request.get_json() or {}

    result = update_cardio_log(user_id, int(cardio_log_id), data)

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200