from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.coach_prices import (
    get_pending_coach_price_requests,
    approve_coach_price_request,
    reject_coach_price_request,
)


@admin_bp.route("/coach-prices/pending", methods=["GET"])
def admin_get_pending_coach_prices():
    """
Get pending coach price requests
---
tags:
  - admin
responses:
  200:
    description: List of price requests
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        requests = get_pending_coach_price_requests(user_id)

        return jsonify({
            "message": "success",
            "requests": requests
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/coach-prices/approve", methods=["PATCH"])
def admin_approve_coach_price():
    """
Approve coach price request
---
tags:
  - admin
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - request_id
      properties:
        request_id:
          type: integer
        admin_action:
          type: string
responses:
  200:
    description: Request approved
  400:
    description: Invalid input
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        request_id = data.get("request_id")
        admin_action = data.get("admin_action")

        result = approve_coach_price_request(
            admin_user_id=user_id,
            request_id=request_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "request": result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/coach-prices/reject", methods=["PATCH"])
def admin_reject_coach_price():
    """
Reject coach price request
---
tags:
  - admin
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - request_id
      properties:
        request_id:
          type: integer
        admin_action:
          type: string
responses:
  200:
    description: Request rejected
  400:
    description: Invalid input
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        request_id = data.get("request_id")
        admin_action = data.get("admin_action")

        result = reject_coach_price_request(
            admin_user_id=user_id,
            request_id=request_id,
            admin_action=admin_action
        )

        return jsonify({
            "message": "success",
            "request": result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500