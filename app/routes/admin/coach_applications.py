from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.coach_applications import (
    get_admin_coach_applications,
    approve_coach_application,
    reject_coach_application
)


@admin_bp.route("/coach-applications/list", methods=["POST"])
def admin_get_coach_applications():
    """
Get coach applications by status
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
        - status
      properties:
        status:
          type: string
responses:
  200:
    description: List of applications
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

        data = request.get_json() or {}
        status = data.get("status")

        if not status:
            return jsonify({"error": "status is required"}), 400

        user_id = int(user_id)

        applications = get_admin_coach_applications(user_id, status)

        return jsonify({
            "message": "success",
            "applications": applications
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/coach-applications/approve", methods=["PATCH"])
def admin_approve_coach_application():
    """
Approve coach application
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
        - application_id
      properties:
        application_id:
          type: integer
        admin_action:
          type: string
responses:
  200:
    description: Application approved
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

        application_id = data.get("application_id")
        admin_action = data.get("admin_action")

        application = approve_coach_application(user_id, application_id, admin_action)

        return jsonify({
            "message": "success",
            "application": application
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/coach-applications/reject", methods=["PATCH"])
def admin_reject_coach_application():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        application_id = data.get("application_id")
        admin_action = data.get("admin_action")

        application = reject_coach_application(user_id, application_id, admin_action)

        return jsonify({
            "message": "success",
            "application": application
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500