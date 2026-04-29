from flask import jsonify, session
from . import client_bp
from app.services.client.reports import get_my_reports


@client_bp.route("/reports/my", methods=["GET"])
def get_my_reports_route():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        reports = get_my_reports(int(user_id))

        return (
            jsonify(
                {
                    "message": "success",
                    "reports": reports,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
