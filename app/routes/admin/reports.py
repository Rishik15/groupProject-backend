from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.reports import get_admin_reports, close_admin_report


@admin_bp.route("/reports", methods=["GET"])
def admin_get_reports():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        status = request.args.get("status")

        if not status:
            return jsonify({"error": "status query parameter is required"}), 400

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


@admin_bp.route("/reports/<int:report_id>/close", methods=["PATCH"])
def admin_close_report(report_id):
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

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