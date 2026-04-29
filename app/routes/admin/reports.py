from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.reports import get_admin_reports, close_admin_report


@admin_bp.route("/reports/list", methods=["POST"])
def admin_get_reports():
    """
Get reports by status
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
    description: List of reports
  400:
    description: Invalid input
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

        reports = get_admin_reports(user_id, status)

        return jsonify({
            "message": "success",
            "reports": reports
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/reports/close", methods=["PATCH"])
def admin_close_report():
    """
Close report
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
        - report_id
      properties:
        report_id:
          type: integer
responses:
  200:
    description: Report closed
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        report_id = data.get("report_id")
        admin_action = data.get("admin_action")

        result = close_admin_report(user_id, report_id, admin_action)

        return jsonify({
            "message": "success",
            "report": result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500