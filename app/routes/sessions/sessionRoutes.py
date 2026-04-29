from flask import jsonify, request, session

from app.routes.sessions import sessions_bp
from app.services.sessions.sessionService import (
    finish_session,
    get_active_session,
    get_session_exercises,
    get_today_scheduled_sessions,
    start_scheduled_session,
)


@sessions_bp.route("/scheduled-today", methods=["GET"])
def scheduled_today_route():
    """
Get today's scheduled sessions
---
tags:
  - sessions
responses:
  200:
    description: Scheduled sessions
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    result = get_today_scheduled_sessions(user_id)

    return jsonify(result), 200


@sessions_bp.route("/active", methods=["GET"])
def active_session_route():
    """
Get active session
---
tags:
  - sessions
responses:
  200:
    description: Active session data
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    result = get_active_session(user_id)

    return jsonify(result), 200


@sessions_bp.route("/start-scheduled", methods=["POST"])
def start_scheduled_session_route():
    """
Start scheduled session
---
tags:
  - sessions
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - event_id
      properties:
        event_id:
          type: integer
responses:
  200:
    description: Session started
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    result = start_scheduled_session(user_id, int(event_id))

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@sessions_bp.route("/session-exercises", methods=["GET"])
def session_exercises_route():
    """
Get session exercises
---
tags:
  - sessions
parameters:
  - name: session_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Session exercises
  400:
    description: Missing session_id
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    session_id = request.args.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    result = get_session_exercises(user_id, int(session_id))

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200


@sessions_bp.route("/finish", methods=["PATCH"])
def finish_session_route():
    """
Finish session
---
tags:
  - sessions
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
    description: Session finished
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    result = finish_session(user_id, int(session_id))

    if not result.get("success"):
        return jsonify(result), 400

    return jsonify(result), 200