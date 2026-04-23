from flask import request, jsonify, session
from . import coach_bp
from app.services.coach.delete_Certs import delete_coach_certification

@coach_bp.route("/certifications/delete", methods=["DELETE"])
def delete_certification_route():
    try:
        coach_id = session.get("user_id")
        if not coach_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        
        role = data.get("role")
        cert_id = data.get("cert_id")

        if role != "coach":
            return jsonify({"error": "Forbidden. Coach role required."}), 403
        
        if not cert_id:
            return jsonify({"error": "cert_id is required in the request body"}), 400

        delete_coach_certification(
            coach_id=int(coach_id),
            cert_id=int(cert_id)
        )

        return jsonify({"message": "Certification deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500