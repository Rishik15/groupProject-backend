from . import coach_bp
from flask import request, jsonify, session


@coach_bp.route("/clients", methods=["GET"])
def get_coach_clients():
    """
Get coach's active clients
---
tags:
  - coach
responses:
  200:
    description: List of clients
    schema:
      type: object
      properties:
        clients:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
              first_name:
                type: string
              last_name:
                type: string
              email:
                type: string
              start_date:
                type: string
                format: date
              agreed_price:
                type: number
  401:
    description: Unauthorized
    """
    coach_id = session.get("user_id")

    if not coach_id:
        return jsonify({"error": "Not logged in"}), 401

    try:
        clients = get_coach_clients(coach_id=coach_id)
        return jsonify({"clients": clients}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500