from flask import request, jsonify, session
from . import coach_bp
from app.services.coach.update_certs import update_coach_certification


@coach_bp.route("/certifications/update", methods=["PATCH"])
def update_certification_route():
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

        cert_name = data.get("cert_name")
        provider = data.get("provider_name")
        description = data.get("description")
        expires_date = data.get("expires_date")

        if not cert_name or not provider:
            return jsonify({"error": "Certificate name and provider are required"}), 400

        update_coach_certification(
            coach_id=int(coach_id),
            cert_id=int(cert_id),
            cert_name=cert_name,
            provider=provider,
            description=description,
            expires_date=expires_date,
        )

        return jsonify({"message": "Certification updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
